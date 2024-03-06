import base64
import urllib.parse
from http.server import BaseHTTPRequestHandler
from typing import Callable


def parse_basic_auth_header(header: str) -> tuple[str, str, str]:
    parts = header.split()
    auth_type = parts[0].strip() if len(parts) > 0 else None
    cred_parts = base64.b64decode(parts[1]).decode('utf-8').split(':', 1) if len(parts) > 1 else None
    username = cred_parts[0].strip() if len(cred_parts) > 0 else None
    password = cred_parts[1].strip() if len(cred_parts) > 1 else None

    return auth_type, username, password


def make_ngx_auth_request_handler(
        success_code: int = None,
        error_code: int = None,
        realm: str = None,
        allow_anonymous: bool = None,
        allow_no_password: bool = None,
) -> Callable[[any, any, any], BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):

        def _get_allow_anonymous(self) -> bool:
            return allow_anonymous or self.get_query_parameters().get('allow_anonymous') or False

        def _get_allow_no_pwd(self) -> bool:
            return allow_no_password or self.get_query_parameters().get('allow_no_password') or False

        def _get_realm(self) -> str:
            return realm or self.get_query_parameters().get('realm') or "Restricted Access"

        def _get_success_code(self) -> int:
            return success_code or self.get_query_parameters().get('success_code') or 204

        def _get_error_code(self) -> int:
            return error_code or self.get_query_parameters().get('error_code') or self._get_auth_code()

        def _get_auth_code(self) -> int:
            return 401

        def _get_url_parts(self):
            return urllib.parse.urlparse(self.path, allow_fragments=False)

        def get_query_parameters(self) -> dict[str, list[str]]:
            return urllib.parse.parse_qs(self._get_url_parts().query)

        def get_query_path(self) -> str:
            return self._get_url_parts().path

        def authrorize_creds(self, username, password):
            # TODO authrorize_creds
            return username == password

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

    return Handler
