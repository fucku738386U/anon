#!/bin/bash
# ANON — Single Command Installer
echo "🌀 ANON MONSTER — Installing..."
rm -rf /tmp/anon 2>/dev/null
git clone https://github.com/fucku738386U/anon.git /tmp/anon
cd /tmp/anon
pip3 install requests beautifulsoup4 lxml fake-useragent -q 2>/dev/null
rm /usr/local/bin/cc 2>/dev/null
ln -sf /tmp/anon/anon.py /usr/local/bin/cc
chmod +x /tmp/anon/anon.py
echo "alias cc='/tmp/anon/anon.py'" >> ~/.bashrc 2>/dev/null
echo ""
echo "✅ Ready! Launching..."
python3 /tmp/anon/anon.py
