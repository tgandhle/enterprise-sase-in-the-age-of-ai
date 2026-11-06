#!/usr/bin/env bash
# Runs the lab's six requests through a real TLS-inspecting proxy.
# Needs: python3, openssl, curl, and mitmproxy (pip install mitmproxy).
# Everything runs on this machine and stops when the script ends.
set -euo pipefail
cd "$(dirname "$0")"
WORK=$(mktemp -d)
trap 'kill $(jobs -p) 2>/dev/null || true; rm -rf "$WORK"' EXIT

# The fake vendor's own CA and server certificate, for both names.
openssl req -x509 -newkey rsa:2048 -nodes -days 1 -subj "/CN=Fake assistant vendor CA" \
  -keyout "$WORK/vendor-ca.key" -out "$WORK/vendor-ca.pem" 2>/dev/null
openssl req -newkey rsa:2048 -nodes -subj "/CN=assistant.example" \
  -keyout "$WORK/server.key" -out "$WORK/server.csr" 2>/dev/null
printf "subjectAltName=DNS:chat.assistant.example,DNS:desktop.assistant.example\n" > "$WORK/san.ext"
openssl x509 -req -in "$WORK/server.csr" -CA "$WORK/vendor-ca.pem" -CAkey "$WORK/vendor-ca.key" \
  -CAcreateserial -days 1 -extfile "$WORK/san.ext" -out "$WORK/server.pem" 2>/dev/null

python3 make_bodies.py "$WORK/bodies" > /dev/null
python3 assistant.py "$WORK/server.pem" "$WORK/server.key" 8443 > "$WORK/assistant.log" 2>&1 &

# The gateway: inspects everything except the bypass list, trusts the vendor CA upstream.
# Its own CA is written to $WORK/mitm, and the browser client trusts only that one.
proxy() {  # port, extra options
  mitmdump --listen-port "$1" --set confdir="$WORK/mitm" \
    --set ssl_verify_upstream_trusted_ca="$WORK/vendor-ca.pem" \
    -s lab_dns.py -s addon.py "${@:2}" >> "$WORK/proxy-$1.log" 2>&1 &
}
proxy 8080 --ignore-hosts '^desktop\.assistant\.example:'   # bypass list: the desktop app
proxy 8081                                                  # same gateway, empty bypass list
for _ in $(seq 50); do [ -f "$WORK/mitm/mitmproxy-ca-cert.pem" ] && break; sleep 0.2; done
sleep 2

send() {  # label, port, body number, CA the client trusts
  local host code
  host=$(cat "$WORK/bodies/$3.host")
  code=$(curl -s -o "$WORK/out" -w "%{http_code}" --proxy "http://127.0.0.1:$2" --cacert "$4" \
    -H "Content-Type: application/json" --data-binary @"$WORK/bodies/$3.json" \
    "https://$host:8443/v1/chat" || true)
  [ "$code" = "000" ] && echo "$1  connection failed" || echo "$1  $code $(head -c 60 "$WORK/out")"
}

BROWSER_CA="$WORK/mitm/mitmproxy-ca-cert.pem"   # managed devices trust the gateway's CA
PINNED_CA="$WORK/vendor-ca.pem"                 # the desktop app trusts only its vendor
echo "Browser, through the gateway"
for i in 1 2 3 4 5; do send "  request $i" 8080 "$i" "$BROWSER_CA"; done
echo "Desktop app, on the bypass list"
send "  request 6" 8080 6 "$PINNED_CA"
echo "Desktop app, bypass list empty"
send "  request 6" 8081 6 "$PINNED_CA"
sleep 1
echo
echo "What the assistant received"
sed 's/^/  /' "$WORK/assistant.log" | grep -v listening
echo "What the gateway decided"
cat "$WORK"/proxy-*.log | grep -E "prompt-dlp|certificate|Client TLS handshake failed" | sed 's/^/  /' | cut -c1-150
