#!/bin/bash
while true; do
  if ! pgrep -f "cloudflared tunnel" >/dev/null; then
    cd /tmp/moncao-poc
    ./cloudflared tunnel --url http://127.0.0.1:8097 --no-autoupdate --protocol http2 > tun.log 2>&1 &
    sleep 12
    grep -o "https://[a-z0-9-]*\.trycloudflare\.com" tun.log | head -1 > url.txt
  fi
  U=$(cat /tmp/moncao-poc/url.txt 2>/dev/null)
  [ -n "$U" ] && curl -s --max-time 15 -o /dev/null "$U/api/saude"
  sleep 45
done
