# Packages
import argparse
import time

# Custom Classes
import httpc


REQUEST_DELAY = 0.5


def parse_flags():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", help="server host", default="localhost")
    parser.add_argument("--port", help="server port", type=int, default=8007)
    return parser.parse_args()


# Tests Entry Point
if __name__ == "__main__":
    flags = parse_flags()

    # Test simple GET
    print("=== SIMPLE GET ===")
    httpc.get(url="https://httpbin.org/status/418", verbose=True)

    time.sleep(REQUEST_DELAY)

    # Test GET with Query Params
    print("\r\n=== GET WITH QUERY PARAMS ===")
    httpc.get(url="https://httpbin.org/get?test=something&other=else", verbose=True)

    time.sleep(REQUEST_DELAY)

    # Test GET with Header
    print("\r\n=== GET WITH HEADER ===")
    header = {
        "Content-Type": "application/json",
        "User-Agent": "HTTPc/1.0"
    }
    httpc.get(url="https://httpbin.org/headers", header=header, verbose=True)

    time.sleep(REQUEST_DELAY)

    # Test POST with Body
    print("\r\n=== POST WITH BODY ===")
    header = {
        "Content-Type": "application/json",
        "Content-Length": 23
    }
    httpc.post(url="https://httpbin.org/post", header=header, body='{"test": ["something"]}', verbose=True)
