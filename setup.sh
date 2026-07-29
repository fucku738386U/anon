#!/bin/bash
# ANON Scraper — VPS Setup Script
# Run: bash setup.sh

echo "🌀 ANON Scraper Setup"
echo ""

# Install deps
echo "📦 Installing dependencies..."
pip install requests beautifulsoup4 lxml fake-useragent -q 2>/dev/null

# Create alias
echo "⚡ Creating 'cc' command alias..."
ALIAS_CMD="alias cc='cd $(pwd) && python3 anon.py'"

if [ -f ~/.bashrc ]; then
    if ! grep -q "alias cc=" ~/.bashrc; then
        echo "$ALIAS_CMD" >> ~/.bashrc
        echo "✅ Added to ~/.bashrc"
    fi
fi

if [ -f ~/.zshrc ]; then
    if ! grep -q "alias cc=" ~/.zshrc; then
        echo "$ALIAS_CMD" >> ~/.zshrc
        echo "✅ Added to ~/.zshrc"
    fi
fi

# Also create global symlink
ln -sf $(pwd)/anon.py /usr/local/bin/cc 2>/dev/null || sudo ln -sf $(pwd)/anon.py /usr/local/bin/cc 2>/dev/null
chmod +x anon.py

echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 Usage:"
echo "   cc              → Launch interactive mode"
echo "   cc --instant    → Instant 30-sec scan"
echo "   cc --auto       → 24/7 daemon mode"
echo "   cc --stealth    → Stealth anti-bot mode"
echo "   cc --monitor    → Live dashboard"
echo ""
echo "🌀 Sab chhod, system tod."
