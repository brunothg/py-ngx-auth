import base64
import urllib.parse
from http.server import BaseHTTPRequestHandler
from typing import Callable
from functools import reduce
import authenticator
from authenticator import Authenticator


def parse_basic_auth_header(header: str) -> tuple[str, str, str]:
    parts = header.split()
    auth_type = parts[0].strip() if len(parts) > 0 else None
    cred_parts = base64.b64decode(parts[1]).decode('utf-8').split(':', 1) if len(parts) > 1 else None
    username = cred_parts[0].strip() if len(cred_parts) > 0 else None
    password = cred_parts[1].strip() if len(cred_parts) > 1 else None

    return auth_type, username, password


class NgxAuthRequestHandler(BaseHTTPRequestHandler):
    _success_code: int
    _error_code: int
    _realm: str
    _allow_anonymous: bool
    _allow_no_password: bool
    _authenticators: list[Authenticator]

    def __init__(
            self, request, client_address, server,
            success_code: int = None,
            error_code: int = None,
            realm: str = None,
            allow_anonymous: bool = None,
            allow_no_password: bool = None,
            authenticators: list[Authenticator] = None,
    ):
        self._success_code = success_code
        self._error_code = error_code
        self._realm = realm
        self._allow_anonymous = allow_anonymous
        self._allow_no_password = allow_no_password
        self._authenticators = authenticators or authenticator.get_authenticators()
        super().__init__(request, client_address, server)

    def _get_authenticator(self) -> list[Authenticator]:
        authenticators = [
            auth
            for auth in self._authenticators
            if auth.get_name() in (self.get_query_parameters().get('authenticator') or [])
        ]
        return authenticators or []

    def _get_allow_anonymous(self) -> bool:
        return (self._allow_anonymous
                or next(iter(self.get_query_parameters().get('allow_anonymous') or []), None)
                or False)

    def _get_allow_no_pwd(self) -> bool:
        return (self._allow_no_password
                or next(iter(self.get_query_parameters().get('allow_no_password') or []), None)
                or False)

    def _get_realm(self) -> str:
        return (self._realm
                or next(iter(self.get_query_parameters().get('realm') or []), None)
                or "Restricted Access")

    def _get_success_code(self) -> int:
        return (self._success_code
                or next(iter(self.get_query_parameters().get('success_code') or []), None)
                or 204)

    def _get_error_code(self) -> int:
        return (self._error_code
                or next(iter(self.get_query_parameters().get('error_code') or []), None)
                or self._get_auth_code())

    def _get_auth_code(self) -> int:
        return 401

    def _get_url_parts(self):
        return urllib.parse.urlparse(self.path, allow_fragments=False)

    def get_query_parameters(self) -> dict[str, list[str]]:
        return urllib.parse.parse_qs(self._get_url_parts().query)

    def get_query_path(self) -> str:
        return self._get_url_parts().path

    def authrorize_creds(self, username, password) -> bool:
        return reduce(
            lambda a, b: a or b,
            [
                auth.authenticate(username=username, password=password, parameters=self.get_query_parameters())
                for auth in self._get_authenticator()
            ],
            False
        )

    def send_head(self):
        req_auth_code: int = self._get_auth_code()
        req_error_code: int = self._get_error_code()

        req_result_code: int = self._get_success_code()

        auth_header: str = self.headers['Authorization']
        if auth_header is None:
            req_result_code = req_auth_code
        else:
            basic_auth_type, username, password = parse_basic_auth_header(auth_header)
            if not basic_auth_type or basic_auth_type.casefold() != 'Basic'.casefold():
                req_result_code = req_auth_code
            if not username and not self._get_allow_anonymous():
                req_result_code = req_error_code
            if not password and not self._get_allow_no_pwd():
                req_result_code = req_error_code
            if not self.authrorize_creds(username, password):
                req_result_code = req_error_code

        self.send_response(req_result_code)
        if req_result_code == req_auth_code:
            self.send_header('WWW-Authenticate', f'Basic realm="{self._get_realm()}"')
        self.end_headers()

    def do_HEAD(self):
        self.send_head()

    def do_GET(self):
        self.send_head()

    def do_POST(self):
        self.do_GET()


def make_ngx_auth_request_handler(
        success_code: int = None,
        error_code: int = None,
        realm: str = None,
        allow_anonymous: bool = None,
        allow_no_password: bool = None,
        authenticators: list[Authenticator] = None,
) -> Callable[[any, any, any], BaseHTTPRequestHandler]:
    return lambda request, client_address, server: NgxAuthRequestHandler(
        request, client_address, server,
        success_code=success_code,
        error_code=error_code,
        realm=realm,
        allow_anonymous=allow_anonymous,
        allow_no_password=allow_no_password,
        authenticators=authenticators,
    )
