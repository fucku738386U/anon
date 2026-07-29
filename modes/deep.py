
from core.scraper import AnonScraper
from config.sites import get_all_sites

class DeepMode:
    """Recursive multi-page deep crawl"""
    def __init__(self, db):
        self.db = db
        from core.fx import fx
        self.fx = fx

    def run(self):
        print(f"\n{self.fx.blood('🕳️ DEEP MODE — RECURSIVE CRAWL')}\n")
        sites = get_all_sites()
        for sid, cfg in sites.items():
            cfg["deep_crawl"] = True
            cfg["max_pages"] = 10
        AnonScraper(self.db, self.fx).run_all(sites, workers=2)
