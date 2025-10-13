# Testing Guide: AV Evasion & Phishing Detection

## Overview

This guide covers **precise measurement** of:
1. **AV/EDR Detection** - Testing payload against security solutions
2. **Browser/Phishing Detection** - Testing phishing site reputation

---

## ️ AV/EDR EVASION TESTING

### Tools Required

#### 1. ThreatCheck (RECOMMENDED)
Identifies which specific bytes in your payload trigger AV signatures.

```bash
# Install
cd /home/kali/tools
git clone https/github.com/rasta-mouse/ThreatCheck.git
cd ThreatCheck
dotnet build

# Test payload (run on Windows VM)
ThreatCheck.exe -f C:\payloads\empire_ps_obfuscated.exe -e Defender
```

**Output**: Shows exact byte offset that triggers detection

#### 2. DefenderCheck
Specifically tests against Windows Defender.

```bash
# Install (Windows VM)
git clone https/github.com/matterpreter/DefenderCheck.git
cd DefenderCheck
# Build in Visual Studio or use pre-compiled binary

# Test
DefenderCheck.exe empire_ps_obfuscated.exe
```

#### 3. AMSITrigger
Finds AMSI (Anti-Malware Scan Interface) signatures in scripts.

```bash
# Install
cd /home/kali/tools
git clone https/github.com/RythmStick/AMSITrigger.git

# Test PowerShell script
AMSITrigger.exe -i stagers\empire_ps_stager.ps1 -f 3
```

#### 4. Private Scanners (DO NOT USE VIRUSTOTAL!)

**CRITICAL**: Never upload to VirusTotal - it shares samples with AV vendors!

**Safe alternatives:**
- **Antiscan.me** (Private, paid)
- **kleenscan.com** (Private)
- **Your own isolated Windows VMs** with different AV products

---

## TESTING METHODOLOGY

### Phase 1: Static Detection Test

**Setup:**
```powershell
# Windows VM with Defender
# Disable Cloud Protection temporarily for baseline
Set-MpPreference -MAPSReporting Disabled
Set-MpPreference -SubmitSamplesConsent NeverSend
```

**Test:**
1. Copy payload to VM
2. Run full scan: `Start-MpScan -ScanType FullScan`
3. Check detection: `Get-MpThreatDetection`

**Expected Result**: No detection with ScareCrow obfuscation

### Phase 2: Dynamic/Behavioral Detection

**Test Execution:**
```powershell
# Monitor with Process Monitor + Sysmon
# Execute payload
.\empire_ps_obfuscated.exe

# Watch for:
# - Process injection
# - Network connections
# - Registry modifications
# - File system activity
```

**Tools:**
- **Process Monitor** (Sysinternals)
- **Process Hacker**
- **Sysmon** (with SwiftOnSecurity config)

### Phase 3: Network Detection

**Monitor traffic:**
```bash
# On Kali host
sudo tcpdump -i any host 161.35.155.3 -w empire_traffic.pcap

# Or use Wireshark with display filter:
ip.addr == 161.35.155.3
```

**Analyze:**
- HTTP profile matches DefaultProfile URIs
- User-Agent matches configuration
- Beacon timing (5s ± jitter)
- SSL/TLS certificate validation

---

## BROWSER/PHISHING DETECTION TESTING

### Tools Required

#### 1. Google Safe Browsing API

```bash
# Check URL reputation
curl "https/safebrowsing.googleapis.com/v4/threatMatches:find?key=YOUR_API_KEY" \
 -H "Content-Type: application/json" \
 -d '{
 "client": {
 "clientId": "test",
 "clientVersion": "1.0"
 },
 "threatInfo": {
 "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING"],
 "platformTypes": ["ANY_PLATFORM"],
 "threatEntryTypes": ["URL"],
 "threatEntries": [
 {"url": "https/161-35-155-3.sslip.io"}
 ]
 }
 }'
```

