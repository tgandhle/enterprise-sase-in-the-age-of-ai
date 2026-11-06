"""mitmproxy addon: the lab's configuration D, applied to real HTTPS traffic.

The policy is not rewritten here. This file imports Gateway from
labs/prompt_dlp_lab.py, so the proxy and the lab make the same decision.
Hosts on the bypass list never reach this addon: mitmproxy's ignore_hosts
option passes them through still encrypted, as a real gateway's bypass does.
"""
import pathlib
import sys

from mitmproxy import http

LABS = pathlib.Path(__file__).resolve().parents[2] / "labs"
sys.path.insert(0, str(LABS))
import prompt_dlp_lab as lab  # noqa: E402

GATEWAY = lab.Gateway("D", inspect=True, decode=True, oversize="block")
AI_HOSTS = {lab.AI_HOST, lab.PINNED_HOST}
# The bypass list is enforced by mitmproxy's ignore_hosts option, so traffic
# that reaches this addon was not bypassed. Empty the lab's own list to match.
lab.BYPASS = set()


def request(flow: http.HTTPFlow) -> None:
    host = flow.request.pretty_host
    if host not in AI_HOSTS:
        return
    verdict = GATEWAY.decide(host, flow.request.get_content() or b"")
    print(f"prompt-dlp {host} {len(flow.request.raw_content or b'')} bytes: {verdict}", flush=True)
    if verdict.startswith("block"):
        flow.response = http.Response.make(
            403, (verdict + "\n").encode(), {"Content-Type": "text/plain"})
