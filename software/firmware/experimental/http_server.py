# Copyright 2025 Allen Synthesis
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
A simple HTTP server for the Raspberry Pi Pico
"""

try:
    import socket
except ImportError as err:
    raise Exception(f"Failed to load HTTP server dependencies: {err}")


class HttpStatus:
    """
    HTTP status codes to include in the header.

    This collection is not exhaustive, just what we need to handle this minimal server implementation
    """

    OK = "200 OK"

    BAD_REQUEST = "400 Bad Request"
    FORBIDDEN = "403 Forbidden"
    NOT_FOUND = "404 Not Found"
    TEAPOT = "418 I'm a teapot"  # for fun & debugging!

    INTERNAL_SERVER_ERROR = "500 Internal Server Error"
    NOT_IMPLEMENTED = "501 Not Implemented"


class MimeTypes:
    """
    Common MIME types we can support with this HTTP server implementation
    """

    CSV = "text/csv"
    HTML = "text/html"
    JSON = "text/json"
    TEXT = "text/plain"
    XML = "text/xml"
    YAML = "text/yaml"


class HttpServer:
    """
    The main server instance

    You should define a callback to handle incoming requests, e.g.:

    server = HttpServer(port=8080)

    @server.request_handler
    def handle_http_request(request:str=None, conn:Socket=None):
        # process the request
        server.send_response()
    """

    # A basic error page template
    ERROR_PAGE = """<!DOCTYPE html>
<html>
  <head>
    <title>EuroPi Error: {title}</title>
  </head>
  <body>
    <h1>EuroPi Error</h1>
    <h2>{title}</h2>
    <p>{body}</p>
  </body>
</html>
"""

    def __init__(self, port=80):
        self.port = 80
        self.request_callback = self.default_request_handler

        if wifi_connection is None:
            raise WifiError("Unable to start HTTP server: no wifi connection")

        self.socket = socket.socket()
        addr = socket.getaddrinfo("0.0.0.0", port)[0][-1]
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.settimeout(0)
        self.socket.bind(addr)
        self.socket.listen()

    def default_request_handler(self, connection=None, request=None):
        raise NotImplementedError("No request handler set")

    def check_requests(self):
        """
        Poll the socket and process any incoming requests.

        This will invoke the request handler function if it has been defined

        This function should be called inside the main loop of the program
        """
        conn = None
        while True:
            try:
                conn, addr = self.socket.accept()

                request = conn.recv(2048)
                request = str(request)

                self.request_callback(request=request, connection=conn)
            except NotImplementedError as err:
                # send a 501 error page
                self.send_response(
                    conn,
                    self.ERROR_PAGE.format(
                        title=HttpStatus.NOT_IMPLEMENTED,
                        body=str(err),
                    ),
                    status=HttpStatus.NOT_IMPLEMENTED,
                    content_type=MimeTypes.HTML,
                )
            except OSError as err:
                return
            except BlockingIOError as err:
                return
            except TimeoutError as err:
                return
            except Exception as err:
                # send a 500 error page
                self.send_response(
                    conn,
                    self.ERROR_PAGE.format(
                        title=HttpStatus.INTERNAL_SERVER_ERROR,
                        body=str(err),
                    ),
                    status=HttpStatus.INTERNAL_SERVER_ERROR,
                    content_type=MimeTypes.HTML,
                )
            finally:
                if conn is not None:
                    conn.close()
                    conn = None

    def request_handler(self, func):
        """
        Decorator for the function to handle HTTP requests

        The provided function must accept the following keyword arguments:
        - request: str  The request the client sent
        - conn: socket  A socket connection to the client

        @param func  The function to handle the request.
        """

        def wrapper(*args, **kwargs):
            func(*args, **kwargs)

        self.request_callback = wrapper
        return wrapper

    def send_response(
        self,
        connection,
        response,
        status=HttpStatus.OK,
        content_type=MimeTypes.HTML,
    ):
        """
        Send a response to the client

        @param connection  The socket connection to the client
        @param response  The response payload
        @param content_type  The MIME type to include in the HTTP header
        """
        connection.send(f"HTTP/1.0 {status}\r\nContent-type: {content_type}\r\ncharset=utf-8\r\n\r\n".encode("UTF-8"))
        connection.send(response.encode("UTF-8"))
