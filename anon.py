#!/usr/bin/env python3
# ═══════════════════════════════════════════════════════════════
# ANON SCRAPER v2.0 — ADVANCED EDITION
# Created by: anonymous | anonymous.world
# 10 Modes | 10 Features | Instant Launch | Auto-Everything
# ═══════════════════════════════════════════════════════════════

import sys
import os
import time
import json
import signal
import argparse
import threading
from pathlib import Path
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.fx import AnonFX, fx
from core.db import AnonDB
from core.scraper import AnonScraper
from modes.instant import InstantMode
from modes.manual import ManualMode
from modes.auto import AutoMode
from modes.deep import DeepMode
from modes.pastebin import PastebinMode
from modes.forum import ForumMode
from modes.darkweb import DarkWebMode
from modes.telegram import TelegramMode
from modes.export import ExportMode
from modes.stealth import StealthMode
from modes.monitor import MonitorMode

class AnonLauncher:
    """Main launcher — just press ENTER, everything auto"""

    VERSION = "2.0.0-ADVANCED"
    MODES = {
        "1": ("🚀 INSTANT", "30-sec auto-scan all sources", InstantMode),
        "2": ("🔍 MANUAL", "Choose sites & options", ManualMode),
        "3": ("🤖 AUTO", "Background 24/7 daemon", AutoMode),
        "4": ("🕳️ DEEP", "Recursive multi-page crawl", DeepMode),
        "5": ("📋 PASTEBIN", "Auto-detect & scrape pastes", PastebinMode),
        "6": ("💬 FORUM", "XenForo/vBulletin scraper", ForumMode),
        "7": ("🧅 DARKWEB", "Tor proxy .onion support", DarkWebMode),
        "8": ("📱 TELEGRAM", "Auto-send to Telegram bot", TelegramMode),
        "9": ("💾 EXPORT", "Auto-export every N mins", ExportMode),
        "10": ("👻 STEALTH", "Anti-bot + fingerprint random", StealthMode),
        "11": ("📊 MONITOR", "Live dashboard + alerts", MonitorMode),
    }

    def __init__(self):
        self.db = None
        self.running = True
        signal.signal(signal.SIGINT, self._handler)
        self._setup()

    def _handler(self, s, f):
        print(f"\n{fx.RED}\n💀 Interrupted. Shutting down...{fx.RESET}")
        self.running = False
        sys.exit(0)

    def _setup(self):
        fx.banner()
        fx.spinner(0.5, "Initializing")
        self.db = AnonDB()
        fx.typing_effect(fx.green_gradient("✅ Database ready"), 0.01)
        fx.typing_effect(fx.green_gradient("✅ 10 modes loaded"), 0.01)
        fx.typing_effect(fx.green_gradient("✅ Auto-config applied"), 0.01)
        print()

    def _menu(self):
        print(fx.box(" ANON CONTROL CENTER ", fx.CYAN, 75, "double"))
        print()
        for k, (name, desc, _) in self.MODES.items():
            print(f"  {fx.GREEN}[{k}]{fx.RESET} {fx.BOLD}{name:<12}{fx.RESET} {fx.DIM}— {desc}{fx.RESET}")
        print(f"  {fx.RED}[0]{fx.RESET} {fx.BOLD}{'EXIT':<12}{fx.RESET} {fx.DIM}— Kill switch{fx.RESET}")
        print()
        print(fx.box("", fx.DIM, 75, "single"))

    def run(self):
        while self.running:
            self._menu()
            choice = input(f"{fx.CYAN}anon>{fx.RESET} {fx.WHITE}").strip()
            print(fx.RESET)

            if choice == "":
                # DEFAULT — Instant mode on ENTER
                print(fx.fire_gradient("⚡ ENTER pressed → Launching INSTANT MODE"))
                InstantMode(self.db).run()
            elif choice in self.MODES:
                _, _, ModeClass = self.MODES[choice]
                ModeClass(self.db).run()
            elif choice == "0":
                fx.glitch_text("SYSTEM SHUTDOWN...", 2)
                print(f"{fx.RED}💀 ANON offline. Sab chhod, system tod. 🕳️{fx.RESET}")
                break
            else:
                print(f"{fx.RED}❌ Invalid! Press ENTER for instant mode.{fx.RESET}")

            input(f"\n{fx.DIM}Press ENTER to continue...{fx.RESET}")
            os.system('clear')


def main():
    parser = argparse.ArgumentParser(description="ANON Scraper v2.0")
    parser.add_argument("--instant", "-i", action="store_true", help="Instant mode (default)")
    parser.add_argument("--auto", "-a", action="store_true", help="Auto daemon mode")
    parser.add_argument("--deep", "-d", action="store_true", help="Deep scan mode")
    parser.add_argument("--stealth", "-s", action="store_true", help="Stealth mode")
    parser.add_argument("--monitor", "-m", action="store_true", help="Monitor dashboard")
    parser.add_argument("--pastebin", "-p", action="store_true", help="Pastebin mode")
    parser.add_argument("--forum", "-f", action="store_true", help="Forum mode")
    parser.add_argument("--darkweb", "-dw", action="store_true", help="Dark web mode")
    parser.add_argument("--telegram", "-t", action="store_true", help="Telegram notify mode")
    parser.add_argument("--export", "-e", action="store_true", help="Export mode")
    args = parser.parse_args()

    launcher = AnonLauncher()

    if args.auto:
        AutoMode(launcher.db).run()
    elif args.deep:
        DeepMode(launcher.db).run()
    elif args.stealth:
        StealthMode(launcher.db).run()
    elif args.monitor:
        MonitorMode(launcher.db).run()
    elif args.pastebin:
        PastebinMode(launcher.db).run()
    elif args.forum:
        ForumMode(launcher.db).run()
    elif args.darkweb:
        DarkWebMode(launcher.db).run()
    elif args.telegram:
        TelegramMode(launcher.db).run()
    elif args.export:
        ExportMode(launcher.db).run()
    else:
        launcher.run()


if __name__ == "__main__":
    main()
