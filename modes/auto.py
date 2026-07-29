
import time
import threading
from core.scraper import AnonScraper
from config.sites import get_all_sites

class AutoMode:
    """24/7 background daemon"""
    def __init__(self, db):
        self.db = db
        from core.fx import fx
        self.fx = fx
        self.running = False

    def run(self):
        print(f"\n{self.fx.neon('🤖 AUTO MODE — 24/7 DAEMON')}\n")
        print(f"{self.fx.YELLOW}Press Ctrl+C to stop{self.fx.RESET}\n")
        self.running = True
        while self.running:
            sites = get_all_sites()
            scraper = AnonScraper(self.db, self.fx)
            scraper.run_all(sites, workers=3)
            print(f"\n{self.fx.CYAN}Sleeping 300s...{self.fx.RESET}\n")
            time.sleep(300)
