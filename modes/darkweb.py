
from core.scraper import AnonScraper

class DarkWebMode:
    """Tor proxy .onion site support"""
    def __init__(self, db):
        self.db = db
        from core.fx import fx
        self.fx = fx

    def run(self):
        print(f"\n{self.fx.blood('🧅 DARKWEB MODE — TOR ENABLED')}\n")
        print(f"{self.fx.YELLOW}Requires Tor proxy: socks5h://127.0.0.1:9050{self.fx.RESET}\n")
        dark_sites = {
            "dark_market_1": {"name": "Dark Market", "base_url": "http://example.onion", "urls": ["/"], "search_queries": ["cc"], "patterns": {"cc_number": r"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14})\b"}, "rate_limit": 5.0},
        }
        scraper = AnonScraper(self.db, self.fx, proxy_pool=["socks5h://127.0.0.1:9050"])
        scraper.run_all(dark_sites, workers=1)
