#!/usr/bin/env python3

from http.server import ThreadingHTTPServer, HTTPServer

import click

import authenticator
import handler
from authenticator import Authenticator


@click.command()
@click.option('--port', '-p', 'port', default=8080, help='Port number')
@click.option('--ip', '-i', 'ip', default='0.0.0.0', help='IP address')
@click.option('--threaded/--blocking', 'threaded', default=True, help='Threaded or blocking mode')
@click.option('--success_code', 'success_code', default=None, type=int, help='Fixed success code')
@click.option('--error_code', 'error_code', default=None, type=int, help='Fixed error code')
@click.option('--realm', 'realm', default=None, type=str, help='Fixed realm')
@click.option('--allow_anonymous', 'allow_anonymous', default=None, type=bool, help='Fixed allow anonymous')
@click.option('--allow_no_password', 'allow_no_password', default=None, type=bool, help='Fixed allow no password')
def main(
        ip: str = '0.0.0.0',
        port: int = 8080,
        threaded: bool = False,
        success_code: int = None,
        error_code: int = None,
        realm: str = None,
        allow_anonymous: bool = None,
        allow_no_password: bool = None,
        authenticator_names: list[str] = None,
):
    server_class = ThreadingHTTPServer if threaded else HTTPServer
    server_address = (ip, port)
    authenticators = None if authenticator_names is None else [
        auth
        for auth in authenticator.get_authenticators()
        if auth.get_name() in authenticator_names
    ]

    print(f"Start {server_class.__name__} at: ", server_address)
    httpd = server_class(server_address, handler.make_ngx_auth_request_handler(
        success_code=success_code,
        error_code=error_code,
        realm=realm,
        allow_anonymous=allow_anonymous,
        allow_no_password=allow_no_password,
        authenticators=authenticators,
    ))
    httpd.serve_forever()


if __name__ == "__main__":
    main()
