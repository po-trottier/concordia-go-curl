#############################################################################################
# Written by:
#   - Pierre-Olivier Trottier (40059235)
#   - Nimit Jaggi (40032159)
#############################################################################################

import argparse
import io
import json
import mimetypes
import os
import pprint
import re
import socket
import sys
from enum import Enum


#############################################################################################
# IMPORTANT NOTE:
# This script requires Python 3.10 to work due to use of match/case statements
#############################################################################################


#############################################################################################
# Library Implementation
#############################################################################################


class HttpVerb(Enum):
    GET = "GET"
    DELETE = "DELETE"
    POST = "POST"
    PUT = "PUT"


# Local connection
__LOCAL_HOSTNAME = "localhost"
__LOCAL_PORT = 1338
# Connection ports
__HTTP_PORT = 80
# Socket buffer size
__BUFFER_SIZE = 1024


def __parse_url(url):
    # From URI RFC: https://datatracker.ietf.org/doc/html/rfc3986#appendix-B
    result = re.search('^(([^:/?#]+):)?(//([^/?#]*))?([^?#]*)(\?([^#]*))?(#(.*))?', url)

    # When the port is in the URL
    host = result.group(4)
    port = __HTTP_PORT
    if ':' in host:
        connection = result.group(4).split(':')
        host = connection[0]
        port = int(connection[1])

    # Return the port here to allow for dynamic port selection based on the protocol later if we add SSL?
    return {
        "hostname": host,
        "path": result.group(5),
        "args": result.group(6),
        "port": port
    }


def __receive_data(sock):
    # Read the socket data byte by byte until we reach the end of the headers
    data, address = sock.recvfrom(__BUFFER_SIZE)

    body_index = 0
    headers_buffer = b''
    for byte in data:
        if b'\r\n\r\n' in headers_buffer:
            break
        headers_buffer += byte.to_bytes(1, sys.byteorder)
        body_index += 1

    # Get the request body
    body_buffer = b''
    if len(data) > body_index:
        body_buffer = data[body_index:]

    # Get a string from the header bytes without the empty lines
    header_data = headers_buffer[:-4].decode()

    # Ignore the HTTP Version and Request Status
    header_strings = header_data.splitlines()[1:]

    # Build a dictionary from the string
    header_dictionary = {}
    for string in header_strings:
        header = string.split(': ')
        header_dictionary[header[0]] = header[1]

    return headers_buffer, body_buffer


def __parse_response(headers, body):
    lines = headers.splitlines()

    # First line is always the status and status code
    full_status = re.search('HTTP/\d+\.?\d* (\d+) (.*)', lines[0])

    # Every line after that until the first empty line is a header
    header_dictionary = {}
    for index in range(1, len(lines)):
        # Found the empty line
        if not lines[index]:
            break
        header = lines[index].split(': ')
        header_dictionary[header[0]] = header[1]

    # Attempt to parse the string to a dict (Expect JSON)
    try:
        body_content = json.loads(body.decode())
    # If the string is a valid JSON string return is raw
    except ValueError as e:
        body_content = body

    return {
        "status_code": full_status.group(1),
        "status": full_status.group(2),
        "headers": header_dictionary,
        "body": body_content
    }


def __request(verb, url, header, body=None, file=None, verbose=False):
    # Make sure we're sending a valid request
    if not isinstance(verb, HttpVerb):
        print("Invalid verb requested", verb)
        sys.exit(1)

    if verbose:
        print(f"[INITIALIZE] {verb.value} Request: Initializing Socket")

    __socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        # Bind to the local hostname and port
        __socket.bind((__LOCAL_HOSTNAME, __LOCAL_PORT))

        if verbose:
            print(f"[PARSING] {verb.value} Parsing URL:", url)

        # Get the Host, Port, Path and Args
        parsed = __parse_url(url)

        if verbose:
            print(f"[SENDING] {verb.value} Request:", parsed)

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
        if body or file:
            if body:
                if isinstance(body, dict):
                    json_body = json.dumps(body)
                    content += f"Content-Length: {len(json_body)}\r\n\r\n"
                    content += json_body + "\r\n"
                else:
                    content += f"Content-Length: {len(body)}\r\n\r\n"
                    content += body + "\r\n"
            if file:
                if isinstance(file, io.BufferedReader):
                    file_type = mimetypes.guess_type(os.path.basename(file.name))[0]
                    file_content = file.read()
                    file.close()
                    content += f"Content-Length: {len(file_content)}\r\n"
                    content += f"Content-Type: {file_type}\r\n\r\n"
                    content += str(file_content) + "\r\n"
                else:
                    raise IOError('Invalid file requested')
        else:
            content += "\r\n"

        # Send the Request to the URI
        __socket.sendto(content.encode(), (parsed['hostname'], parsed['port']))

        if verbose:
            print(f"[SENT] {verb.value} Request:\r\n\r\n{content}")

        # Receive the Request Response
        headers_data, body_data = __receive_data(__socket)

        if verbose:
            print(f"[SUCCESS] {verb.value} Request: Response Received")

        if verbose:
            print(f"[PARSING] {verb.value} Request: Parsing Response Data")

        __socket.close()

        # Return the response data
        return __parse_response(headers_data.decode("utf-8"), body_data)

    except socket.error as error:
        print(f"[FAILED] {verb.value} Error:", error.strerror)
        sys.exit(1)

    finally:
        if file:
            file.close()
        __socket.close()


