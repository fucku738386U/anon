
import time
import os

class MonitorMode:
    """Live dashboard with real-time updates"""
    def __init__(self, db):
        self.db = db
        from core.fx import fx
        self.fx = fx

    def run(self):
        print(f"\n{self.fx.neon('📊 MONITOR MODE — LIVE DASHBOARD')}\n")
        try:
            while True:
                os.system('clear')
                self.fx.banner()
                total = self.db.get_total()
                stats = self.db.get_stats()
                print(f"\n{self.fx.box(' LIVE STATS ', self.fx.CYAN, 50, 'double')}")
                print(f"{self.fx.CYAN}  Total CCs: {self.fx.GREEN}{total}{self.fx.RESET}")
                print(f"{self.fx.CYAN}  Fresh:     {self.fx.GREEN}{len(self.db.get_fresh())}{self.fx.RESET}")
                if stats:
                    print(f"\n{self.fx.YELLOW}  By Source:{self.fx.RESET}")
                    for s, c in stats.items():
                        print(f"    {self.fx.CYAN}{s:<20} {self.fx.GREEN}{c}{self.fx.RESET}")
                print(f"\n{self.fx.DIM}Refreshing every 5s... Press Ctrl+C to exit{self.fx.RESET}")
                time.sleep(5)
        except KeyboardInterrupt:
            pass
