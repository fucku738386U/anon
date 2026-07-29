
from core.scraper import AnonScraper
from config.sites import get_all_sites

class ManualMode:
    def __init__(self, db):
        self.db = db
        from core.fx import fx
        self.fx = fx

    def run(self):
        print(f"\n{self.fx.ice('🔍 MANUAL MODE')}\n")
        sites = get_all_sites()
        for i, (sid, cfg) in enumerate(sites.items(), 1):
            print(f"  {self.fx.GREEN}[{i}]{self.fx.RESET} {cfg['name']}")
        try:
            c = int(input(f"\n{self.fx.YELLOW}Select (0=all): {self.fx.RESET}"))
            if c == 0:
                AnonScraper(self.db, self.fx).run_all(sites, workers=3)
            else:
                sid = list(sites.keys())[c-1]
                AnonScraper(self.db, self.fx).scan(sites[sid], sid)
        except:
            print(f"{self.fx.RED}Invalid!{self.fx.RESET}")
