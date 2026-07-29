
import re
import requests
from core.scraper import AnonScraper

class PastebinMode:
    """Auto-detect and scrape paste links"""
    def __init__(self, db):
        self.db = db
        from core.fx import fx
        self.fx = fx

    def run(self):
        print(f"\n{self.fx.ice('📋 PASTEBIN MODE')}\n")
        # Pastebin scraper logic
        pastebin_sites = {
            "pastebin": {"name": "Pastebin", "base_url": "https://pastebin.com", "urls": ["/archive"], "search_queries": ["cc", "card", "cvv"], "patterns": {"cc_number": r"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14})\b"}, "rate_limit": 1.5},
            "ghostbin": {"name": "Ghostbin", "base_url": "https://ghostbin.co", "urls": ["/"], "search_queries": ["cc"], "patterns": {"cc_number": r"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14})\b"}, "rate_limit": 2.0},
        }
        AnonScraper(self.db, self.fx).run_all(pastebin_sites, workers=3)
