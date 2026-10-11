import re
import urllib.parse
from typing import Dict, List, Any

# Common phishing keywords categorized by vector
SUSPICIOUS_KEYWORDS = {
    "urgency": [
        "urgent", "immediately", "action required", "within 24 hours", "account suspended",
        "temporary suspension", "security compromise", "unauthorized access", "critical alert",
        "immediate attention", "time sensitive", "final warning", "lockout", "account termination",
        "deactivated", "quarantine"
    ],
    "credentials": [
        "verify your password", "confirm your identity", "reset password", "security update",
        "login credentials", "re-verify", "update billing", "signon", "unlock your account",
        "seed phrase", "private key", "ssn", "social security"
    ],
    "financial": [
        "wire transfer", "payment failed", "refund pending", "tax recalculation", "bonus payout",
        "lottery", "cash prize", "crypto airdrop", "unauthorized transaction", "zelle payment",
        "customs fee", "unpaid invoice", "bitcoin", "usdt", "wallet"
    ],
    "impersonation": [
        "paypal", "apple id", "microsoft 365", "office 365", "netflix", "bank of america",
        "wells fargo", "chase bank", "dhl express", "fedex tracking", "metamask", "coinbase"
    ]
}

SUSPICIOUS_TLDS = {
    ".xyz", ".top", ".tk", ".buzz", ".cc", ".info", ".club", ".icu",
    ".gq", ".ga", ".cf", ".ml", ".work", ".click", ".link", ".rest"
}

URL_SHORTENERS = {
    "bit.ly", "tinyurl.com", "t.co", "is.gd", "buff.ly", "ow.ly", "cutt.ly"
}

URL_PATTERN = re.compile(
    r'(?:(?:https?|ftp):\/\/|www\.)[^\s/$.?#].[^\s]*',
    re.IGNORECASE
)

IP_DOMAIN_PATTERN = re.compile(
    r'https?:\/\/(?:\d{1,3}\.){3}\d{1,3}(?::\d+)?(?:[/?#]|$)'
)

def extract_urls(text: str) -> List[str]:
    """Extract all URLs from a text string."""
    if not text:
        return []
    urls = URL_PATTERN.findall(text)
    # Clean trailing punctuation often caught by regex
    cleaned_urls = []
    for url in urls:
        u = url.rstrip('.,;:)!?"\'')
        if not u.startswith(('http://', 'https://')):
            u = 'http://' + u
        cleaned_urls.append(u)
    return list(set(cleaned_urls))

def analyze_url(url: str) -> Dict[str, Any]:
    """Analyze a single URL for phishing indicators."""
    indicators = []
    risk = 0
    parsed = urllib.parse.urlparse(url)
    hostname = (parsed.hostname or "").lower()

    # 1. IP address instead of domain name
    if IP_DOMAIN_PATTERN.match(url):
        indicators.append("URL uses raw IP address instead of domain")
        risk += 30

    # 2. Suspicious TLD
    for tld in SUSPICIOUS_TLDS:
        if hostname.endswith(tld):
            indicators.append(f"Suspicious high-risk TLD ({tld})")
            risk += 20
            break

    # 3. URL Shortener used to conceal destination
    if hostname in URL_SHORTENERS:
        indicators.append("URL shortener used to conceal final destination")
        risk += 15

    # 4. Brand spoofing / lookalike domain in hostname
    spoofed_brands = ["paypal", "paypa1", "m1crosoft", "micro-soft", "appleid", "wellsfargo", "bofa", "chase", "netflix", "coinbase", "binance", "docusign"]
    for brand in spoofed_brands:
        if brand in hostname:
            legit_domains = [f"{brand}.com", f"www.{brand}.com"]
            if not any(hostname == ld or hostname.endswith('.' + ld) for ld in legit_domains):
                indicators.append(f"Possible brand impersonation in URL host ({brand})")
                risk += 25
                break

    # 5. Excessive subdomains
    parts = hostname.split('.')
    if len(parts) > 4:
        indicators.append("Excessive subdomains (subdomain obfuscation)")
        risk += 10

    # 6. Sensitive keywords in URL path
    sensitive_path_keywords = ["login", "verify", "secure", "auth", "signin", "update", "portal", "account", "wallet", "recover"]
    matched_paths = [kw for kw in sensitive_path_keywords if kw in parsed.path.lower()]
    if matched_paths and risk > 0:
        indicators.append(f"Credential harvesting path detected: {', '.join(matched_paths)}")
        risk += 10

    return {
        "url": url,
        "hostname": hostname,
        "risk_score": min(100, risk),
        "is_suspicious": risk >= 20,
        "indicators": indicators
    }

def extract_heuristic_features(subject: str, sender: str, body: str) -> Dict[str, Any]:
    """Extract rule-based threat signals across subject, sender, and body."""
    combined_text = f"{subject} {body}".lower()
    detected_flags: List[str] = []
    keyword_matches: Dict[str, List[str]] = {}
    heuristic_score = 0

    # 1. Keyword analysis
    for category, kws in SUSPICIOUS_KEYWORDS.items():
        found = [kw for kw in kws if kw in combined_text]
        if found:
            keyword_matches[category] = found
            if category == "urgency":
                detected_flags.append(f"Urgency tactics detected: {', '.join(found[:3])}")
                heuristic_score += 15
            elif category == "credentials":
                detected_flags.append(f"Credential request keywords: {', '.join(found[:3])}")
                heuristic_score += 20
            elif category == "financial":
                detected_flags.append(f"Financial lure keywords: {', '.join(found[:3])}")
                heuristic_score += 15
            elif category == "impersonation":
                heuristic_score += 10

    # 2. Sender spoofing check
    sender_lower = (sender or "").lower()
    # Check for lookalike characters or brand names in sender
    brand_keywords = ["paypal", "microsoft", "apple", "netflix", "bofa", "chase", "google", "amazon", "dhl", "fedex", "binance", "coinbase"]
    for brand in brand_keywords:
        if brand in sender_lower:
            # If sender has brand name in display or username but not the actual legit domain
            if not re.search(rf'@{brand}\.(?:com|org|net|us)$', sender_lower):
                detected_flags.append(f"Sender domain mismatch: claims {brand.capitalize()} but email is '{sender}'")
                heuristic_score += 25
                break

    for tld in SUSPICIOUS_TLDS:
        if sender_lower.endswith(tld) or f"{tld}>" in sender_lower:
            detected_flags.append(f"Sender email utilizes high-risk TLD ({tld})")
            heuristic_score += 15
            break

    # 3. URL inspections
    extracted_urls = extract_urls(body)
    url_analyses = [analyze_url(u) for u in extracted_urls]
    suspicious_urls = [u for u in url_analyses if u["is_suspicious"]]

    if suspicious_urls:
        heuristic_score += min(35, len(suspicious_urls) * 20)
        for s_url in suspicious_urls[:3]:
            for ind in s_url["indicators"]:
                if ind not in detected_flags:
                    detected_flags.append(ind)

    return {
        "heuristic_score": min(100, heuristic_score),
        "detected_flags": detected_flags,
        "keyword_matches": keyword_matches,
        "extracted_urls": extracted_urls,
        "url_analyses": url_analyses,
        "suspicious_url_count": len(suspicious_urls)
    }
