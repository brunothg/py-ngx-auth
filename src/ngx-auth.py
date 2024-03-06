#!/usr/bin/env python3

from http.server import ThreadingHTTPServer, HTTPServer

import click

import handler


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
        **kwargs
):
    server_class = ThreadingHTTPServer if threaded else HTTPServer
    server_address = (ip, port)

    print(f"Start {server_class.__name__} at: ", server_address)
    httpd = server_class(server_address, handler.make_ngx_auth_request_handler(**kwargs))
    httpd.serve_forever()


if __name__ == "__main__":
    main()
