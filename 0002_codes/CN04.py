"""
Task CN04 : http request simulator

Description: This task shows how a basic HTTP GET request looks in text form.
The program builds a simple request using the path and host you provide
and prints the final formatted request.

Concept explained: HTTP is a text-based protocol where the client sends a request line,
some headers, and then an empty line before the message body.
Understanding this structure helps you recognize how browsers communicate
with web servers.
"""

def build_http_get(host, path):
    # simple textual HTTP GET request
    request = (
        f"GET {path} HTTP/1.1\r\n"
        f"Host: {host}\r\n"
        f"User-Agent: CN04-Simulator\r\n"
        f"Accept: */*\r\n"
        f"\r\n"
    )
    return request


# program entry point
if __name__ == "__main__":
    host = "example.com"
    path = "/"

    http_request = build_http_get(host, path)

    print("Generated HTTP GET request:")
    print(http_request)
