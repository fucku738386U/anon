
from core.scraper import AnonScraper
from config.sites import get_all_sites

class InstantMode:
    """30-second auto-scan. Just press ENTER."""
    def __init__(self, db):
        self.db = db
        from core.fx import fx
        self.fx = fx

    def run(self):
        print(f"\n{self.fx.fire('⚡ INSTANT MODE — 30 SECOND SCAN')}\n")
        self.fx.spinner(0.5, "Loading sources")
        sites = get_all_sites()
        print(f"{self.fx.CYAN}Loaded {len(sites)} sources{self.fx.RESET}\n")
        scraper = AnonScraper(self.db, self.fx)
        scraper.run_all(sites, workers=4)
