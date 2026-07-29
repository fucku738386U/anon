
# ANON Site Configurations — Pre-loaded & Ready

SITES = {
    "reddit_dumps": {
        "name": "anon-reddit-dumps",
        "base_url": "https://www.reddit.com",
        "subreddits": [
            "r/CreditCards", "r/CreditCardTips", "r/CreditCardHacks",
            "r/Carding", "r/DarkWeb", "r/Scamming", "r/Fraud",
            "r/CreditCardFraud", "r/BlackHatSEO", "r/IllegalLifeProTips",
        ],
        "search_queries": ["cc dump", "credit card dump", "card number", "cvv", "fullz", "bin", "track 1", "track 2"],
        "patterns": {
            "cc_number": r"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|3(?:0[0-5]|[68][0-9])[0-9]{11}|6(?:011|5[0-9]{2})[0-9]{12}|(?:2131|1800|35\d{3})\d{11})\b",
            "expiry": r"\b(0[1-9]|1[0-2])[\/\-\|\s](20)?[0-9]{2}\b",
            "cvv": r"\b[0-9]{3,4}\b",
        },
        "rate_limit": 2.0, "type": "reddit"
    },
    "reddit_paste": {
        "name": "anon-reddit-paste",
        "base_url": "https://www.reddit.com",
        "subreddits": ["r/pastebin", "r/leaked", "r/databreach", "r/hacked"],
        "search_queries": ["pastebin.com", "ghostbin", "zerobin", "privatebin", "cc list", "combo list"],
        "patterns": {
            "pastebin_url": r"pastebin\.com\/\w+",
            "ghostbin_url": r"ghostbin\.co\/\w+",
            "cc_number": r"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14})\b",
        },
        "rate_limit": 3.0, "type": "reddit_paste"
    },
    "reddit_market": {
        "name": "anon-reddit-market",
        "base_url": "https://www.reddit.com",
        "subreddits": ["r/shopify", "r/ecommerce", "r/dropship", "r/beermoney"],
        "search_queries": ["carding", "method", "tutorial", "guide"],
        "patterns": {
            "cc_number": r"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14})\b",
            "contact": r"\b[Tt]elegram[:\s@]+\w+|\b[Ww]ickr[:\s@]+\w+",
        },
        "rate_limit": 2.5, "type": "reddit_market"
    },
    "reddit_crypto": {
        "name": "anon-reddit-crypto",
        "base_url": "https://www.reddit.com",
        "subreddits": ["r/Bitcoin", "r/CryptoCurrency", "r/Monero", "r/darknet"],
        "search_queries": ["cc to btc", "carding crypto", "exchange", "method"],
        "patterns": {
            "cc_number": r"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14})\b",
            "btc_address": r"\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\b|\bbc1[a-z0-9]{39,59}\b",
        },
        "rate_limit": 2.0, "type": "reddit_crypto"
    },
    "pastebin_direct": {
        "name": "anon-pastebin",
        "base_url": "https://pastebin.com",
        "urls": ["/archive"],
        "search_queries": ["cc", "card", "cvv", "dump"],
        "patterns": {"cc_number": r"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14})\b"},
        "rate_limit": 1.5, "type": "pastebin"
    },
    "ghostbin_direct": {
        "name": "anon-ghostbin",
        "base_url": "https://ghostbin.co",
        "urls": ["/"],
        "search_queries": ["cc", "card"],
        "patterns": {"cc_number": r"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14})\b"},
        "rate_limit": 2.0, "type": "ghostbin"
    },
}

def get_all_sites(): return SITES
def get_site_ids(): return list(SITES.keys())
def get_site(sid): return SITES.get(sid)
