import json
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
__BUFFER_SIZE = 1


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


def __receive_data(sock):
    # Read the socket data byte by byte until we reach the end of the headers
    data = b''
    while b'\r\n\r\n' not in data:
        data += sock.recv(__BUFFER_SIZE)

    # Get a string from the header bytes without the empty lines
    header_data = data[:-4].decode()

    # Ignore the HTTP Version and Request Status
    header_strings = header_data.splitlines()[1:]

    # Build a dictionary from the string
    headers = {}
    for string in header_strings:
        header = string.split(': ')
        headers[header[0]] = header[1]

    # Create a dictionary from the headers
    content_length = int(headers.get('Content-Length'))

    if content_length:
        data += sock.recv(content_length)

    return data


def __parse_response(data):
    lines = data.splitlines()

    # First line is always the status and status code
    full_status = re.search('HTTP/\d+\.?\d* (\d+) (.*)', lines[0])

    # Every line after that until the first empty line is a header
    body_index = 0
    headers = {}
    for index in range(1, len(lines)):
        # Found the empty line
        if not lines[index]:
            # If the next line is also empty continue until we find the body
            if index + 1 < len(lines) and not lines[index + 1]:
                continue
            # We found the start of the body
            body_index = index + 1
            break
        header = lines[index].split(': ')
        headers[header[0]] = header[1]

    # Anything after the empty line is the body
    body = None
    if 0 < body_index < len(lines):
        # Re-join the body lines to a string
        body_string = '\r\n'.join(lines[body_index:len(lines)])
        # Attempt to parse the string to a dict (Expect JSON)
        try:
            body = json.loads(body_string)
        # If the string is a valid JSON string return is raw
        except ValueError:
            body = body_string

    return {
        "status_code": full_status.group(1),
        "status": full_status.group(2),
        "headers": headers,
        "body": body
    }


def __request(verb, url, header, body=None, verbose=False):
    # Make sure we're sending a valid request
    if not isinstance(verb, HttpVerb):
        print("Invalid verb requested", verb)
        sys.exit(1)

    if verbose:
        print(f"[INITIALIZE] {verb.value} Request: Initializing Socket")

    __socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        if verbose:
            print(f"[SENDING] {verb.value} Request:", url)

        # Get the Host, Port, Path and Args
        parsed = __parse_url(url)

        # Connect to the Host on the proper Port
        __socket.connect((parsed['hostname'], parsed['port']))

        # Make sure the path is valid
        path = parsed['path'] if parsed['path'] else '/'
        args = parsed['args'] if parsed['args'] else ''

        # Build a URI from all the parts
        content = f"{verb.value} {path}{args} HTTP/1.1\r\nHost: {parsed['hostname']}\r\n"

        # If the headers are given add them after the hose
        if header:
            # If the headers are a dictionary add them nicely
            if isinstance(header, dict):
                for key in header:
                    content += f"{key}: {header[key]}\r\n"
            # If we don't recognize the format just dump everything
            else:
                content += header

        # If the request body is given calculate the content-length
        # automatically and add the body after an empty line
        if body:
            if isinstance(body, dict):
                json_body = json.dumps(body)
                content += f"Content-Length: {len(json_body)}\r\n\r\n"
                content += json_body + "\r\n"
            else:
                content += f"Content-Length: {len(body)}\r\n\r\n"
                content += body + "\r\n"
        else:
            content += "\r\n"

        # Send the Request to the URI
        __socket.sendall(content.encode())

        if verbose:
            print(f"[SENT] {verb.value} Request:\r\n\r\n{content}")

        # Receive the Request Response
        data = __receive_data(__socket)

        if verbose:
            print(f"[SUCCESS] {verb.value} Request: Response Received")

        __socket.close()

        if verbose:
            print(f"[PARSING] {verb.value} Request: Parsing Response Data")

        # Return the response data
        return __parse_response(data.decode("utf-8"))

    except socket.error as error:
        print(f"[FAILED] {verb.value} Request:", os.strerror(error.errno))
        sys.exit(1)

    finally:
        __socket.close()


def get(url, header=None, verbose=False):
    return __request(HttpVerb.GET, url, header, None, verbose)


def delete(url, header=None, verbose=False):
    return __request(HttpVerb.DELETE, url, header, None, verbose)


def post(url, body=None, header=None, verbose=False):
    return __request(HttpVerb.POST, url, header, body, verbose)


def put(url, body=None, header=None, verbose=False):
    return __request(HttpVerb.PUT, url, header, body, verbose)
