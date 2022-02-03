# Packages
import pprint
import time

# Custom Class
import httpc

# Constants
REQUEST_DELAY = 1
VERBOSE = False

# Use this code to read the CLI flags
# Access a values by doing "args.host" or "args.port", etc.
# def parse_flags():
#     parser = argparse.ArgumentParser()
#     parser.add_argument("--host", help="server host", default="localhost")
#     parser.add_argument("--port", help="server port", type=int, default=8007)
#     return parser.parse_args()


# Tests Entry Point
if __name__ == "__main__":
    # Test simple GET
    print("=== SIMPLE GET ===")
    pprint.pprint(httpc.get(url="https://httpbin.org/status/418", verbose=VERBOSE))

    time.sleep(REQUEST_DELAY)

    # Test GET with Query Params
    print("\r\n=== GET WITH QUERY PARAMS ===")
    pprint.pprint(httpc.get(url="https://httpbin.org/get?test=something&other=else", verbose=VERBOSE))

    time.sleep(REQUEST_DELAY)

    # Test GET with Header
    print("\r\n=== GET WITH HEADER ===")
    header = {
        "Content-Type": "application/json",
        "User-Agent": "HTTPc/1.0"
    }
    pprint.pprint(httpc.get(url="https://httpbin.org/headers", header=header, verbose=VERBOSE))

    time.sleep(REQUEST_DELAY)

    # Test POST with Body
    print("\r\n=== POST WITH BODY ===")
    header = {
        "Content-Type": "application/json"
    }
    pprint.pprint(httpc.post(url="https://httpbin.org/post", header=header, body='{"test": ["something"]}', verbose=VERBOSE))

    # Test PUT with Body
    print("\r\n=== PUT WITH BODY ===")
    header = {
        "Content-Type": "application/json"
    }
    pprint.pprint(httpc.put(url="https://httpbin.org/put", header=header, body='{"test": ["something"]}', verbose=VERBOSE))

    # Test simple DELETE
    print("\r\n=== SIMPLE DELETE ===")
    pprint.pprint(httpc.delete(url="https://httpbin.org/delete?test=true", verbose=VERBOSE))
