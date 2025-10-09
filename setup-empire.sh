#!/bin/bash
# Empire C2 Setup Script for Digital Ocean Integration

set -e

echo "[+] Installing PowerShell Empire and dependencies..."

# Clone Empire from BC-SECURITY
cd /opt
if [ ! -d "/opt/Empire" ]; then
    sudo git clone --recursive https://github.com/BC-SECURITY/Empire.git
fi

cd /opt/Empire

# Install dependencies
sudo pip3 install -r requirements.txt

# Run setup
sudo ./setup/install.sh

echo "[+] Empire installed successfully!"
echo "[+] Starting Empire server..."

# Start Empire server
sudo powershell-empire server &

echo "[+] Waiting for Empire to start..."
sleep 10

echo "[+] Checking Empire status..."
curl -s http://127.0.0.1:1337/api/v2/meta/version || echo "Empire may need more time to start"

echo "[+] Empire setup complete!"
echo "[+] Access Starkiller at: https://161-35-155-3.sslip.io"
echo "[+] API endpoint: http://127.0.0.1:1337"
echo "[+] Default credentials: empireadmin / password123"
