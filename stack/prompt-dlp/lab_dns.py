"""mitmproxy addon for this lab only: send both fake assistant names to the
local fake assistant, so the lab needs no change to the hosts file.

A real gateway resolves names with real DNS. Nothing here is part of the
policy being taught.
"""
from mitmproxy import proxy

ASSISTANT = ("127.0.0.1", 8443)
NAMES = {"chat.assistant.example", "desktop.assistant.example"}


def server_connect(data: proxy.server_hooks.ServerConnectionHookData) -> None:
    host = data.server.address[0] if data.server.address else None
    if host in NAMES:
        data.server.sni = data.server.sni or host
        data.server.address = ASSISTANT
