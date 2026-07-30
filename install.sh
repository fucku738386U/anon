#!/bin/bash
# ANON — Single Command Installer
echo "🌀 ANON MONSTER — Installing..."
rm -rf /tmp/anon 2>/dev/null
git clone https://github.com/fucku738386U/anon.git /tmp/anon
cd /tmp/anon
pip3 install requests beautifulsoup4 lxml fake-useragent -q 2>/dev/null
rm /usr/local/bin/cc /usr/local/bin/checker 2>/dev/null
ln -sf /tmp/anon/anon.py /usr/local/bin/cc
ln -sf /tmp/anon/checker.py /usr/local/bin/checker
chmod +x /tmp/anon/anon.py /tmp/anon/checker.py
echo "alias cc='/tmp/anon/anon.py'" >> ~/.bashrc 2>/dev/null
echo "alias checker='/tmp/anon/checker.py'" >> ~/.bashrc 2>/dev/null
echo ""
echo "✅ Ready! Launching..."
echo "   cc       → ANON Scraper"
echo "   checker  → Card Validator"
echo ""
python3 /tmp/anon/anon.py
