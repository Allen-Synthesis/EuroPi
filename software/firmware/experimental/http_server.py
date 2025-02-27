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

import json

try:
    import socket
except ImportError as err:
    raise Exception(f"Failed to load HTTP server dependencies: {err}")

from europi_log import *


class HttpStatus:
    """
    HTTP status codes to include in the header.

    This collection is not exhaustive, just what we need to handle this minimal server implementation
    """

    # 200 series - everything's fine
    OK = 200

    # 400 series - error is on the client end
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    REQUEST_TIMEOUT = 408
    TEAPOT = 418

    # 500 series - error is on the server end
    INTERNAL_SERVER_ERROR = 500
    NOT_IMPLEMENTED = 501

    # Human-readable names/descriptions of the error codes above
    # If you add another error code, make sure to add it here too!
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

    You should define a callback to handle incoming GET and/or POST requests, e.g.:

    server = HttpServer(port=8080)

    @server.get_handler
    def handle_http_get(request:str=None, connection:Socket=None):
        # process the request
        server.send_response(...)

    @server.post_handler
    def handle_http_post(request:str=None, connection:Socket=None):
        # process the request
        server.send_response(...)
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
            body {{
                font-family: Montserrat;
                text-align: center;
            }}
            h1 {{
                font-weight: normal;
                font-size: 2.5rem;
                letter-spacing: 1.75rem;
                padding-left: 1.75rem;
            }}
            h2 {{
                font-weight:  bold;
                font-size: 3.0rem;
            }}
            p {{
                font-weight: lighter;
                font-size: 2.0rem;
            }}
            .content-wrapper {{
                margin: 0;
                position: absolute;
                top: 50%;
                align-content: center;
                width: 100%;
                -ms-transform: translateY(-50%);
                transform: translateY(-50%);
            }}
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
        """
        Create a new HTTP server.

        This will open a socket on the specified port, allowing for clients to connect to us.
        Only HTTP is supported, not HTTPS. Basic GET/POST requests should work, but websockets
        and anything fancy likely won't.

        Port 80 is officially reserved for HTTP traffic, and can be used by default. Port 8080
        is also commonly used for HTTP traffic.

        If you're operating in WiFi Client mode you may be subject to the whims of whatever
        port filter/firewall your IT administrator has implemented, so some ports may not work/
        may not be available.

        Operating in WiFi AP mode should allow the use of any port you want.

        After creating the HTTP server, you should assign a handler function to process requests:

        ```python
            srv = HttpServer(8080)
            @srv.request_handler
            def handle_http_request(connection=None, request=None):
                # 1. process the request, take any necessary actions
                ...
                my_response = f"{...}"

                # 2. send the response back
                srv.send_response(
                    connection,
                    my_response,
                    HttpStatus.OK,
                    MimeTypes.HTML,
                )
        ```
        Response can be an HTTP page, plain text, or JSON/CSV/YAML/XML formatted data. See
        MimeTypes for supported types. The response should always be a string; if sending
        a dict as JSON data you'll need to stringify it before passing it to send_response.

        You may send your own error codes as desired:
        ```python
            def handle_http_request(connection=None, request=None):
                srv.send_error_page(
                    Exception("We're out of coffee!")
                    connection,
                    HttpStatus.TEAPOT,  # send error 418 "I'm a teapot"
                )
        ```

        Inside the program's main loop you should call srv.check_connections() to process any
        incoming requests:

        ```python
            def main(self):
                # ...
                while True:
                    # ...
                    srv.check_requests()
                    # ...
        ```

        @param port  The port to listen on
        """
        self.port = port
        self.get_callback = self.default_request_handler
        self.post_callback = self.default_request_handler

        self.socket = socket.socket()
        addr = socket.getaddrinfo("0.0.0.0", port)
        addr = addr[0][-1]
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.settimeout(0)
        self.socket.bind(addr)
        self.socket.listen(5)

    def default_request_handler(self, connection=None, request=None):
        """
        The default request handler for GET and POST requests the server.

        The intent is that whatever program is using the HTTP server will create their own callback
        to replace this function. So all we do is raise a NotImplementedError that's handled
        by self.check_requests() and will serve our HTTP 501 error page accordingly.

        @param connection  The socket the client connected on
        @param request  The client's request
        """
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

                # the request should look something like this
                #
                # GET / HTTP/1.1
                # Host: localhost:8080
                # User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0
                # Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
                # Accept-Language: en-US,en;q=0.5
                # Accept-Encoding: gzip, deflate, br, zstd
                # Connection: keep-alive
                # Upgrade-Insecure-Requests: 1
                # Sec-Fetch-Dest: document
                # Sec-Fetch-Mode: navigate
                # Sec-Fetch-Site: none
                # Sec-Fetch-User: ?1
                # Priority: u=0, i

                request = conn.recv(1024)
                request = request.decode("UTF-8")

                if request.startswith("GET"):
                    self.get_callback(request=request, connection=conn)
                elif request.startswith("POST"):
                    self.post_callback(request=request, connection=conn)
                else:
                    method = request.strip().split()[0]
                    self.send_error_page(
                        Exception(f"Unsupported HTTP method {method}"),
                        conn,
                        status=HttpStatus.BAD_REQUEST,
                        headers=None,
                    )
            except NotImplementedError as err:
                log_warning(f"{err}", "http_server")
                # send a 501 error page
                self.send_error_page(err, conn, HttpStatus.NOT_IMPLEMENTED)
            except OSError as err:
                return
            except Exception as err:
                log_warning(f"{err}", "http_server")
                # send a 500 error page
                self.send_error_page(err, conn, HttpStatus.INTERNAL_SERVER_ERROR)
            finally:
                if conn is not None:
                    conn.close()
                    conn = None

    def get_handler(self, func):
        """
        Decorator for the function to handle HTTP GET requests

        The provided function must accept the following keyword arguments:
        - request: str  The request the client sent
        - conn: socket  A socket connection to the client

        @param func  The function to handle the request.
        """

        def wrapper(*args, **kwargs):
            func(*args, **kwargs)

        self.get_callback = wrapper
        return wrapper

    def post_handler(self, func):
        """
        Decorator for the function to handle HTTP POST requests

        The provided function must accept the following keyword arguments:
        - request: str  The request the client sent
        - conn: socket  A socket connection to the client

        @param func  The function to handle the request.
        """

        def wrapper(*args, **kwargs):
            func(*args, **kwargs)

        self.post_callback = wrapper
        return wrapper

    def send_error_page(
        self,
        error,
        connection,
        status=HttpStatus.INTERNAL_SERVER_ERROR,
        headers=None,
    ):
        """
        Serve our customized HTTP error page

        @param error  The exception that caused the error
        @param connection  The socket to send the response over
        @param status  The error status to respond with
        @param headers  Optional additional headers
        """
        self.send_html(
            connection,
            self.ERROR_PAGE.format(
                errno=status,
                errname=HttpStatus.StatusText[status],
                message=str(error),
            ),
            status=status,
            headers=headers,
        )

    def send_json(self, connection, data, headers=None):
        """
        Send a JSON object to the client

        @param connection  The socket connection to the client
        @param data  A dict to be converted to a JSON object
        @param headers  Optional additional HTTP headers to include
        """
        self.send_response(
            connection,
            json.dumps(data),
            status=HttpStatus.OK,
            content_type=MimeTypes.JSON,
            headers=headers,
        )

    def send_html(self, connection, html_page, status=HttpStatus.OK, headers=None):
        """
        Send an HTML document to the client

        @param connection  The socket to send the data over
        @param html_page  A string containing the HTML document.
        @param status  The HTTP status to send the page with
        @param headers  Optional additional HTTP headers
        """
        self.send_response(
            connection, html_page, content_type=MimeTypes.HTML, status=status, headers=headers
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

        connection.send(f"{header}\r\n\r\n".encode("UTF-8"))
        connection.send(response.encode("UTF-8"))
