import os
import re
import socket
import sys
from enum import Enum


class HttpVerb(Enum):
    GET = "GET"
    DELETE = "DELETE"
    POST = "POST"
    PUT = "PUT"


# Connection ports
__HTTP_PORT = 80
# Socket buffer size
__BUFFER_SIZE = 1024


def __parse_url(url):
    # From Uniform Resource Identifier RFC
    # https://www.rfc-editor.org/rfc/rfc3986#appendix-B
    result = re.search('^(([^:/?#]+):)?(//([^/?#]*))?([^?#]*)(\?([^#]*))?(#(.*))?', url)
    # Return the port here to allow for dynamic port selection based on the protocol later?
    return {
        "hostname": result.group(4),
        "path": result.group(5),
        "args": result.group(6),
        "port": __HTTP_PORT
    }


def __request(verb, url, header, body=None, verbose=False):
    # Make sure we're sending a valid request
    if not isinstance(verb, HttpVerb):
        print("Invalid verb requested", verb)
        sys.exit(1)
    if verbose:
        print(f"[INITIALIZE] {verb.value} Request: Initializing Socket")
    __socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if verbose:
        print(f"[SENDING] {verb.value} Request:", url)
    try:
        # Get the Host, Port, Path and Args
        parsed = __parse_url(url)
        # Connect to the Host on the proper Port
        __socket.connect((parsed['hostname'], parsed['port']))
        # Make sure the path is valid
        path = parsed['path'] if parsed['path'] else '/'
        args = parsed['args'] if parsed['args'] else ''
        # Build a URI from all the parts
        uri = f"{verb.value} {path}{args} HTTP/1.1\r\nHost: {parsed['hostname']}\r\n"
        # If the headers are given add them after the hose
        if header:
            for key in header:
                uri += f"{key}: {header[key]}\r\n"
        uri += "\r\n"
        # If the request body is given add it after an empty line
        if body:
            uri += body + "\r\n"
        # Send the Request to the URI
        __socket.sendall(uri.encode())
        if verbose:
            print(f"[SENT] {verb.value} Request:\r\n\r\n{uri}")
        # Receive the Request Response
        # TODO Make sure we get the whole response
        data = __socket.recv(__BUFFER_SIZE)
        if verbose:
            print(f"[SUCCESS] {verb.value} Request: Response Received")
        # Return the response data
        return data.decode("utf-8")
    except socket.error as error:
        print(f"[FAILED] {verb.value} Request:", os.strerror(error.errno))
        sys.exit(1)
    finally:
        __socket.close()


def get(url, header=None, verbose=False):
    response = __request(HttpVerb.GET, url, header, None, verbose)
    print(response)


def delete(url, header=None, verbose=False):
    response = __request(HttpVerb.DELETE, url, header, None, verbose)
    print(response)


def post(url, body=None, header=None, verbose=False):
    response = __request(HttpVerb.POST, url, header, body, verbose)
    print(response)


def put(url, body=None, header=None, verbose=False):
    response = __request(HttpVerb.PUT, url, header, body, verbose)
    print(response)
