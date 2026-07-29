
from core.scraper import AnonScraper
from config.sites import get_all_sites

class StealthMode:
    """Anti-bot + fingerprint randomization"""
    def __init__(self, db):
        self.db = db
        from core.fx import fx
        self.fx = fx

    def run(self):
        print(f"\n{self.fx.blood('👻 STEALTH MODE — ANTI-BOT ENABLED')}\n")
        print(f"{self.fx.YELLOW}Features:{self.fx.RESET}")
        print(f"  • Random User-Agent rotation")
        print(f"  • Proxy rotation")
        print(f"  • Request delay jitter")
        print(f"  • Header fingerprint randomization")
        print(f"  • Cookie jar management\n")
        sites = get_all_sites()
        scraper = AnonScraper(self.db, self.fx)
        scraper.run_all(sites, workers=2)
