"""A fake AI assistant: an HTTPS server that answers every POST with 200.

It plays both chat.assistant.example and desktop.assistant.example, with one
certificate for both names. It decodes each body the way the lab's
configuration C does and logs whether the fake key reached it, which is the
question the stack answers.
"""
import http.server
import json
import pathlib
import ssl
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "labs"))
import prompt_dlp_lab as lab  # noqa: E402


class Handler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        body = self.rfile.read(int(self.headers.get("Content-Length", 0)))
        # Read the body the way the assistant would: decoded, attachments included.
        text = "\n".join(lab.texts_in(json.loads(body)))
        reached = "KEY REACHED THE ASSISTANT" if lab.KEY_PATTERN.search(text) else "no key"
        print(f"assistant {self.headers.get('Host')}: {len(body)} bytes, {reached}", flush=True)
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"assistant: 200 ok\n")

    def log_message(self, *args):
        pass


class Server(http.server.ThreadingHTTPServer):
    # The gateway opens a connection to the assistant before it decides, and
    # closes it unused when it blocks. That is not an error worth printing.
    def handle_error(self, request, client_address):
        if not isinstance(sys.exc_info()[1], (BrokenPipeError, ConnectionResetError, ssl.SSLError)):
            super().handle_error(request, client_address)


def main():
    cert, key, port = sys.argv[1], sys.argv[2], int(sys.argv[3])
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.load_cert_chain(cert, key)
    server = Server(("0.0.0.0", port), Handler)
    server.socket = ctx.wrap_socket(server.socket, server_side=True)
    print(f"assistant listening on {port}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
