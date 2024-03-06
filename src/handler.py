from http.server import BaseHTTPRequestHandler
import base64
from typing import Callable


def parse_basic_auth_header(header: str) -> tuple[str, str, str]:
    parts = header.split()
    auth_type = parts[0].strip() if len(parts) > 0 else None
    cred_parts = base64.b64decode(parts[1]).decode('utf-8').split(':', 1) if len(parts) > 1 else None
    username = cred_parts[0].strip() if len(cred_parts) > 0 else None
    password = cred_parts[1].strip() if len(cred_parts) > 1 else None

    return auth_type, username, password


def make_ngx_auth_request_handler(
        success_code: int = 204,
        error_code: int = 401,
) -> Callable[[any, any, any], BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):

        _success_code = success_code
        _auth_code = 401
        _error_code = error_code

        def authrorize_creds(self, username, password):
            # TODO authrorize_creds
            return username == password

        def send_head(self):
            result_code = self._success_code

            auth_header = self.headers['Authorization']
            if auth_header is None:
                result_code = self._auth_code
            else:
                basic_auth_type, username, password = parse_basic_auth_header()
                if not basic_auth_type or basic_auth_type.casefold() != 'Basic'.casefold():
                    result_code = self._auth_code
                if not username and not False:  # TODO is allow anonymous
                    result_code = self._error_code
                if not password and not False:  # TODO is allow no passwd
                    result_code = self._error_code
                if not self.authrorize_creds(username, password):
                    result_code = self._error_code

            self.send_response(result_code)
            if result_code == self._auth_code:
                self.send_header('WWW-Authenticate', 'Basic realm=""')  # TODO realm
            self.end_headers()

        def do_HEAD(self):
            self.send_head()

        def do_GET(self):
            self.send_head()

        def do_POST(self):
            self.do_GET()

    return Handler
