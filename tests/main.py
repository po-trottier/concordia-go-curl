# Packages
import pprint
import time

# Custom Class
import httpc_tcp
import httpc_udp


# Constants
REQUEST_DELAY = 1
VERBOSE = False


def run_tests(client):
    # Test simple GET
    print("=== SIMPLE GET ===")
    pprint.pprint(client.get(url="https://httpbin.org/status/418", verbose=VERBOSE))

    time.sleep(REQUEST_DELAY)

    # Test GET with Query Params
    print("\r\n=== GET WITH QUERY PARAMS ===")
    pprint.pprint(client.get(url="https://httpbin.org/get?test=something&other=else", verbose=VERBOSE))

    time.sleep(REQUEST_DELAY)

    # Test GET with Header
    print("\r\n=== GET WITH HEADER ===")
    header = {
        "Content-Type": "application/json",
        "User-Agent": "httpc_tcp/1.0"
    }
    pprint.pprint(client.get(url="https://httpbin.org/headers", header=header, verbose=VERBOSE))

    time.sleep(REQUEST_DELAY)

    # Test POST with Body
    print("\r\n=== POST WITH BODY ===")
    header = {"Content-Type": "application/json"}
    body = {"test": ["something"]}
    pprint.pprint(client.post(url="https://httpbin.org/post", header=header, body=body, verbose=VERBOSE))

    # Test PUT with Body
    print("\r\n=== PUT WITH BODY ===")
    header = {"Content-Type": "application/json"}
    body = {"test": ["something"]}
    pprint.pprint(client.put(url="https://httpbin.org/put", header=header, body=body, verbose=VERBOSE))

    # Test simple DELETE
    print("\r\n=== SIMPLE DELETE ===")
    pprint.pprint(client.delete(url="https://httpbin.org/delete?test=true", verbose=VERBOSE))


# Tests Entry Point
if __name__ == "__main__":
    # TCP
    print("====== TCP ======")
    run_tests(httpc_tcp)

    time.sleep(REQUEST_DELAY)

    # UDP
    print("====== UDP ======")
    run_tests(httpc_udp)