def get(url, header=None, verbose=False):
    return __request(HttpVerb.GET, url, header, None, None, verbose)


def delete(url, header=None, verbose=False):
    return __request(HttpVerb.DELETE, url, header, None, None, verbose)


def post(url, body=None, file=None, header=None, verbose=False):
    return __request(HttpVerb.POST, url, header, body, file, verbose)


def put(url, body=None, file=None, header=None, verbose=False):
    return __request(HttpVerb.PUT, url, header, body, file, verbose)


#############################################################################################
# CLI Tool Implementation
#############################################################################################


# Access a values by doing "args.host" or "args.port", etc.
def __parse_flags():
    parser = argparse.ArgumentParser(prog="httpc")
    subparsers = parser.add_subparsers(dest="verb", required=True, help="Verb to be used")

    get_parser = subparsers.add_parser(HttpVerb.GET.value, help="GET request")
    get_parser.add_argument("-V", "--verbose", help="Activate verbose mode", action="store_true")
    get_parser.add_argument("-H", "--headers", help="Headers to be sent using the following format: 'Key:Value'", action="append")
    get_parser.add_argument("url", help="URL to point to for the request")

    delete_parser = subparsers.add_parser(HttpVerb.DELETE.value, help="DELETE request")
    delete_parser.add_argument("-V", "--verbose", help="Activate verbose mode", action="store_true")
    delete_parser.add_argument("-H", "--headers", help="Headers to be sent using the following format: 'Key:Value'", action="append")
    delete_parser.add_argument("url", help="URL to point to for the request")

    post_parser = subparsers.add_parser(HttpVerb.POST.value, help="POST request")
    post_parser.add_argument("-V", "--verbose", help="Activate verbose mode", action="store_true")
    post_parser.add_argument("-H", "--headers", help="Headers to be sent using the following format: 'Key:Value'", action="append")
    post_data_group = post_parser.add_mutually_exclusive_group()
    post_data_group.add_argument("-D", "--inlinedata", help="Inline data to be sent in the request body")
    post_data_group.add_argument("-F", "--file", help="File to be sent in the request body", type=argparse.FileType('rb'))
    post_parser.add_argument("url", help="URL to point to for the request")

    put_parser = subparsers.add_parser(HttpVerb.PUT.value, help="PUT request")
    put_parser.add_argument("-V", "--verbose", help="Activate verbose mode", action="store_true")
    put_parser.add_argument("-H", "--headers", help="Headers to be sent using the following format: 'Key:Value'", action="append")
    put_data_group = put_parser.add_mutually_exclusive_group()
    put_data_group.add_argument("-D", "--inlinedata", help="Inline data to be sent in the request body")
    put_data_group.add_argument("-F", "--file", help="File to be sent in the request body", type=argparse.FileType('rb'))
    put_parser.add_argument("url", help="URL to point to for the request")

    args = parser.parse_args()

    # Validate header's format
    if args.headers:
        for header_arg in args.headers:
            if len(header_arg.split(':')) != 2:
                print("[FAILED] Invalid header format. Input headers using the following format: 'Key:Value'")
                sys.exit(1)

    return args


# Build dictionary from header strings if they were given
def __parse_headers(header_args):
    header_dictionary = None

    if header_args:
        header_dictionary = {}
        for string in header_args:
            header = string.split(':')
            header_dictionary[header[0]] = header[1]

    return header_dictionary


# CLI Entry Point
if __name__ == "__main__":
    flags = __parse_flags()
    header_content = __parse_headers(flags.headers)

    if flags.verbose:
        print(f"[ARGS] {flags.verb} Arguments: {flags}")

    # Send the request
    match flags.verb:
        case HttpVerb.GET.value:
            pprint.pprint(get(flags.url, header_content, flags.verbose))
        case HttpVerb.DELETE.value:
            pprint.pprint(delete(flags.url, header_content, flags.verbose))
        case HttpVerb.POST.value:
            pprint.pprint(post(flags.url, flags.inlinedata, flags.file, header_content, flags.verbose))
        case HttpVerb.PUT.value:
            pprint.pprint(put(flags.url, flags.inlinedata, flags.file, header_content, flags.verbose))
