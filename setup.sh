#!/bin/bash
# ANON Scraper — VPS Setup
echo "🌀 ANON MONSTER SCRAPER SETUP"
echo ""
pip3 install requests beautifulsoup4 lxml fake-useragent -q 2>/dev/null
echo "⚡ Creating cc command..."
rm /usr/local/bin/cc 2>/dev/null
ln -sf $(pwd)/anon.py /usr/local/bin/cc
chmod +x anon.py
echo "alias cc='$(pwd)/anon.py'" >> ~/.bashrc 2>/dev/null
echo "alias cc='$(pwd)/anon.py'" >> ~/.zshrc 2>/dev/null
echo ""
echo "✅ Setup complete!"
echo "   cc         → Launch"
echo "   cc --test  → Test mode"
echo "   cc --deep  → Deep scan"
echo "   cc --auto  → 24/7 daemon"
echo ""
echo "🌀 Sab chhod, system tod."
