#!/usr/bin/env python3

from http.server import ThreadingHTTPServer, HTTPServer

import click

import handler


@click.command()
@click.option('--port', '-p', 'port', default=8080, help='Port number')
@click.option('--ip', '-i', 'ip', default='127.0.0.1', help='IP address')
@click.option('--threaded/--blocking', 'threaded', default=True, help='Threaded or blocking mode')
def main(
        ip: str = '127.0.0.1',
        port: int = 8080,
        threaded: bool = False,
):
    server_class = ThreadingHTTPServer if threaded else HTTPServer
    server_address = (ip, port)

    print(f"Start {server_class.__name__} at: ", server_address)
    httpd = server_class(server_address, handler.make_ngx_auth_request_handler())
    httpd.serve_forever()


if __name__ == "__main__":
    main()
