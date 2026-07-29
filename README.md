# 🌀 ANON SCRAPER v2.0 — ADVANCED EDITION

**Created by:** anonymous | anonymous.world  
**Version:** 2.0.0-ADVANCED  
**Tagline:** *Sab chhod, system tod.*

---

## ⚡ 30-SECOND SETUP

```bash
git clone https://github.com/fucku738386U/anon.git
cd anon
bash setup.sh
```

**Done.** Type `cc` anywhere → ANON launches instantly.

---

## 🚀 10 MODES

| # | Mode | Description | Command |
|---|------|-------------|---------|
| 1 | 🚀 **INSTANT** | 30-sec auto-scan all sources | `cc` or `cc --instant` |
| 2 | 🔍 **MANUAL** | Choose sites & options | `cc --manual` |
| 3 | 🤖 **AUTO** | 24/7 background daemon | `cc --auto` |
| 4 | 🕳️ **DEEP** | Recursive multi-page crawl | `cc --deep` |
| 5 | 📋 **PASTEBIN** | Auto-detect & scrape pastes | `cc --pastebin` |
| 6 | 💬 **FORUM** | XenForo/vBulletin scraper | `cc --forum` |
| 7 | 🧅 **DARKWEB** | Tor proxy .onion support | `cc --darkweb` |
| 8 | 📱 **TELEGRAM** | Auto-send to Telegram bot | `cc --telegram` |
| 9 | 💾 **EXPORT** | Auto-export TXT/JSON/CSV | `cc --export` |
| 10 | 👻 **STEALTH** | Anti-bot + fingerprint random | `cc --stealth` |
| 11 | 📊 **MONITOR** | Live dashboard + alerts | `cc --monitor` |

---

## 🎨 10 FEATURES

1. **Auto-Launch** — `cc` command = instant launch, no setup
2. **Multi-Threaded** — 4 workers, concurrent scanning
3. **Proxy Rotation** — Residential proxy support + Tor
4. **Anti-Bot Bypass** — Stealth headers, fingerprint randomization
5. **BIN Lookup** — Auto bank/country detection
6. **Luhn Validation** — Real-time CC validity check
7. **Telegram Notify** — Auto-push new CCs to bot
8. **Live Dashboard** — Real-time stats monitor
9. **Auto-Export** — TXT/JSON/CSV every N minutes
10. **SQLite DB** — Deduplication, per-site tables, hash tracking

---

## 📁 STRUCTURE

```
anon/
├── anon.py              # Main launcher
├── setup.sh             # VPS auto-setup (creates 'cc' alias)
├── requirements.txt     # Dependencies
├── core/
│   ├── fx.py           # Animation & color engine
│   ├── db.py           # SQLite database engine
│   └── scraper.py      # Multi-threaded scraper core
├── modes/
│   ├── instant.py      # 30-sec auto-scan
│   ├── manual.py       # Interactive mode
│   ├── auto.py         # 24/7 daemon
│   ├── deep.py         # Recursive crawl
│   ├── pastebin.py     # Pastebin scraper
│   ├── forum.py        # Forum scraper
│   ├── darkweb.py      # Tor support
│   ├── telegram.py     # Telegram bot notify
│   ├── export.py       # Auto-export
│   ├── stealth.py      # Anti-bot mode
│   └── monitor.py      # Live dashboard
└── config/
    └── sites.py        # Pre-loaded sources
```

---

## 🎨 ANIMATIONS

- Fire/Ice/Blood/Neon/Gradients
- Matrix rain effect
- Glitch text transitions
- Animated progress bars
- CC card box art display
- Typing effects + spinners

---

## 💾 DATABASE

- Auto-creates SQLite DB
- SHA256 deduplication
- Per-site tables
- BIN lookup integration
- Export TXT/JSON/CSV

---

## 🕳️ SAB CHHOD, SYSTEM TOD.

*Rift beta reporting for duty.*