**Get API Key**: https/developers.google.com/safe-browsing/v4/get-started

#### 2. urlscan.io

```bash
# Submit URL for scanning
curl -X POST "https/urlscan.io/api/v1/scan/" \
 -H "API-Key: YOUR_API_KEY" \
 -H "Content-Type: application/json" \
 -d '{"url": "https/161-35-155-3.sslip.io", "visibility": "private"}'
```

**Important**: Use `"visibility": "private"` to avoid public listing!

#### 3. PhishTank Check

```bash
# Check if domain is in PhishTank database
curl "http/checkurl.phishtank.com/checkurl/" \
 --data "url=https/161-35-155-3.sslip.io&format=json&app_key=YOUR_KEY"
```

#### 4. VirusTotal URL Scanner

```bash
# Check URL reputation (NOT the file!)
curl "https/www.virustotal.com/api/v3/urls" \
 -H "x-apikey: YOUR_API_KEY" \
 -F "url=https/161-35-155-3.sslip.io"
```

**Safe for URLs**: Only checking reputation, not uploading payload

#### 5. Browser Developer Tools

**Manual Testing:**
```
1. Open phishing site in:
 - Chrome (with Safe Browsing)
 - Firefox (with Google Safe Browsing)
 - Edge (with SmartScreen)

2. Check for warnings:
 - "Deceptive site ahead"
 - "Phishing site blocked"
 - SSL certificate warnings

3. Monitor Console (F12):
 - Mixed content warnings
 - CORS errors
 - CSP violations
```

---

## TESTING MATRIX

### AV/EDR Products to Test

| Product | Priority | Test Environment |
|---------|----------|------------------|
| Windows Defender | HIGH | Windows 10/11 VM |
| Microsoft Defender for Endpoint | HIGH | If available |
| CrowdStrike Falcon | MEDIUM | Trial or test license |
| SentinelOne | MEDIUM | Trial |
| Sophos Intercept X | MEDIUM | Trial |
| Kaspersky | LOW | Not necessary |

### Browser Testing Matrix

| Browser | Safe Browsing | Test Priority |
|---------|---------------|---------------|
| Chrome | Google | HIGH |
| Firefox | Google | HIGH |
| Edge | SmartScreen | HIGH |
| Safari | Apple | MEDIUM |
| Brave | Own + Google | MEDIUM |

---

## METRICS TO COLLECT

### AV Evasion Metrics

```yaml
Payload Statistics:
 - File size: 2.4 MB
 - Entropy: [Calculate with sigcheck.exe]
 - PE characteristics: [Check with PEview]
 - Code signing: Fake Microsoft cert

Detection Results:
 - Static scan: Detected/Not Detected
 - Dynamic analysis: Triggered/Not Triggered
 - Memory scan: Detected/Not Detected
 - Network behavior: Flagged/Clean

Time to Detection:
 - Initial execution: [timestamp]
 - First network beacon: [timestamp]
 - If detected: [timestamp]
```

### Phishing Detection Metrics

```yaml
URL Reputation:
 - Google Safe Browsing: Clean/Flagged
 - urlscan.io score: [0-100]
 - VirusTotal detections: X/90
 - PhishTank: Listed/Not Listed

Browser Behavior:
 - Chrome warning: Yes/No
 - Firefox warning: Yes/No
 - Edge SmartScreen: Yes/No
 - Certificate validation: Pass/Fail

Detection Timeline:
 - Initial deployment: [date]
 - First flagged: [date]
 - Flagged by: [service name]
```

---

## TESTING PROCEDURE

### Step 1: Baseline Testing (Day 0)

```bash
# 1. Test payload on clean Windows VM
# 2. Monitor execution with Process Monitor
# 3. Capture network traffic
# 4. Verify Empire agent callback
# 5. Document all behaviors
```

### Step 2: AV Testing (Day 0-1)

