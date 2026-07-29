
import re
import time
import json
import random
import requests
import threading
import urllib.parse
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

class AnonScraper:
    """Advanced multi-engine CC scraper — Dorks + Direct + Paste + File"""

    UAS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0",
    ]

    CC_PATTERNS = [
        r"\b4[0-9]{12}(?:[0-9]{3})?\b",  # Visa
        r"\b5[1-5][0-9]{14}\b",  # MasterCard
        r"\b3[47][0-9]{13}\b",  # Amex
        r"\b3(?:0[0-5]|[68][0-9])[0-9]{11}\b",  # Diners
        r"\b6(?:011|5[0-9]{2})[0-9]{12}\b",  # Discover
    ]

    EXPIRY_PATTERNS = [
        r"\b(0[1-9]|1[0-2])[\/\-|](20)?[0-9]{2}\b",
        r"\b(0[1-9]|1[0-2])[-\s](20)?[0-9]{2}\b",
    ]

    CVV_PATTERN = r"\b[0-9]{3,4}\b"

    # Google Dorks for finding CC dumps
    DORKS = [
        'site:pastebin.com "visa" "cvv"',
        'site:pastebin.com "mastercard" "exp"',
        'site:pastebin.com "cc" "dump"',
        'site:ghostbin.co "cc" "cvv"',
        'site:zerobin.net "visa" "mastercard"',
        'site:privatebin.net "cc" "dump"',
        'site:textise.net "cc" "cvv"',
        'site:justpaste.it "cc" "dump"',
        'site:cl1p.net "visa" "mastercard"',
        'site:dpaste.com "cc" "cvv"',
        'intitle:"index of" "cc.txt"',
        'intitle:"index of" "cards.txt"',
        'intitle:"index of" "dumps.txt"',
        'intitle:"index of" "fullz"',
        'filetype:txt "visa" "mastercard" "cvv"',
        'filetype:csv "cc_num" "exp_date"',
        'filetype:sql "credit_card" "cvv"',
        'site:github.com "cc" "dump" filetype:txt',
        'site:github.com "cards" "cvv" filetype:txt',
        'inurl:raw.githubusercontent.com "cc" "cvv"',
        'site:rentry.co "cc" "cvv"',
        'site:termbin.com "visa" "mastercard"',
        'site:0bin.net "cc" "dump"',
        'site:hastebin.com "cc" "cvv"',
        'site:cl1p.net "cc" "dump"',
        'site:dumpz.org "visa" "mastercard"',
    ]

    # Direct paste sites to scrape
    PASTE_SITES = [
        "https://pastebin.com/archive",
        "https://pastebin.com/search?q=cc+dump",
        "https://rentry.co",
        "https://dpaste.com",
        "https://0bin.net",
        "https://hastebin.com",
        "https://cl1p.net",
        "https://dumpz.org",
        "https://justpaste.it",
        "https://termbin.com",
    ]

    # File hosting / dump sites
    FILE_SITES = [
        "https://file.io",
        "https://transfer.sh",
    ]

    def __init__(self, db, fx):
        self.db = db
        self.fx = fx
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": random.choice(self.UAS)})
        self.stats = {"found": 0, "errors": 0, "urls_scanned": 0, "start": None}
        self.lock = threading.Lock()
        self.running = False

    def _fetch(self, url, headers=None, timeout=15):
        try:
            h = {"User-Agent": random.choice(self.UAS)}
            if headers:
                h.update(headers)
            r = self.session.get(url, headers=h, timeout=timeout, allow_redirects=True)
            self.stats["urls_scanned"] += 1
            return r.text if r.status_code == 200 else None
        except Exception as e:
            with self.lock:
                self.stats["errors"] += 1
            return None

    def _extract_ccs(self, text, source="unknown", url=""):
        """Extract CC data from any text"""
        found = []
        if not text:
            return found

        # Find all CC numbers
        cc_matches = []
        for pat in self.CC_PATTERNS:
            cc_matches.extend(re.findall(pat, text))

        # Find expiry dates
        exp_matches = []
        for pat in self.EXPIRY_PATTERNS:
            exp_matches.extend(re.findall(pat, text))

        # Find CVVs
        cvv_matches = re.findall(self.CVV_PATTERN, text)

        # Pair them up
        for i, cc in enumerate(cc_matches[:200]):
            if not self._luhn(cc):
                continue

            exp = "??/??"
            if i < len(exp_matches):
                e = exp_matches[i]
                exp = f"{e[0]}/{e[1] if e[1] else '25'}"

            cvv = "???"
            if i < len(cvv_matches):
                cvv = cvv_matches[i]

            bank, country = self._bin_lookup(cc[:6])

            found.append({
                "number": cc, "expiry": exp, "cvv": cvv,
                "name": "", "bank": bank, "card_type": self._ctype(cc),
                "country": country, "level": "", "ctype": ""
            })

        # Add to DB
        for cc in found:
            if self.db.add_cc(cc["number"], cc["expiry"], cc["cvv"],
                            cc["name"], cc["bank"], cc["card_type"],
                            source, url, cc["country"], cc["level"], cc["ctype"]):
                with self.lock:
                    self.stats["found"] += 1
                print(self.fx.cccard(cc["number"], cc["expiry"], cc["cvv"],
                                     cc["name"], cc["bank"], cc["country"]))

        return found

    def _luhn(self, n):
        d = [int(c) for c in str(n) if c.isdigit()]
        if len(d) < 13: return False
        return (sum(d[-1::-2]) + sum([sum(divmod(2*x,10)) for x in d[-2::-2]])) % 10 == 0

    def _ctype(self, n):
        if n.startswith("4"): return "Visa"
        elif n.startswith("5"): return "MasterCard"
        elif n.startswith("3"): return "Amex"
        elif n.startswith("6"): return "Discover"
        return "Unknown"

    def _bin_lookup(self, bin6):
        try:
            r = requests.get(f"https://lookup.binlist.net/{bin6}", timeout=5,
                           headers={"User-Agent": random.choice(self.UAS)})
            if r.status_code == 200:
                d = r.json()
                return d.get("bank",{}).get("name",""), d.get("country",{}).get("name","")
        except:
            pass
        return "", ""

    # ═══════════════════════════════════════════════════════════════
    # ENGINE 1: GOOGLE DORK SEARCH
    # ═══════════════════════════════════════════════════════════════
    def engine_dork(self, dork, num_results=10):
        """Search Google dork and extract URLs"""
        print(self.fx.status(f"DORK: {dork[:40]}...", "dorking", self.fx.PURPLE))

        try:
            # Use DuckDuckGo HTML (no JS needed)
            query = urllib.parse.quote(dork)
            url = f"https://html.duckduckgo.com/html/?q={query}"
            html = self._fetch(url, timeout=20)
            if not html:
                return []

            # Extract URLs
            urls = re.findall(r'<a rel="nofollow" class="result__a" href="([^"]+)"', html)
            titles = re.findall(r'<a rel="nofollow" class="result__a"[^>]*>([^<]+)</a>', html)

            results = []
            for i, u in enumerate(urls[:num_results]):
                title = titles[i] if i < len(titles) else ""
                self.db.add_dork_result(u, title, f"dork:{dork}")
                results.append((u, title))

            return results
        except Exception as e:
            return []

    # ═══════════════════════════════════════════════════════════════
    # ENGINE 2: SCRAPE URL CONTENT
    # ═══════════════════════════════════════════════════════════════
    def engine_scrape(self, url, source="dork"):
        """Scrape a single URL for CCs"""
        print(self.fx.status(f"SCRAPING: {url[:40]}...", "scraping", self.fx.YELLOW))

        html = self._fetch(url, timeout=15)
        if html:
            # Remove HTML tags for text extraction
            text = re.sub(r'<[^>]+>', ' ', html)
            text = re.sub(r'\s+', ' ', text)
            self._extract_ccs(text, source, url)

        self.db.mark_dork_scraped(url)

    # ═══════════════════════════════════════════════════════════════
    # ENGINE 3: DIRECT PASTEBIN SCRAPE
    # ═══════════════════════════════════════════════════════════════
    def engine_pastebin(self):
        """Scrape Pastebin archive and recent pastes"""
        print(self.fx.status("PASTEBIN ARCHIVE", "scanning", self.fx.CYAN))

        # Archive page
        html = self._fetch("https://pastebin.com/archive", timeout=20)
        if html:
            paste_ids = re.findall(r'href="/([a-zA-Z0-9]{8})"', html)
            paste_ids = list(set(paste_ids))[:30]

            for pid in paste_ids:
                raw_url = f"https://pastebin.com/raw/{pid}"
                text = self._fetch(raw_url, timeout=10)
                if text and len(text) < 100000:  # Skip huge files
                    self._extract_ccs(text, "pastebin", raw_url)
                time.sleep(0.5)

    # ═══════════════════════════════════════════════════════════════
    # ENGINE 4: RENTRY / DPASTE / 0BIN
    # ═══════════════════════════════════════════════════════════════
    def engine_rentry(self):
        """Scrape rentry.co for CC dumps"""
        print(self.fx.status("RENTRY.CO", "scanning", self.fx.CYAN))

        try:
            html = self._fetch("https://rentry.co", timeout=15)
            if html:
                slugs = re.findall(r'href="/([a-zA-Z0-9_-]+)"', html)
                slugs = list(set(slugs))[:20]
                for slug in slugs:
                    if slug in ["api", "about", "contact", "terms", "privacy"]:
                        continue
                    text = self._fetch(f"https://rentry.co/{slug}/raw", timeout=10)
                    if text:
                        self._extract_ccs(text, "rentry", f"https://rentry.co/{slug}")
                    time.sleep(0.5)
        except:
            pass

    # ═══════════════════════════════════════════════════════════════
    # ENGINE 5: HASTEBIN / CL1P
    # ═══════════════════════════════════════════════════════════════
    def engine_hastebin(self):
        """Scrape hastebin.com for CCs"""
        print(self.fx.status("HASTEBIN / CL1P", "scanning", self.fx.CYAN))

        # Try to find recent pastes via search
        dork_results = self.engine_dork('site:hastebin.com "visa" "cvv"', 10)
        for url, title in dork_results:
            raw = url.replace("hastebin.com/", "hastebin.com/raw/")
            text = self._fetch(raw, timeout=10)
            if text:
                self._extract_ccs(text, "hastebin", url)
            time.sleep(0.5)

    # ═══════════════════════════════════════════════════════════════
    # ENGINE 6: GITHUB RAW FILE SEARCH
    # ═══════════════════════════════════════════════════════════════
    def engine_github(self):
        """Search GitHub for CC dump files"""
        print(self.fx.status("GITHUB RAW FILES", "scanning", self.fx.CYAN))

        queries = [
            "cc dump txt",
            "credit cards cvv",
            "carding dumps",
            "fullz dump",
        ]

        for q in queries:
            try:
                search_url = f"https://api.github.com/search/code?q={urllib.parse.quote(q)}+in:file+extension:txt"
                r = requests.get(search_url, headers={
                    "User-Agent": random.choice(self.UAS),
                    "Accept": "application/vnd.github.v3+json"
                }, timeout=15)
                if r.status_code == 200:
                    data = r.json()
                    for item in data.get("items", [])[:10]:
                        raw_url = item.get("html_url", "").replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
                        if raw_url:
                            text = self._fetch(raw_url, timeout=10)
                            if text:
                                self._extract_ccs(text, "github", raw_url)
                        time.sleep(1)
            except:
                pass
            time.sleep(2)

    # ═══════════════════════════════════════════════════════════════
    # ENGINE 7: TEXT FILES / INDEX OF
    # ═══════════════════════════════════════════════════════════════
    def engine_indexof(self):
        """Search for open directory listings with CC files"""
        print(self.fx.status("OPEN DIRECTORIES", "scanning", self.fx.CYAN))

        dorks = [
            'intitle:"index of" "cc.txt"',
            'intitle:"index of" "cards.txt"',
            'intitle:"index of" "dumps"',
            'intitle:"index of" "fullz"',
        ]

        for dork in dorks:
            results = self.engine_dork(dork, 5)
            for url, title in results:
                html = self._fetch(url, timeout=15)
                if html and "Index of" in html:
                    # Find .txt files
                    files = re.findall(r'href="([^"]+\.txt)"', html)
                    for f in files[:5]:
                        file_url = url.rstrip("/") + "/" + f
                        text = self._fetch(file_url, timeout=10)
                        if text:
                            self._extract_ccs(text, "indexof", file_url)
                        time.sleep(0.5)
                time.sleep(1)

    # ═══════════════════════════════════════════════════════════════
    # ENGINE 8: COMBO LIST SITES
    # ═══════════════════════════════════════════════════════════════
    def engine_combo(self):
        """Search for combo lists that might contain CCs"""
        print(self.fx.status("COMBO LISTS", "scanning", self.fx.CYAN))

        # Known combo list sources (these rotate, so we dork)
        dorks = [
            'site:pastebin.com "combo" "@gmail.com"',
            'site:pastebin.com "combo" "@yahoo.com"',
            'site:ghostbin.co "combo"',
        ]

        for dork in dorks[:2]:
            results = self.engine_dork(dork, 5)
            for url, title in results:
                self.engine_scrape(url, "combo")
                time.sleep(1)

    # ═══════════════════════════════════════════════════════════════
    # ENGINE 9: TELEGRAM CHANNEL SCRAPER (via search)
    # ═══════════════════════════════════════════════════════════════
    def engine_telegram_search(self):
        """Search for Telegram channels with CC dumps"""
        print(self.fx.status("TELEGRAM CHANNELS", "scanning", self.fx.CYAN))

        queries = [
            'site:t.me "cc dump"',
            'site:t.me "carding"',
            'site:t.me "cvv"',
        ]

        for q in queries:
            results = self.engine_dork(q, 5)
            for url, title in results:
                self.db.add_dork_result(url, title, "telegram")
            time.sleep(1)

    # ═══════════════════════════════════════════════════════════════
    # ENGINE 10: TEST / DEMO MODE (Generates sample data for testing)
    # ═══════════════════════════════════════════════════════════════
    def engine_test(self):
        """Generate test CCs to verify system works"""
        print(self.fx.status("TEST MODE — GENERATING SAMPLES", "testing", self.fx.MAGENTA))

        # These are test/invalid numbers for verification
        test_ccs = [
            ("4532015112830366", "12/25", "123", "Test User", "Chase Bank", "Visa", "US"),
            ("5425233430109903", "11/26", "456", "Demo Name", "Bank of America", "MasterCard", "US"),
            ("374245455400126", "09/25", "789", "Sample", "Amex", "Amex", "US"),
            ("6011514433546201", "03/27", "321", "Example", "Discover", "Discover", "US"),
        ]

        for num, exp, cvv, name, bank, ctype, country in test_ccs:
            if self.db.add_cc(num, exp, cvv, name, bank, ctype, "test-mode", "", country, "", ""):
                with self.lock:
                    self.stats["found"] += 1
                print(self.fx.cccard(num, exp, cvv, name, bank, country))

        print(f"{self.fx.GREEN}✅ Test mode complete — system verified!{self.fx.RESET}")

    # ═══════════════════════════════════════════════════════════════
    # MASTER RUN — ALL ENGINES
    # ═══════════════════════════════════════════════════════════════
    def run_all(self, mode="full"):
        self.running = True
        self.stats["start"] = datetime.now()

        print(f"\n{self.fx.fire('═══ ANON MONSTER SCAN — ALL ENGINES ═══')}\n")

        if mode == "test":
            self.engine_test()
        elif mode == "fast":
            # Fast mode — dorks + pastebin only
            self.engine_dork('site:pastebin.com "visa" "cvv"', 10)
            self.engine_pastebin()
            self.engine_rentry()
        elif mode == "deep":
            # Deep mode — all engines
            self.engine_dork('site:pastebin.com "visa" "cvv"', 15)
            self.engine_dork('site:pastebin.com "mastercard" "exp"', 15)
            self.engine_dork('site:ghostbin.co "cc" "dump"', 10)
            self.engine_dork('intitle:"index of" "cc.txt"', 10)
            self.engine_pastebin()
            self.engine_rentry()
            self.engine_hastebin()
            self.engine_github()
            self.engine_indexof()
            self.engine_combo()
            self.engine_telegram_search()
        else:
            # Default — balanced
            self.engine_dork('site:pastebin.com "visa" "cvv"', 10)
            self.engine_pastebin()
            self.engine_rentry()
            self.engine_github()

        self._final_stats()
        self.running = False

    def _final_stats(self):
        dur = (datetime.now() - self.stats["start"]).total_seconds()
        print(f"\n{self.fx.blood('═'*70)}")
        print(self.fx.box(" SCAN COMPLETE ", self.fx.GREEN, 70, "heavy"))
        print(f"{self.fx.CYAN}  URLs Scanned:  {self.fx.WHITE}{self.stats['urls_scanned']}")
        print(f"{self.fx.CYAN}  CCs Found:     {self.fx.GREEN}{self.stats['found']} 💳")
        print(f"{self.fx.CYAN}  Errors:        {self.fx.RED}{self.stats['errors']}")
        print(f"{self.fx.CYAN}  Duration:      {self.fx.YELLOW}{dur:.1f}s")
        print(f"{self.fx.CYAN}  DB Total:      {self.fx.MAGENTA}{self.db.get_total()}")
        print(f"{self.fx.blood('═'*70)}\n")

        stats = self.db.get_stats()
        if stats:
            print(self.fx.ice("📊 BY SOURCE:"))
            for s, c in stats.items():
                print(f"  {self.fx.CYAN}{s:<25} {self.fx.progress(c, max(stats.values()), 25)} {self.fx.WHITE}{c}")

        self.db.log_scan("monster", self.stats["found"], self.stats["errors"], dur)
