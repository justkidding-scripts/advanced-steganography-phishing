#!/bin/bash
# Quick Start Script for Empire C2 Framework

set -e

echo "================================================"
echo "  Empire C2 Framework - Quick Start"
echo "================================================"

# Check if Empire is installed
if [ ! -d "/opt/Empire" ]; then
    echo "[!] Empire not found in /opt/Empire"
    echo "[+] Cloning Empire from GitHub..."
    cd /opt && sudo git clone --recursive https://github.com/BC-SECURITY/Empire.git
    cd /opt/Empire && sudo ./setup/install.sh
fi

cd /opt/Empire

# Start Empire server
echo "[+] Starting Empire server..."
echo "[+] API will be available at: http://127.0.0.1:1337"
echo "[+] Default credentials: empireadmin / password123"
echo ""
echo "[+] To access Empire CLI:"
echo "    cd /opt/Empire"
echo "    sudo python3 empire --rest"
echo ""
echo "[+] To access Starkiller:"
echo "    https://161-35-155-3.sslip.io"
echo ""

# Start server in background
sudo python3 empire server &

echo "[+] Empire server starting in background (PID: $!)"
echo "[+] Waiting for server to initialize..."
sleep 10

# Check if server is running
if curl -s http://127.0.0.1:1337/api/v2/meta/version > /dev/null 2>&1; then
    echo "[✓] Empire API is responding!"
    curl -s http://127.0.0.1:1337/api/v2/meta/version | python3 -m json.tool
else
    echo "[!] Empire API not responding yet. Check logs: tail -f /opt/Empire/empire.log"
fi

echo ""
echo "================================================"
echo "  Next Steps:"
echo "================================================"
echo "1. Configure listeners (see DEPLOYMENT_GUIDE.md)"
echo "2. Generate stagers"
echo "3. Setup nginx proxy on Digital Ocean"
echo "4. Test connection to droplet"
echo ""
