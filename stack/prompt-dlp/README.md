# Real-stack lab: prompt DLP through a TLS-inspecting proxy

Optional. The lesson's own lab, `labs/prompt_dlp_lab.py`, teaches the policy and needs Python alone. This one sends the same six requests over real HTTPS, through a real proxy that decrypts them, to a fake AI assistant. It shows two things the Python lab can only describe: the gateway really does read the encrypted body, and an app that pins its certificate really does stop connecting when you take it off the bypass list.

This lab is not checked by the site's tools or by CI. The output below is from one run on Linux on 2026-11-05.

## What runs

| File | Role |
|---|---|
| `assistant.py` | The fake assistant: an HTTPS server for `chat.assistant.example` and `desktop.assistant.example`, with its own certificate authority. It decodes each body the way the lesson's configuration C does and logs whether the key reached it. |
| `addon.py` | A mitmproxy addon that applies configuration D from the lesson. It imports `Gateway` from `labs/prompt_dlp_lab.py`, so the proxy and the lab make the same decision. |
| `lab_dns.py` | A mitmproxy addon for this lab only. It sends both fake names to the fake assistant on this machine, so you do not have to edit your hosts file. |
| `make_bodies.py` | Writes the lesson's six request bodies, with one fake key for this run. |
| `run.sh` | Makes the certificates, starts the assistant and two proxies, sends the requests with `curl`, and prints what each side saw. Everything stops when the script ends. |

Two proxies run. The one on port 8080 has the desktop app on its bypass list (`--ignore-hosts`). The one on port 8081 has an empty bypass list. The browser client trusts only the proxy's certificate authority, as a managed device does. The desktop client trusts only the vendor's, which is what pinning means for this lab.

## Run it

Needs `python3`, `openssl`, `curl` and mitmproxy. The script was run with mitmproxy 12.3.1 and Python 3.13. On Windows, run it inside WSL.

```
python3 -m venv .venv
source .venv/bin/activate
python -m pip install mitmproxy==12.3.1
./stack/prompt-dlp/run.sh
```

## Output

```
Browser, through the gateway
  request 1  200 assistant: 200 ok
  request 2  403 block: secret found
  request 3  403 block: secret found
  request 4  403 block: secret found
  request 5  403 block: too large to scan
Desktop app, on the bypass list
  request 6  200 assistant: 200 ok
Desktop app, bypass list empty
  request 6  connection failed

What the assistant received
  assistant chat.assistant.example:8443: 112 bytes, no key
  assistant desktop.assistant.example:8443: 183 bytes, KEY REACHED THE ASSISTANT
What the gateway decided
  prompt-dlp chat.assistant.example 112 bytes: allow: nothing found
  prompt-dlp chat.assistant.example 183 bytes: block: secret found
  prompt-dlp chat.assistant.example 628 bytes: block: secret found
  prompt-dlp chat.assistant.example 295 bytes: block: secret found
  prompt-dlp chat.assistant.example 76184 bytes: block: too large to scan
  [00:57:27.299][127.0.0.1:55652] Client TLS handshake failed. The client does not trust the proxy's certificate for desktop.assistant.example (tlsv1
```

The timestamp, port and the end of the last line will differ on your run. Read it against the lesson:

- Requests 1 to 5 match configuration D in the lesson's transcript. The proxy read every one of them, including the 628-byte body where the key is written as `\u` escapes.
- Request 6 on the bypass list reached the assistant with the key in it. The proxy never logged it, because it never saw inside it.
- Request 6 with an empty bypass list did not get inspected. It failed: the client refused the proxy's certificate. That is the decision the lesson's exercise 3 and check `dlp-04` are about.

## Try next

Both of these were run on 2026-11-05 with the results described.

- In `addon.py`, change `oversize="block"` to `oversize="skip"` and run again. Request 5 returns 200, and the assistant logs that a 76184-byte body reached it with the key in it.
- In `run.sh`, change `"$PINNED_CA"` to `"$BROWSER_CA"` in the last `send` line, the one that uses port 8081. This is what an unpinned app on a managed device looks like: request 6 through the proxy with the empty bypass list returns `403 block: secret found`.
