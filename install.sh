#!/bin/bash
# ANON SCRAPER — Single Command Setup
# Run this ONE command on VPS:
# bash <(curl -s https://raw.githubusercontent.com/fucku738386U/anon/main/install.sh)

echo "🌀 ANON SCRAPER v2.0 — Single Command Setup"
echo ""

# Remove old if exists
rm -rf /tmp/anon 2>/dev/null

# Clone fresh
echo "📦 Cloning repo..."
git clone https://github.com/fucku738386U/anon.git /tmp/anon
cd /tmp/anon

# Install deps
echo "⚡ Installing dependencies..."
pip3 install requests beautifulsoup4 lxml fake-useragent -q 2>/dev/null

# Fix symlink
echo "🔗 Setting up cc command..."
rm /usr/local/bin/cc 2>/dev/null
ln -sf /tmp/anon/anon.py /usr/local/bin/cc
chmod +x /tmp/anon/anon.py

# Add alias
echo "alias cc='/tmp/anon/anon.py'" >> ~/.bashrc 2>/dev/null
echo "alias cc='/tmp/anon/anon.py'" >> ~/.zshrc 2>/dev/null

echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 Launching ANON..."
echo ""

# Launch
python3 /tmp/anon/anon.py
