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

import europi
import experimental.wifi

try:
    import socket
except ImportError as err:
    raise Exception(f"Failed to load HTTP server dependencies: {err}")


class HttpStatus:
    """
    HTTP status codes to include in the header.

    This collection is not exhaustive, just what we need to handle this minimal server implementation
    """

    OK = 200

    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    REQUEST_TIMEOUT = 408
    TEAPOT = 418

    INTERNAL_SERVER_ERROR = 500
    NOT_IMPLEMENTED = 501

    StatusText = {
        OK: "OK",

        BAD_REQUEST: "Bad Request",
        UNAUTHORIZED: "Unauthorized",
        FORBIDDEN: "Forbidden",
        NOT_FOUND: "Not Found",
        REQUEST_TIMEOUT: "Request Timeout",
        TEAPOT: "I'm a teapot",

        INTERNAL_SERVER_ERROR: "Internal Server Error",
        NOT_IMPLEMENTED: "Not Implemented",
    }


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
    # Contains 3 parameters for the user to fill:
    # - errno: the error number (e.g. 404, 500)
    # - errname: the human-legible error name (e.g Not Found, Internal Server Error)
    # - message: free-form error message, stack trace, etc...
    ERROR_PAGE = """<!DOCTYPE html>
<!DOCTYPE html>
<html lang="en">
    <head>
        <style>
            body {
                font-family: Montserrat;
                text-align: center;
            }
            h1 {
                font-weight: normal;
                font-size: 2.5rem;
                letter-spacing: 1.75rem;
                padding-left: 1.75rem;
            }
            h2 {
                font-weight:  bold;
                font-size: 3.0rem;
            }
            p {
                font-weight: lighter;
                font-size: 2.0rem;
            }
            .content-wrapper {
                margin: 0;
                position: absolute;
                top: 50%;
                align-content: center;
                width: 100%;
                -ms-transform: translateY(-50%);
                transform: translateY(-50%);
            }
        </style>
        <title>EuroPi Error {errno}</title>
    </head>
    <body>
        <div class="content-wrapper"?>
            <h1>EuroPi</h1>
            <h2>{errno} {errname}</h2>
            <p>
                {message}
            </p>
        </div>
    </body>
</html>
"""

    def __init__(self, port=80):
        self.port = 80
        self.request_callback = self.default_request_handler

        if europi.wifi_connection is None:
            raise experimental.wifi.WifiError("Unable to start HTTP server: no wifi connection")

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

        The client socket is closed after we send our response
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
                self.send_error_page(err, conn, HttpStatus.NOT_IMPLEMENTED)
            except OSError as err:
                return
            except BlockingIOError as err:
                return
            except TimeoutError as err:
                return
            except Exception as err:
                # send a 500 error page
                self.send_error_page(err, conn, HttpStatus.INTERNAL_SERVER_ERROR)
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

    def send_error_page(
        self,
        error,
        connection,
        status=HttpStatus.INTERNAL_SERVER_ERROR,
    ):
        """
        Serve our customized HTTP error page

        @param error  The exception that caused the error
        @param connection  The socket to send the response over
        @param status  The error status to respond with
        """
        self.send_response(
            connection,
            self.ERROR_PAGE.format(
                errno=status,
                errname=HttpStatus.StatusText[status],
                message=str(error),
            ),
            status=status,
            content_type=MimeTypes.HTML,
        )

    def send_response(
        self,
        connection,
        response,
        status=HttpStatus.OK,
        content_type=MimeTypes.HTML,
        headers=None,
    ):
        """
        Send a response to the client

        @param connection  The socket connection to the client
        @param response  The response payload
        @param status  The HTTP status to respond with
        @param content_type  The MIME type to include in the HTTP header
        @param headers  Optional dict of key/value pairs for addtional HTTP headers. Charset is ALWAYS utf-8
        """
        header = f"HTTP/1.0 {status} {HttpStatus.StatusText[status]}\r\nContent-type: {content_type}\r\ncharset=utf-8"

        if headers is not None:
            for k in headers.keys():
                header = f"{header}\r\n{k}={headers[k]}"

        connection.send(
            f"{header}\r\n\r\n".encode(
                "UTF-8"
            )
        )
        connection.send(response.encode("UTF-8"))
