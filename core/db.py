
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
                country TEXT, level TEXT, ctype TEXT,
                extra TEXT
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS dork_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE, title TEXT, source TEXT,
                found_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                scraped INTEGER DEFAULT 0
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                engine TEXT, found INTEGER, errors INTEGER,
                duration REAL, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()

    def add_cc(self, number, expiry, cvv, name, bank, card_type, site, url, country="", level="", ctype="", extra=""):
        h = hashlib.sha256(f"{number}:{cvv}".encode()).hexdigest()[:16]
        try:
            self.cursor.execute("""
                INSERT OR IGNORE INTO ccs (number, expiry, cvv, name, bank, card_type, site_source, url_source, hash, country, level, ctype, extra)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, (number, expiry, cvv, name, bank, card_type, site, url, h, country, level, ctype, extra))
            self.conn.commit()
            return self.cursor.rowcount > 0
        except:
            return False

    def add_dork_result(self, url, title, source):
        try:
            self.cursor.execute("INSERT OR IGNORE INTO dork_results (url, title, source) VALUES (?,?,?)", (url, title, source))
            self.conn.commit()
        except:
            pass

    def get_dork_unscraped(self, limit=50):
        self.cursor.execute("SELECT url, title, source FROM dork_results WHERE scraped=0 LIMIT ?", (limit,))
        return self.cursor.fetchall()

    def mark_dork_scraped(self, url):
        self.cursor.execute("UPDATE dork_results SET scraped=1 WHERE url=?", (url,))
        self.conn.commit()

    def get_total(self):
        self.cursor.execute("SELECT COUNT(*) FROM ccs")
        return self.cursor.fetchone()[0]

    def get_fresh(self, limit=100):
        self.cursor.execute("SELECT * FROM ccs WHERE status='fresh' ORDER BY first_seen DESC LIMIT ?", (limit,))
        return self.cursor.fetchall()

    def get_stats(self):
        self.cursor.execute("SELECT site_source, COUNT(*) FROM ccs GROUP BY site_source")
        return dict(self.cursor.fetchall())

    def export_txt(self, fn=None):
        fn = fn or f"exports/ccs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        Path(fn).parent.mkdir(parents=True, exist_ok=True)
        self.cursor.execute("SELECT number, expiry, cvv, name, bank, site_source, country FROM ccs")
        with open(fn, "w") as f:
            for r in self.cursor.fetchall():
                f.write(f"{'|'.join(map(str, r))}\n")
        return fn

    def export_json(self):
        fn = f"exports/ccs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        Path(fn).parent.mkdir(parents=True, exist_ok=True)
        self.cursor.execute("SELECT * FROM ccs")
        rows = self.cursor.fetchall()
        cols = [d[0] for d in self.cursor.description]
        data = [dict(zip(cols, r)) for r in rows]
        with open(fn, "w") as f:
            json.dump(data, f, indent=2, default=str)
        return fn

    def log_scan(self, engine, found, errors, duration):
        self.cursor.execute("INSERT INTO logs (engine, found, errors, duration) VALUES (?,?,?,?)",
                          (engine, found, errors, duration))
        self.conn.commit()

    def close(self):
        self.conn.close()
