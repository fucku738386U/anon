#!/bin/bash
# ANON — Single Command Installer
echo "🌀 ANON MONSTER — Installing..."

# Remove old installations
rm -rf /tmp/anon /root/anon /home/*/anon 2>/dev/null
rm -f /usr/local/bin/cc /usr/local/bin/checker 2>/dev/null

# Clone fresh
git clone https://github.com/fucku738386U/anon.git /tmp/anon
cd /tmp/anon

# Install deps
pip3 install requests beautifulsoup4 lxml fake-useragent -q 2>/dev/null

# Create fresh symlinks
ln -sf /tmp/anon/anon.py /usr/local/bin/cc
ln -sf /tmp/anon/checker.py /usr/local/bin/checker
chmod +x /tmp/anon/anon.py /tmp/anon/checker.py

# Add aliases
echo "alias cc='/tmp/anon/anon.py'" >> ~/.bashrc 2>/dev/null
echo "alias checker='/tmp/anon/checker.py'" >> ~/.bashrc 2>/dev/null

echo ""
echo "✅ Ready!"
echo "   cc       → ANON Scraper"
echo "   checker  → Card Validator"
echo ""
echo "🌀 Sab chhod, system tod."
