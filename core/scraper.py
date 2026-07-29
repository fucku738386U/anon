
import re
import time
import json
import random
import requests
import threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin, quote

class AnonScraper:
    """Advanced multi-threaded scraper with proxy rotation & anti-bot"""

    PROXY_POOL = [
        None,  # Direct
        # Add your proxies here: "http://user:pass@ip:port"
    ]

    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15",
    ]

    def __init__(self, db, fx, proxy_pool=None):
        self.db = db
        self.fx = fx
        self.proxy_pool = proxy_pool or self.PROXY_POOL
        self.session = requests.Session()
        self.running = False
        self.stats = {"scanned": 0, "found": 0, "errors": 0, "start": None}
        self.lock = threading.Lock()

    def _proxy(self):
        return random.choice(self.proxy_pool) if self.proxy_pool else None

    def _headers(self, extra=None):
        h = {
            "User-Agent": random.choice(self.USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0",
        }
        if extra:
            h.update(extra)
        return h

    def _fetch(self, url, headers=None, timeout=20):
        proxy = self._proxy()
        proxies = {"http": proxy, "https": proxy} if proxy else None
        try:
            resp = self.session.get(url, headers=self._headers(headers), proxies=proxies, timeout=timeout)
            return resp.text if resp.status_code == 200 else None
        except Exception as e:
            with self.lock:
                self.stats["errors"] += 1
            return None

    def _extract_cc(self, text, patterns):
        found = []
        cc_pat = patterns.get("cc_number", r"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|3(?:0[0-5]|[68][0-9])[0-9]{11}|6(?:011|5[0-9]{2})[0-9]{12}|(?:2131|1800|35\d{3})\d{11})\b")
        exp_pat = patterns.get("expiry", r"\b(0[1-9]|1[0-2])[\/\-\|\s](20)?[0-9]{2}\b")
        cvv_pat = patterns.get("cvv", r"\b[0-9]{3,4}\b")

        cc_matches = re.findall(cc_pat, text)
        exp_matches = re.findall(exp_pat, text)
        cvv_matches = re.findall(cvv_pat, text)

        for i, cc in enumerate(cc_matches[:100]):
            exp = f"{exp_matches[i][0]}/{exp_matches[i][1] if exp_matches[i][1] else '25'}" if i < len(exp_matches) else "??/??"
            cvv = cvv_matches[i] if i < len(cvv_matches) else "???"
            found.append({
                "number": cc, "expiry": exp, "cvv": cvv,
                "name": "", "bank": "", "card_type": self._ctype(cc),
                "country": "", "level": "", "type": ""
            })
        return found

    def _ctype(self, n):
        if n.startswith("4"): return "Visa"
        elif n.startswith("5"): return "MasterCard"
        elif n.startswith("3"): return "Amex"
        elif n.startswith("6"): return "Discover"
        return "Unknown"

    def _luhn(self, n):
        d = [int(c) for c in str(n) if c.isdigit()]
        if len(d) < 13: return False
        return (sum(d[-1::-2]) + sum([sum(divmod(2*x,10)) for x in d[-2::-2]])) % 10 == 0

    def _bin_lookup(self, cc):
        try:
            r = requests.get(f"https://lookup.binlist.net/{cc[:6]}", timeout=5, headers={"User-Agent": random.choice(self.USER_AGENTS)})
            if r.status_code == 200:
                d = r.json()
                return d.get("bank",{}).get("name",""), d.get("country",{}).get("name",""), d.get("scheme",""), d.get("type",""), d.get("brand","")
        except:
            pass
        return "", "", "", "", ""

    def scan(self, site_cfg, site_id):
        name = site_cfg["name"]
        base = site_cfg.get("base_url", "")
        subs = site_cfg.get("subreddits", site_cfg.get("urls", []))
        queries = site_cfg.get("search_queries", [])
        patterns = site_cfg.get("patterns", {})
        rate = site_cfg.get("rate_limit", 2.0)

        print(self.fx.status(name, "scanning", self.fx.YELLOW))
        found_site = 0

        for sub in subs:
            for q in queries:
                url = f"{base}/{sub}/search/?q={quote(q)}&sort=new&restrict_sr=1" if "reddit" in base else f"{sub}"
                html = self._fetch(url)
                if not html:
                    continue

                posts = re.findall(r'href="(/r/[^"]+/comments/[^"]+)"', html) if "reddit" in base else re.findall(r'href="([^"]+)"', html)
                posts = list(set(posts))[:15]

                for post in posts:
                    full = urljoin(base, post) if not post.startswith("http") else post
                    ph = self._fetch(full)
                    if not ph:
                        continue

                    ccs = self._extract_cc(ph, patterns)
                    for cc in ccs:
                        if self._luhn(cc["number"]):
                            bank, country, scheme, ctype, brand = self._bin_lookup(cc["number"])
                            success = self.db.add_cc(
                                cc["number"], cc["expiry"], cc["cvv"],
                                cc["name"], bank or cc["bank"], cc["card_type"],
                                site_id, full, country, level, ctype
                            )
                            if success:
                                found_site += 1
                                with self.lock:
                                    self.stats["found"] += 1
                                print(self.fx.cccard(cc["number"], cc["expiry"], cc["cvv"], cc["name"], bank or cc["bank"]))

                    time.sleep(rate)
                time.sleep(rate)

        print(self.fx.status(name, "done", self.fx.GREEN))
        return found_site

    def run_all(self, sites, workers=4):
        self.running = True
        self.stats["start"] = datetime.now()
        print(f"\n{self.fx.fire('═══ ANON SCAN SEQUENCE INITIATED ═══')}\n")

        with ThreadPoolExecutor(max_workers=workers) as ex:
            futures = {ex.submit(self.scan, cfg, sid): sid for sid, cfg in sites.items()}
            for f in as_completed(futures):
                sid = futures[f]
                try:
                    f.result()
                    self.stats["scanned"] += 1
                except Exception as e:
                    print(self.fx.status(sid, "error", self.fx.RED))

        self.running = False
        self._final()

    def _final(self):
        dur = (datetime.now() - self.stats["start"]).total_seconds()
        print(f"\n{self.fx.blood('═'*65)}")
        print(self.fx.box(" SCAN COMPLETE ", self.fx.GREEN, 65, "heavy"))
        print(f"{self.fx.CYAN}  Sites Scanned: {self.fx.WHITE}{self.stats['scanned']}")
        print(f"{self.fx.CYAN}  CCs Found:     {self.fx.GREEN}{self.stats['found']} 💳")
        print(f"{self.fx.CYAN}  Errors:        {self.fx.RED}{self.stats['errors']}")
        print(f"{self.fx.CYAN}  Duration:      {self.fx.YELLOW}{dur:.1f}s")
        print(f"{self.fx.CYAN}  DB Total:      {self.fx.MAGENTA}{self.db.get_total()}")
        print(f"{self.fx.blood('═'*65)}\n")

        stats = self.db.get_stats()
        if stats:
            print(self.fx.ice("📊 BREAKDOWN:"))
            for s, c in stats.items():
                print(f"  {self.fx.CYAN}{s:<25} {self.fx.progress(c, max(stats.values()), 25)} {self.fx.WHITE}{c}")
