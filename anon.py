#!/usr/bin/env python3
# ANON SCRAPER v2.0 — MONSTER EDITION
# Created by: anonymous | anonymous.world
# 10 Engines | Auto-Dork | Instant Results

import sys
import os
import time
import signal
import argparse
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.fx import AnonFX, fx
from core.db import AnonDB
from core.scraper import AnonScraper

class AnonLauncher:
    VERSION = "2.0.0-MONSTER"

    MODES = {
        "1": ("🚀 INSTANT", "Fast scan — Dorks + Pastebin + Rentry", "fast"),
        "2": ("🕳️ DEEP", "Full deep scan — ALL engines", "deep"),
        "3": ("🧪 TEST", "Generate test CCs — verify system", "test"),
        "4": ("💾 EXPORT", "Export all data TXT/JSON", "export"),
        "5": ("📊 STATS", "View database statistics", "stats"),
        "6": ("🔍 DORK ONLY", "Google dork search only", "dork"),
        "7": ("📋 PASTE ONLY", "Pastebin + Rentry only", "paste"),
        "8": ("💻 GITHUB", "GitHub raw file search", "github"),
        "9": ("📁 INDEX OF", "Open directory search", "indexof"),
        "10": ("🤖 AUTO", "24/7 daemon — all engines", "auto"),
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
        fx.typing_effect(fx.green_gradient("✅ 10 engines loaded"), 0.01)
        fx.typing_effect(fx.green_gradient("✅ Auto-dork system ready"), 0.01)
        print()

    def _menu(self):
        print(fx.box(" ANON MONSTER CONTROL ", fx.CYAN, 75, "double"))
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
                print(fx.fire_gradient("⚡ ENTER pressed → INSTANT MODE"))
                scraper = AnonScraper(self.db, fx)
                scraper.run_all("fast")
            elif choice in self.MODES:
                _, _, mode = self.MODES[choice]
                if mode == "export":
                    self._export()
                elif mode == "stats":
                    self._stats()
                elif mode == "auto":
                    self._auto()
                else:
                    scraper = AnonScraper(self.db, fx)
                    scraper.run_all(mode)
            elif choice == "0":
                fx.glitch_text("SYSTEM SHUTDOWN...", 2)
                print(f"{fx.RED}💀 ANON offline. Sab chhod, system tod. 🕳️{fx.RESET}")
                break
            else:
                print(f"{fx.RED}❌ Invalid! Press ENTER for instant mode.{fx.RESET}")

            input(f"\n{fx.DIM}Press ENTER to continue...{fx.RESET}")
            os.system('clear')

    def _export(self):
        print(f"\n{fx.green_gradient('💾 EXPORT MODE')}\n")
        print(f"  {fx.GREEN}[1]{fx.RESET} TXT")
        print(f"  {fx.GREEN}[2]{fx.RESET} JSON")
        c = input(f"\n{fx.YELLOW}Format: {fx.RESET}")
        if c == "1":
            fn = self.db.export_txt()
        else:
            fn = self.db.export_json()
        print(f"{fx.GREEN}✅ Exported: {fn}{fx.RESET}")

    def _stats(self):
        total = self.db.get_total()
        stats = self.db.get_stats()
        print(f"\n{fx.box(' DATABASE STATS ', fx.MAGENTA, 60, 'double')}")
        print(f"\n  {fx.CYAN}Total CCs: {fx.GREEN}{total}{fx.RESET}")
        if stats:
            print(f"\n  {fx.YELLOW}By Source:{fx.RESET}")
            for s, c in stats.items():
                print(f"    {fx.CYAN}{s:<20} {fx.GREEN}{c}{fx.RESET}")
        print()

    def _auto(self):
        print(f"\n{fx.neon_gradient('🤖 AUTO DAEMON — 24/7')}\n")
        print(f"{fx.YELLOW}Ctrl+C to stop{fx.RESET}\n")
        while self.running:
            scraper = AnonScraper(self.db, fx)
            scraper.run_all("deep")
            print(f"\n{fx.CYAN}Sleeping 300s...{fx.RESET}\n")
            time.sleep(300)


def main():
    parser = argparse.ArgumentParser(description="ANON Scraper v2.0 Monster")
    parser.add_argument("--instant", "-i", action="store_true", help="Fast mode")
    parser.add_argument("--deep", "-d", action="store_true", help="Deep mode")
    parser.add_argument("--test", "-t", action="store_true", help="Test mode")
    parser.add_argument("--auto", "-a", action="store_true", help="Auto daemon")
    parser.add_argument("--export", "-e", action="store_true", help="Export")
    args = parser.parse_args()

    launcher = AnonLauncher()

    if args.instant:
        AnonScraper(launcher.db, fx).run_all("fast")
    elif args.deep:
        AnonScraper(launcher.db, fx).run_all("deep")
    elif args.test:
        AnonScraper(launcher.db, fx).run_all("test")
    elif args.auto:
        launcher._auto()
    elif args.export:
        launcher._export()
    else:
        launcher.run()


if __name__ == "__main__":
    main()
