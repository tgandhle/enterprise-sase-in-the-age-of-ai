"""Prompt DLP lab: what a secure web gateway sees when staff use an AI assistant.

Run:  python3 prompt_dlp_lab.py

Standard library only. No real key is written in this file. Each run makes a
fake key in a fictional format, exk_live_ followed by 32 hex characters, and
plants it in six requests to a fictional AI assistant. Four gateway
configurations then decide each request. Nothing leaves the process.

The lab compares every verdict with the one it expects. It exits 1 and lists
the mismatches if any differs.
"""
import base64, json, re, secrets, sys

SCAN_LIMIT = 64 * 1024  # lab value: the largest body the scanner reads. Not a product default.
KEY_PATTERN = re.compile(r"exk_live_[0-9a-f]{32}")

AI_HOST = "chat.assistant.example"        # the sanctioned assistant, reached through a browser
PINNED_HOST = "desktop.assistant.example"  # its desktop app, which pins its certificate
BYPASS = {PINNED_HOST}                     # hosts the gateway passes without decrypting


class Gateway:
    """One configuration of the gateway's AI policy."""

    def __init__(self, name, inspect, decode, oversize):
        self.name = name
        self.inspect = inspect    # decrypt and look at the body, or only check the host
        self.decode = decode      # scan the content as the destination will read it, or the raw bytes
        self.oversize = oversize  # what happens to a body over SCAN_LIMIT: "skip" or "block"

    def decide(self, host, body):
        if host in BYPASS:
            return "allow: not inspected (bypass list)"
        if not self.inspect:
            return "allow: not inspected"
        if len(body) > SCAN_LIMIT:
            if self.oversize == "block":
                return "block: too large to scan"
            return "allow: too large to scan"
        if self.decode:
            try:
                content = "\n".join(texts_in(json.loads(body)))
            except ValueError:
                return "block: body could not be decoded"
        else:
            content = body.decode("utf-8", "replace")
        if KEY_PATTERN.search(content):
            return "block: secret found"
        return "allow: nothing found"


def texts_in(value):
    """Every string the assistant will read, with declared base64 files decoded."""
    if isinstance(value, dict):
        if value.get("type") == "file" and value.get("encoding") == "base64":
            yield base64.b64decode(value["data"]).decode("utf-8", "replace")
            return
        for item in value.values():
            yield from texts_in(item)
    elif isinstance(value, list):
        for item in value:
            yield from texts_in(item)
    elif isinstance(value, str):
        yield value


def prompt(*parts):
    """A request body in the fictional assistant's format."""
    content = [p if isinstance(p, dict) else {"type": "text", "text": p} for p in parts]
    return json.dumps({"messages": [{"role": "user", "content": content}]}).encode()


def escaped(text):
    """The same text with every character written as a JSON \\u escape."""
    return "".join("\\u%04x" % ord(c) for c in text)


def build_requests(key):
    """The six requests: (label, host, body). stack/prompt-dlp sends the same ones."""
    log_line = "2026-11-02T09:14:07Z payment retry failed, auth=" + key
    padding = "2026-11-02T09:13:00Z health check ok\n" * 2000  # about 74 KB of ordinary log text
    return [
        ("1. clean prompt", AI_HOST, prompt("Why would a payment retry fail twice?")),
        ("2. key pasted in the prompt", AI_HOST, prompt("Why did this fail? " + log_line)),
        ("3. key written as \\u escapes", AI_HOST,
         prompt("Why did this fail? PLACEHOLDER").replace(b"PLACEHOLDER", escaped(log_line).encode())),
        ("4. key in an attached file", AI_HOST,
         prompt("Summarise the attached log.",
                {"type": "file", "name": "retry.log", "encoding": "base64",
                 "data": base64.b64encode(log_line.encode()).decode()})),
        ("5. key after 74 KB of log", AI_HOST, prompt("Why did this fail?\n" + padding + log_line)),
        ("6. key sent from desktop app", PINNED_HOST, prompt("Why did this fail? " + log_line)),
    ]


def main():
    key = "exk_live_" + secrets.token_hex(16)
    requests = build_requests(key)

    gateways = [
        (Gateway("A. host allowlist only", inspect=False, decode=False, oversize="skip"),
         ["allow: not inspected"] * 5),
        (Gateway("B. inspect, scan raw bytes", inspect=True, decode=False, oversize="skip"),
         ["allow: nothing found", "block: secret found", "allow: nothing found",
          "allow: nothing found", "allow: too large to scan"]),
        (Gateway("C. inspect, scan decoded content", inspect=True, decode=True, oversize="skip"),
         ["allow: nothing found", "block: secret found", "block: secret found",
          "block: secret found", "allow: too large to scan"]),
        (Gateway("D. C, and block what it cannot scan", inspect=True, decode=True, oversize="block"),
         ["allow: nothing found", "block: secret found", "block: secret found",
          "block: secret found", "block: too large to scan"]),
    ]

    print("key: random, this run only")
    print(f"scan limit: {SCAN_LIMIT} bytes")

    results = []  # (label, expected, actual), compared at the end
    for gateway, expected in gateways:
        expected = expected + ["allow: not inspected (bypass list)"]
        print()
        print(gateway.name)
        for (label, host, body), want in zip(requests, expected):
            actual = gateway.decide(host, body)
            results.append((f"{gateway.name[:2]} {label}", want, actual))
            print(f"{label:<32} {actual}")

    # Nothing more is printed when every result is the expected one.
    failures = [r for r in results if r[2] != r[1]]
    if failures:
        print()
        print(f"{len(failures)} check(s) did not match the expected outcome:")
        for label, expected, actual in failures:
            print(f"  {label}: expected {expected}, got {actual}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
