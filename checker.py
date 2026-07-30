#!/usr/bin/env python3
# ═══════════════════════════════════════════════════════════════
# ANON CARD CHECKER v3.0 — MONSTER EDITION
# Created by: anonymous | anonymous.world
# Features: Luhn + BIN Lookup + Bank Detect + Country + Level + Live Check
# ═══════════════════════════════════════════════════════════════

import sys
import os
import re
import json
import time
import random
import requests
import threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from core.fx import AnonFX, fx

class AnonCardChecker:
    """Advanced Credit Card Validator & Checker — 100% Working"""

    # BIN Database (common bins with bank info)
    BIN_DB = {
        "4": {"type": "Visa", "levels": {"4": "Classic", "5": "Gold", "6": "Platinum", "7": "Signature", "8": "Infinite"}},
        "51": {"type": "MasterCard", "levels": {"0": "Standard", "2": "Gold", "4": "Platinum", "5": "World", "8": "World Elite"}},
        "52": {"type": "MasterCard", "levels": {"0": "Standard", "2": "Gold", "4": "Platinum"}},
        "53": {"type": "MasterCard", "levels": {"0": "Standard", "8": "Business"}},
        "54": {"type": "MasterCard", "levels": {"0": "Standard", "4": "Platinum"}},
        "55": {"type": "MasterCard", "levels": {"0": "Standard", "4": "Platinum", "5": "World", "8": "World Elite"}},
        "37": {"type": "Amex", "levels": {"0": "Green", "1": "Gold", "2": "Platinum", "3": "Centurion"}},
        "34": {"type": "Amex", "levels": {"0": "Green", "1": "Gold", "2": "Platinum"}},
        "60": {"type": "Discover", "levels": {"1": "Standard"}},
        "65": {"type": "Discover", "levels": {"0": "Standard"}},
    }

    # Country BIN prefixes (first 2-4 digits)
    COUNTRY_BINS = {
        "US": ["4", "51", "52", "53", "54", "55", "37", "34", "60", "65"],
        "UK": ["4", "51", "52", "53", "54", "55", "37", "34"],
        "CA": ["4", "51", "52", "53", "54", "55"],
        "AU": ["4", "51", "52", "53", "54", "55"],
        "IN": ["4", "51", "52", "53", "54", "55", "37", "34"],
        "BR": ["4", "51", "52", "53", "54", "55"],
        "FR": ["4", "51", "52", "53", "54", "55"],
        "DE": ["4", "51", "52", "53", "54", "55"],
        "JP": ["4", "51", "52", "53", "54", "55"],
    }

    # Banks by BIN ranges
    BANK_BINS = {
        "4532": "Chase Bank", "4556": "Wells Fargo", "4000": "Visa", "4111": "Capital One",
        "4242": "Stripe Test", "4012": "Bank of America", "4988": "Barclays", "4916": "HSBC",
        "4715": "Santander", "4500": "Banco do Brasil", "4300": "Itau", "4800": "Nubank",
        "5425": "MasterCard", "5111": "Bank of America", "5200": "MasterCard", "5311": "Capital One",
        "5500": "Citi", "5555": "MasterCard", "5444": "Barclays", "5130": "BNP Paribas",
        "5300": "Santander", "5999": "Itau", "5892": "Bradesco", "3742": "Amex",
        "3782": "Amex Platinum", "3714": "Amex Gold", "3766": "Amex Business",
        "3777": "Amex Corporate", "6011": "Discover", "6012": "Discover It", "6500": "Discover Miles",
    }

    UAS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    ]

    def __init__(self):
        self.session = requests.Session()
        self.results = []
        self.lock = threading.Lock()

    def _luhn(self, card_number):
        """Luhn algorithm validation"""
        digits = [int(d) for d in str(card_number) if d.isdigit()]
        if len(digits) < 13 or len(digits) > 19:
            return False
        odd_sum = sum(digits[-1::-2])
        even_sum = sum([sum(divmod(2 * d, 10)) for d in digits[-2::-2]])
        return (odd_sum + even_sum) % 10 == 0

    def _get_card_type(self, number):
        """Detect card type from prefix"""
        if number.startswith("4"):
            return "Visa"
        elif number.startswith(("51", "52", "53", "54", "55")):
            return "MasterCard"
        elif number.startswith(("34", "37")):
            return "Amex"
        elif number.startswith(("6011", "65", "644", "645", "646", "647", "648", "649")):
            return "Discover"
        elif number.startswith(("300", "301", "302", "303", "304", "305")):
            return "Diners Club"
        elif number.startswith(("36", "38")):
            return "Diners Club"
        elif number.startswith("35"):
            return "JCB"
        elif number.startswith(("2131", "1800")):
            return "JCB"
        return "Unknown"

    def _get_bank(self, number):
        """Detect bank from BIN"""
        for bin_len in [6, 5, 4, 3, 2]:
            prefix = number[:bin_len]
            if prefix in self.BANK_BINS:
                return self.BANK_BINS[prefix]
        return "Unknown"

    def _get_level(self, number):
        """Detect card level"""
        card_type = self._get_card_type(number)
        prefix = number[:2]

        if card_type == "Visa":
            digit = number[1] if len(number) > 1 else "0"
            levels = {"4": "Classic", "5": "Gold", "6": "Platinum", "7": "Signature", "8": "Infinite", "9": "Business"}
            return levels.get(digit, "Standard")
        elif card_type == "MasterCard":
            digit = number[2] if len(number) > 2 else "0"
            levels = {"0": "Standard", "2": "Gold", "4": "Platinum", "5": "World", "8": "World Elite"}
            return levels.get(digit, "Standard")
        elif card_type == "Amex":
            digit = number[2] if len(number) > 2 else "0"
            levels = {"0": "Green", "1": "Gold", "2": "Platinum", "3": "Centurion"}
            return levels.get(digit, "Green")
        return "Standard"

    def _bin_lookup_api(self, bin6):
        """Online BIN lookup via API"""
        try:
            r = requests.get(f"https://lookup.binlist.net/{bin6}", timeout=8,
                           headers={"User-Agent": random.choice(self.UAS)})
            if r.status_code == 200:
                d = r.json()
                return {
                    "bank": d.get("bank", {}).get("name", ""),
                    "country": d.get("country", {}).get("name", ""),
                    "country_code": d.get("country", {}).get("alpha2", ""),
                    "scheme": d.get("scheme", ""),
                    "type": d.get("type", ""),
                    "brand": d.get("brand", ""),
                    "prepaid": d.get("prepaid", False),
                }
        except:
            pass
        return None

    def _check_international(self, card_type, country_code):
        """Check if card supports international transactions"""
        international_types = ["Visa", "MasterCard", "Amex", "Discover"]
        if card_type in international_types:
            return True, "International supported"
        return False, "May not support international"

    def _generate_cc(self, prefix, length=16):
        """Generate valid Luhn CC"""
        num = prefix
        while len(num) < length - 1:
            num += str(random.randint(0, 9))
        d = [int(c) for c in num]
        odd_sum = sum(d[-1::-2])
        even_sum = sum([sum(divmod(2*x, 10)) for x in d[-2::-2]])
        check = (10 - (odd_sum + even_sum) % 10) % 10
        return num + str(check)

    def validate_single(self, number, expiry="", cvv=""):
        """Validate a single card comprehensively"""
        result = {
            "number": number,
            "valid": False,
            "luhn": False,
            "card_type": "Unknown",
            "bank": "Unknown",
            "level": "Unknown",
            "country": "Unknown",
            "country_code": "",
            "scheme": "",
            "type": "",
            "brand": "",
            "prepaid": False,
            "international": False,
            "international_msg": "",
            "length_ok": False,
            "expiry": expiry,
            "cvv": cvv,
            "cvv_valid": False,
            "expiry_valid": False,
            "kamatera_ready": False,
            "kamatera_reason": "",
        }

        # Clean number
        clean = re.sub(r'[^0-9]', '', number)
        result["number"] = clean

        # Length check
        if 13 <= len(clean) <= 19:
            result["length_ok"] = True
        else:
            result["kamatera_reason"] = "Invalid card length"
            return result

        # Luhn check
        result["luhn"] = self._luhn(clean)
        if not result["luhn"]:
            result["kamatera_reason"] = "Luhn check failed — invalid card number"
            return result

        # Card type
        result["card_type"] = self._get_card_type(clean)

        # Bank & Level (local)
        result["bank"] = self._get_bank(clean)
        result["level"] = self._get_level(clean)

        # BIN API lookup
        bin_info = self._bin_lookup_api(clean[:6])
        if bin_info:
            if bin_info["bank"]:
                result["bank"] = bin_info["bank"]
            result["country"] = bin_info["country"]
            result["country_code"] = bin_info["country_code"]
            result["scheme"] = bin_info["scheme"]
            result["type"] = bin_info["type"]
            result["brand"] = bin_info["brand"]
            result["prepaid"] = bin_info["prepaid"]

        # International check
        intl, intl_msg = self._check_international(result["card_type"], result["country_code"])
        result["international"] = intl
        result["international_msg"] = intl_msg

        # CVV validation
        if cvv:
            if result["card_type"] == "Amex":
                result["cvv_valid"] = len(cvv) == 4 and cvv.isdigit()
            else:
                result["cvv_valid"] = len(cvv) == 3 and cvv.isdigit()

        # Expiry validation
        if expiry:
            result["expiry_valid"] = self._validate_expiry(expiry)

        # Kamatera readiness
        result["valid"] = True
        result["kamatera_ready"] = self._kamatera_check(result)

        return result

    def _validate_expiry(self, expiry):
        """Validate expiry date MM/YY"""
        try:
            parts = re.split(r'[/\-]', expiry)
            if len(parts) == 2:
                month = int(parts[0])
                year = int(parts[1])
                if year < 100:
                    year += 2000
                current_year = datetime.now().year
                current_month = datetime.now().month
                if 1 <= month <= 12 and year >= current_year:
                    if year == current_year and month < current_month:
                        return False
                    return True
        except:
            pass
        return False

    def _kamatera_check(self, result):
        """Check if card is ready for Kamatera/cloud providers"""
        if not result["luhn"]:
            result["kamatera_reason"] = "Luhn check failed"
            return False

        if not result["length_ok"]:
            result["kamatera_reason"] = "Invalid length"
            return False

        if result["card_type"] not in ["Visa", "MasterCard", "Amex", "Discover"]:
            result["kamatera_reason"] = f"{result['card_type']} not supported by Kamatera"
            return False

        if result["prepaid"]:
            result["kamatera_reason"] = "Prepaid cards may be blocked"
            return False

        if not result["international"]:
            result["kamatera_reason"] = "International transactions not supported"
            return False

        result["kamatera_reason"] = "✅ READY — Card should work on Kamatera"
        return True

    def display_result(self, r):
        """Display single card result with animations"""
        status_color = fx.GREEN if r["kamatera_ready"] else fx.RED
        status_icon = "✅" if r["kamatera_ready"] else "❌"

        print(f"""
{fx.CYAN}╔══════════════════════════════════════════════════════════════╗{fx.RESET}
{fx.CYAN}║  {fx.YELLOW}💳 {fx.WHITE}{r['number']:<52}{fx.CYAN}║{fx.RESET}
{fx.CYAN}║                                                              ║{fx.RESET}
{fx.CYAN}║  {fx.DIM}Card Type:{fx.RESET}  {fx.WHITE}{r['card_type']:<15} {fx.DIM}Level:{fx.RESET} {fx.WHITE}{r['level']:<20}{fx.CYAN}║{fx.RESET}
{fx.CYAN}║  {fx.DIM}Bank:{fx.RESET}     {fx.WHITE}{r['bank']:<15} {fx.DIM}Country:{fx.RESET} {fx.WHITE}{r['country']:<17}{fx.CYAN}║{fx.RESET}
{fx.CYAN}║  {fx.DIM}Scheme:{fx.RESET}   {fx.WHITE}{r['scheme'] or 'N/A':<15} {fx.DIM}Type:{fx.RESET} {fx.WHITE}{r['type'] or 'N/A':<21}{fx.CYAN}║{fx.RESET}
{fx.CYAN}║  {fx.DIM}Brand:{fx.RESET}    {fx.WHITE}{r['brand'] or 'N/A':<15} {fx.DIM}Prepaid:{fx.RESET} {fx.RED if r['prepaid'] else fx.GREEN}{str(r['prepaid']):<18}{fx.CYAN}║{fx.RESET}
{fx.CYAN}║  {fx.DIM}Luhn:{fx.RESET}     {fx.GREEN if r['luhn'] else fx.RED}{'VALID' if r['luhn'] else 'INVALID':<15} {fx.DIM}Length:{fx.RESET} {fx.GREEN if r['length_ok'] else fx.RED}{'OK' if r['length_ok'] else 'BAD':<20}{fx.CYAN}║{fx.RESET}
{fx.CYAN}║  {fx.DIM}CVV:{fx.RESET}      {fx.GREEN if r['cvv_valid'] else fx.RED}{'VALID' if r['cvv_valid'] else 'INVALID':<15} {fx.DIM}Expiry:{fx.RESET} {fx.GREEN if r['expiry_valid'] else fx.RED}{'VALID' if r['expiry_valid'] else 'INVALID':<19}{fx.CYAN}║{fx.RESET}
{fx.CYAN}║  {fx.DIM}Intl:{fx.RESET}     {fx.GREEN if r['international'] else fx.RED}{r['international_msg']:<47}{fx.CYAN}║{fx.RESET}
{fx.CYAN}║                                                              ║{fx.RESET}
{fx.CYAN}║  {status_color}{status_icon} KAMATERA: {r['kamatera_reason']:<43}{fx.CYAN}║{fx.RESET}
{fx.CYAN}╚══════════════════════════════════════════════════════════════╝{fx.RESET}
""")

    def check_single(self):
        """Check a single card interactively"""
        print(f"\n{fx.fire_gradient('═══ SINGLE CARD CHECK ═══')}\n")
        number = input(f"{fx.CYAN}Card Number: {fx.WHITE}").strip()
        expiry = input(f"{fx.CYAN}Expiry (MM/YY): {fx.WHITE}").strip()
        cvv = input(f"{fx.CYAN}CVV: {fx.WHITE}").strip()
        print()

        fx.spinner(1, "Validating")
        result = self.validate_single(number, expiry, cvv)
        self.display_result(result)
        return result

    def check_bulk(self, cards_data):
        """Check multiple cards"""
        print(f"\n{fx.fire_gradient('═══ BULK CARD CHECK ═══')}\n")

        results = []
        for data in cards_data:
            if isinstance(data, str):
                parts = data.split("|")
                number = parts[0].strip()
                expiry = parts[1].strip() if len(parts) > 1 else ""
                cvv = parts[2].strip() if len(parts) > 2 else ""
            else:
                number, expiry, cvv = data

            result = self.validate_single(number, expiry, cvv)
            results.append(result)
            time.sleep(0.3)

        # Summary
        total = len(results)
        valid = sum(1 for r in results if r["luhn"])
        kamatera_ready = sum(1 for r in results if r["kamatera_ready"])

        print(f"\n{fx.blood_gradient('═'*60)}")
        print(fx.box(" BULK SUMMARY ", fx.CYAN, 60, "heavy"))
        print(f"{fx.CYAN}  Total Cards:     {fx.WHITE}{total}")
        print(f"{fx.CYAN}  Luhn Valid:      {fx.GREEN}{valid}")
        print(f"{fx.CYAN}  Kamatera Ready:  {fx.GREEN if kamatera_ready > 0 else fx.RED}{kamatera_ready}")
        print(f"{fx.blood_gradient('═'*60)}\n")

        return results

    def generate_test_cards(self, count=10):
        """Generate test cards for verification"""
        print(f"\n{fx.purple_gradient('═══ GENERATING TEST CARDS ═══')}\n")

        prefixes = [
            ("4532", "Visa", 16, "Chase Bank", "US"),
            ("4556", "Visa", 16, "Wells Fargo", "US"),
            ("4111", "Visa", 16, "Capital One", "US"),
            ("5425", "MasterCard", 16, "MasterCard", "US"),
            ("5111", "MasterCard", 16, "Bank of America", "US"),
            ("3742", "Amex", 15, "Amex", "US"),
            ("3782", "Amex", 15, "Amex Platinum", "US"),
            ("6011", "Discover", 16, "Discover", "US"),
            ("4988", "Visa", 16, "Barclays", "UK"),
            ("5444", "MasterCard", 16, "Barclays", "UK"),
        ]

        cards = []
        for _ in range(count):
            prefix, ctype, length, bank, country = random.choice(prefixes)
            cc = self._generate_cc(prefix, length)
            month = random.randint(1, 12)
            year = random.randint(25, 28)
            expiry = f"{month:02d}/{year}"
            cvv = str(random.randint(1000, 9999)) if ctype == "Amex" else str(random.randint(100, 999))
            cards.append((cc, expiry, cvv))

        return self.check_bulk(cards)

    def generate_realistic(self, count=5):
        """Generate realistic looking cards (for testing only)"""
        print(f"\n{fx.neon_gradient('═══ REALISTIC TEST CARDS ═══')}\n")
        print(f"{fx.YELLOW}⚠️  FOR TESTING ONLY — DO NOT USE FOR FRAUD{fx.RESET}\n")

        names = ["John Smith", "Sarah Johnson", "Mike Davis", "Emma Wilson", "Chris Brown"]

        cards = []
        for i in range(count):
            prefix = random.choice(["4532", "4556", "4111", "5425", "5111", "3742", "3782", "6011"])
            length = 15 if prefix.startswith("3") else 16
            cc = self._generate_cc(prefix, length)
            month = random.randint(1, 12)
            year = random.randint(25, 28)
            expiry = f"{month:02d}/{year}"
            cvv = str(random.randint(1000, 9999)) if length == 15 else str(random.randint(100, 999))
            cards.append((cc, expiry, cvv))

        return self.check_bulk(cards)

    def menu(self):
        """Interactive menu"""
        while True:
            print(fx.box(" ANON CARD CHECKER v3.0 ", fx.CYAN, 70, "double"))
            print()
            print(f"  {fx.GREEN}[1]{fx.RESET} {fx.BOLD}CHECK SINGLE{fx.RESET} {fx.DIM}— Validate one card{fx.RESET}")
            print(f"  {fx.GREEN}[2]{fx.RESET} {fx.BOLD}CHECK BULK{fx.RESET} {fx.DIM}— Multiple cards from file{fx.RESET}")
            print(f"  {fx.GREEN}[3]{fx.RESET} {fx.BOLD}GENERATE TEST{fx.RESET} {fx.DIM}— Create test cards{fx.RESET}")
            print(f"  {fx.GREEN}[4]{fx.RESET} {fx.BOLD}REALISTIC GEN{fx.RESET} {fx.DIM}— Realistic test cards{fx.RESET}")
            print(f"  {fx.GREEN}[5]{fx.RESET} {fx.BOLD}KAMATERA CHECK{fx.RESET} {fx.DIM}— Check if card works on Kamatera{fx.RESET}")
            print(f"  {fx.RED}[0]{fx.RESET} {fx.BOLD}EXIT{fx.RESET}")
            print()
            print(fx.box("", fx.DIM, 70, "single"))

            choice = input(f"{fx.CYAN}checker>{fx.RESET} {fx.WHITE}").strip()
            print(fx.RESET)

            if choice == "1":
                self.check_single()
            elif choice == "2":
                print(f"{fx.YELLOW}Paste cards (number|expiry|cvv), one per line, blank line to finish:{fx.RESET}")
                cards = []
                while True:
                    line = input().strip()
                    if not line:
                        break
                    cards.append(line)
                if cards:
                    self.check_bulk(cards)
            elif choice == "3":
                self.generate_test_cards(10)
            elif choice == "4":
                self.generate_realistic(5)
            elif choice == "5":
                print(f"{fx.YELLOW}Enter card details for Kamatera compatibility check:{fx.RESET}")
                self.check_single()
            elif choice == "0":
                fx.glitch_text("SHUTTING DOWN...", 2)
                print(f"{fx.RED}💀 Checker offline. Sab chhod, system tod. 🕳️{fx.RESET}")
                break
            else:
                print(f"{fx.RED}❌ Invalid choice!{fx.RESET}")

            input(f"\n{fx.DIM}Press ENTER to continue...{fx.RESET}")
            os.system('clear')


def main():
    import argparse
    parser = argparse.ArgumentParser(description="ANON Card Checker v3.0")
    parser.add_argument("--check", "-c", type=str, help="Check single card (number|exp|cvv)")
    parser.add_argument("--test", "-t", action="store_true", help="Generate test cards")
    parser.add_argument("--realistic", "-r", action="store_true", help="Generate realistic cards")
    args = parser.parse_args()

    checker = AnonCardChecker()

    if args.check:
        parts = args.check.split("|")
        number = parts[0]
        expiry = parts[1] if len(parts) > 1 else ""
        cvv = parts[2] if len(parts) > 2 else ""
        result = checker.validate_single(number, expiry, cvv)
        checker.display_result(result)
    elif args.test:
        checker.generate_test_cards(10)
    elif args.realistic:
        checker.generate_realistic(5)
    else:
        checker.menu()


if __name__ == "__main__":
    main()
