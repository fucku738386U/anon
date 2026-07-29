
from core.scraper import AnonScraper

class ForumMode:
    """XenForo / vBulletin forum scraper"""
    def __init__(self, db):
        self.db = db
        from core.fx import fx
        self.fx = fx

    def run(self):
        print(f"\n{self.fx.gold('💬 FORUM MODE')}\n")
        forums = {
            "carding_forum_1": {"name": "Carding Forum", "base_url": "https://example-forum.com", "urls": ["/forum/carding"], "search_queries": ["cc", "dump"], "patterns": {"cc_number": r"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14})\b"}, "rate_limit": 3.0},
        }
        AnonScraper(self.db, self.fx).run_all(forums, workers=2)
