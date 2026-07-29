
class ExportMode:
    """Auto-export every N minutes"""
    def __init__(self, db):
        self.db = db
        from core.fx import fx
        self.fx = fx

    def run(self):
        print(f"\n{self.fx.green('💾 EXPORT MODE')}\n")
        print(f"  {self.fx.GREEN}[1]{self.fx.RESET} TXT")
        print(f"  {self.fx.GREEN}[2]{self.fx.RESET} JSON")
        print(f"  {self.fx.GREEN}[3]{self.fx.RESET} CSV")
        c = input(f"\n{self.fx.YELLOW}Format: {self.fx.RESET}")
        if c == "1":
            fn = self.db.export_txt()
        elif c == "2":
            fn = self.db.export_json()
        else:
            fn = self.db.export_csv()
        print(f"{self.fx.GREEN}✅ Exported: {fn}{self.fx.RESET}")