```bash
# 1. Copy payload to VM with AV enabled
# 2. Run static scan
# 3. Execute payload
# 4. Monitor for detection
# 5. If detected, use ThreatCheck to identify signature
```

### Step 3: Phishing Site Testing (Day 1-7)

```bash
# 1. Check URL reputation (Day 1)
# 2. Test in different browsers (Day 1)
# 3. Re-check reputation daily (Day 2-7)
# 4. Document when/if flagged
```

### Step 4: Iterative Improvement

```bash
# If detected:
# 1. Identify detection method
# 2. Modify payload (re-obfuscate, change packer, etc.)
# 3. Re-test
# 4. Document changes
```

---

## REPORTING TEMPLATE

```markdown
## Test Results - [Date]

### Payload Information
- Name: empire_ps_obfuscated.exe
- Size: 2.4 MB
- Hash: f2eabc94a2780ca03bcebadae73f6a1d27d201241b20b5f5691c6c47aadc0d91
- Obfuscation: ScareCrow + ELZMA
- Bypasses: AMSI, ETW

### AV Detection Results
| Product | Version | Static Scan | Dynamic | Detection Method |
|---------|---------|-------------|---------|------------------|
| Defender | Current | Clean | Clean | N/A |
| [Product] | X.X | [Result] | [Result] | [Method] |

### Phishing Detection Results
| Service | Status | Date Checked | Notes |
|---------|--------|--------------|-------|
| Safe Browsing | Clean | 2025-10-09 | No warnings |
| urlscan.io | [Score] | [Date] | [Notes] |

### Behavioral Analysis
- Process injection: [Technique used]
- Network beacons: [Every 5s ± jitter]
- Persistence: [None/Registry/Scheduled Task]
- File modifications: [List]

### MITRE ATT&CK Mapping
- T1071.001: Web Protocols (HTTP/HTTPS C2)
- T1027: Obfuscated Files or Information
- T1055: Process Injection
- T1562.001: Impair Defenses (AMSI/ETW bypass)
- T1071.004: DNS (If using domain fronting)

### Recommendations
1. [Improvement suggestion]
2. [OPSEC consideration]
3. [Detection mitigation]
```

---

## ️ OPSEC WARNINGS

### DO NOT:
- Upload payloads to VirusTotal
- Use public URL scanners for sensitive domains
- Test on production systems
- Leave artifacts on test systems
- Use your personal Google account for testing

### DO:
- Use isolated test environments
- Use burner accounts for API testing
- Clean up test artifacts
- Use VPN/Tor for public checks
- Document everything for research

---

## ️ AUTOMATED TESTING SCRIPT

```bash
#!/bin/bash
# av_test.sh - Automated AV testing

PAYLOAD="/home/kali/Main C2 Framework/advanced-steganography-phishing/payloads/empire_ps_obfuscated.exe"
VM_NAME="Windows10-Test"

echo "[+] Starting AV evasion test..."

# 1. Copy payload to VM
scp "$PAYLOAD" user@vmtmp/test.exe

# 2. Execute and monitor
ssh user@vm "powershell.exe -Command 'Start-Process C:\\tmp\\test.exe'"

# 3. Check for detection
sleep 30
ssh user@vm "powershell.exe -Command 'Get-MpThreatDetection'" > detection_results.txt

# 4. Capture traffic
timeout 60 tcpdump -i eth0 host 161.35.155.3 -w test_traffic.pcap

echo "[+] Test complete. Check detection_results.txt"
```

---

## Additional Resources

- **MITRE ATT&CK**: https/attack.mitre.org/
- **ScareCrow Documentation**: https/github.com/optiv/ScareCrow
- **ThreatCheck**: https/github.com/rasta-mouse/ThreatCheck
- **AMSI Bypass Techniques**: https/github.com/S3cur3Th1sSh1t/Amsi-Bypass-Powershell

---

**Ready to test your payload?** Start with Phase 1 baseline testing!
