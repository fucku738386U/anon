
import sqlite3
import json
import hashlib
from datetime import datetime
from pathlib import Path

class AnonDB:
    def __init__(self, db_path="db/anon.db"):
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._init()

    def _init(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS ccs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                number TEXT, expiry TEXT, cvv TEXT, name TEXT,
                bank TEXT, card_type TEXT, site_source TEXT,
                url_source TEXT, bin_info TEXT, luhn_valid INTEGER DEFAULT 0,
                first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                hash TEXT UNIQUE, status TEXT DEFAULT 'fresh',
                country TEXT, level TEXT, type TEXT
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS sites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE, url TEXT, type TEXT,
                status TEXT DEFAULT 'active', last_scan TIMESTAMP,
                total_found INTEGER DEFAULT 0, config TEXT
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                site_name TEXT, started TIMESTAMP, ended TIMESTAMP,
                found INTEGER DEFAULT 0, errors TEXT, proxy_used TEXT
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS proxies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                proxy TEXT UNIQUE, status TEXT DEFAULT 'active',
                last_used TIMESTAMP, success_rate REAL DEFAULT 0,
                country TEXT, speed REAL
            )
        """)
        self.conn.commit()

    def add_cc(self, number, expiry, cvv, name, bank, card_type, site, url, country="", level="", ctype=""):
        h = hashlib.sha256(f"{number}:{cvv}".encode()).hexdigest()[:16]
        try:
            self.cursor.execute("""
                INSERT OR IGNORE INTO ccs (number, expiry, cvv, name, bank, card_type, site_source, url_source, hash, country, level, type)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
            """, (number, expiry, cvv, name, bank, card_type, site, url, h, country, level, ctype))
            self.conn.commit()
            return self.cursor.rowcount > 0
        except:
            return False

    def get_by_site(self, site, limit=100):
        self.cursor.execute("SELECT * FROM ccs WHERE site_source=? ORDER BY first_seen DESC LIMIT ?", (site, limit))
        return self.cursor.fetchall()

    def get_stats(self):
        self.cursor.execute("SELECT site_source, COUNT(*) FROM ccs GROUP BY site_source")
        return dict(self.cursor.fetchall())

    def get_total(self):
        self.cursor.execute("SELECT COUNT(*) FROM ccs")
        return self.cursor.fetchone()[0]

    def get_fresh(self, limit=50):
        self.cursor.execute("SELECT * FROM ccs WHERE status='fresh' ORDER BY first_seen DESC LIMIT ?", (limit,))
        return self.cursor.fetchall()

    def add_site(self, name, url, stype, config=None):
        try:
            self.cursor.execute("INSERT OR IGNORE INTO sites (name, url, type, config) VALUES (?,?,?,?)",
                              (name, url, stype, json.dumps(config) if config else None))
            self.conn.commit()
        except:
            pass

    def get_sites(self, status="active"):
        self.cursor.execute("SELECT name, url, type, status, config FROM sites WHERE status=?", (status,))
        return self.cursor.fetchall()

    def export_txt(self, site=None, fn=None):
        if site:
            data = self.get_by_site(site, 99999)
            fn = fn or f"exports/{site}_ccs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        else:
            self.cursor.execute("SELECT number, expiry, cvv, name, bank, site_source FROM ccs")
            data = self.cursor.fetchall()
            fn = fn or f"exports/all_ccs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        Path(fn).parent.mkdir(parents=True, exist_ok=True)
        with open(fn, "w") as f:
            for r in data:
                f.write(f"{'|'.join(map(str, r))}\n")
        return fn

    def export_json(self, site=None):
        if site:
            data = self.get_by_site(site, 99999)
        else:
            self.cursor.execute("SELECT * FROM ccs")
            data = self.cursor.fetchall()
        fn = f"exports/ccs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        Path(fn).parent.mkdir(parents=True, exist_ok=True)
        with open(fn, "w") as f:
            json.dump(data, f, indent=2, default=str)
        return fn

    def export_csv(self, site=None):
        import csv
        fn = f"exports/ccs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        Path(fn).parent.mkdir(parents=True, exist_ok=True)
        self.cursor.execute("SELECT * FROM ccs" + (" WHERE site_source=?" if site else ""), (site,) if site else ())
        rows = self.cursor.fetchall()
        cols = [d[0] for d in self.cursor.description]
        with open(fn, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(cols)
            w.writerows(rows)
        return fn

    def close(self):
        self.conn.close()
