import re
import urllib.parse
import email.utils
from typing import Dict, List, Any, Tuple

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

# Recognized legitimate root domains for major protected brands (including official subdomains and regional domains)
KNOWN_BRAND_DOMAINS = {
    "paypal": ["paypal.com", "paypal.co.uk", "paypal-communication.com", "paypal.ca", "paypal.de"],
    "microsoft": ["microsoft.com", "microsoftonline.com", "office.com", "office365.com", "live.com", "outlook.com", "hotmail.com", "azure.com", "accountprotection.microsoft.com", "microsoft.net"],
    "apple": ["apple.com", "icloud.com", "appleid.apple.com", "me.com", "mac.com"],
    "google": ["google.com", "google.co.uk", "google.ca", "google.de", "google.co.in", "youtube.com", "abc.xyz", "gmail.com"],
    "amazon": ["amazon.com", "amazon.co.uk", "amazon.de", "amazon.in", "amazon.ca", "amazon.fr", "amazon.es", "amazon.it", "amazon.co.jp", "aws.amazon.com"],
    "netflix": ["netflix.com", "netflix.net"],
    "chase": ["chase.com", "jpmorganchase.com", "jpmorgan.com"],
    "bofa": ["bankofamerica.com", "bofa.com"],
    "wellsfargo": ["wellsfargo.com"],
    "dhl": ["dhl.com", "dhl.de", "dhl-usa.com"],
    "fedex": ["fedex.com"],
    "binance": ["binance.com", "binance.us", "binance.org"],
    "coinbase": ["coinbase.com"],
    "docusign": ["docusign.com", "docusign.net"],
    "stripe": ["stripe.com"],
    "slack": ["slack.com"],
    "github": ["github.com"],
    "notion": ["notion.so"],
    "zoom": ["zoom.us"],
    "dropbox": ["dropbox.com"],
    "adobe": ["adobe.com"],
    "steam": ["steampowered.com", "steamcommunity.com"],
    "uber": ["uber.com"],
    "airbnb": ["airbnb.com"],
    "spotify": ["spotify.com"]
}

# Major brands and common lookalike typo-squat patterns
SPOOFED_BRANDS = [
    ("paypal", ["paypa1", "pay-pal", "paypal-security", "paypal-update", "paypal-verify"]),
    ("microsoft", ["m1crosoft", "micro-soft", "microsoft365", "office365-verify"]),
    ("apple", ["appleid", "apple-verify", "apple-support-login"]),
    ("amazon", ["arnazon", "amazon-security", "amazon-order-dispute"]),
    ("netflix", ["netflx", "netflix-verify", "netflix-card", "netflix-account"]),
    ("wellsfargo", ["wells-fargo", "wellsfargo-verify"]),
    ("bofa", ["bankofamerica-verify", "bofa-security"]),
    ("chase", ["chase-security", "chase-fraud"]),
    ("coinbase", ["coinbase-verify", "coinbase-cancel"]),
    ("binance", ["binance-reward", "binance-claim"]),
    ("docusign", ["docusign-docs", "docusign-secure"]),
    ("google", ["goog1e", "google-security", "google-verify"]),
    ("dhl", ["dhl-express-reschedule", "dhl-delivery-update"]),
    ("fedex", ["fedx", "fedex-delivery-notice"])
]

URL_PATTERN = re.compile(
    r'(?:(?:https?|ftp):\/\/|www\.)[^\s/$.?#].[^\s]*',
    re.IGNORECASE
)

IP_DOMAIN_PATTERN = re.compile(
    r'https?:\/\/(?:\d{1,3}\.){3}\d{1,3}(?::\d+)?(?:[/?#]|$)'
)

def is_legitimate_brand_domain(domain_or_host: str, brand: str) -> bool:
    """Return True if domain_or_host authentically belongs to the brand."""
    if not domain_or_host:
        return False
    host = domain_or_host.lower().strip()
    # Normalize by stripping port if present
    if ":" in host:
        host = host.split(":")[0]
    allowed_list = KNOWN_BRAND_DOMAINS.get(brand.lower(), [f"{brand}.com"])
    for ld in allowed_list:
        if host == ld or host.endswith("." + ld):
            return True
    return False

def extract_urls(text: str) -> List[str]:
    """Extract all URLs from a text string."""
    if not text:
        return []
    urls = URL_PATTERN.findall(text)
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
    try:
        parsed = urllib.parse.urlparse(url)
        hostname = (parsed.hostname or "").lower()
    except Exception:
        hostname = ""

    # 1. IP address instead of domain name
    if IP_DOMAIN_PATTERN.match(url):
        indicators.append("URL uses raw IP address instead of domain")
        risk += 35

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
    # Checks for typo-squats or unauthorized brand naming
    for brand_key, typos in SPOOFED_BRANDS:
        # Check if the hostname claims the brand
        claims_brand = (brand_key in hostname) or any(t in hostname for t in typos)
        if claims_brand:
            if not is_legitimate_brand_domain(hostname, brand_key):
                indicators.append(f"Possible brand impersonation in URL host ({brand_key})")
                risk += 30
                break

    # 5. Excessive subdomains (subdomain obfuscation)
    parts = hostname.split('.')
    if len(parts) > 4 and not is_legitimate_brand_domain(hostname, "google") and not is_legitimate_brand_domain(hostname, "microsoft"):
        indicators.append("Excessive subdomains (subdomain obfuscation)")
        risk += 10

    # 6. Sensitive keywords in URL path (only penalized if host already has risk)
    if risk > 0:
        sensitive_path_keywords = ["login", "verify", "secure", "auth", "signin", "update", "wallet", "seed", "ssn"]
        try:
            path_lower = parsed.path.lower()
            matched_paths = [kw for kw in sensitive_path_keywords if kw in path_lower]
            if matched_paths:
                indicators.append(f"Credential harvesting path detected: {', '.join(matched_paths)}")
                risk += 10
        except Exception:
            pass

    return {
        "url": url,
        "hostname": hostname,
        "risk_score": min(100, risk),
        "is_suspicious": risk >= 20,
        "indicators": indicators
    }

def extract_heuristic_features(subject: str, sender: str, body: str) -> Dict[str, Any]:
    """Extract rule-based threat signals across subject, sender, and body with calibrated weights."""
    subject = subject or ""
    sender = sender or ""
    body = body or ""
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
                # Only flag urgency if multiple words or strong phrase
                detected_flags.append(f"Urgency tactics detected: {', '.join(found[:3])}")
                heuristic_score += 15
            elif category == "credentials":
                detected_flags.append(f"Credential request keywords: {', '.join(found[:3])}")
                heuristic_score += 20
            elif category == "financial":
                heuristic_score += 10
                high_risk_fin = [kw for kw in found if kw in ["wire transfer", "zelle payment", "crypto airdrop", "bitcoin", "usdt", "lottery", "cash prize"]]
                if high_risk_fin:
                    detected_flags.append(f"High-risk financial demand: {', '.join(high_risk_fin[:3])}")
                    heuristic_score += 15
            elif category == "impersonation":
                heuristic_score += 5

    # Combined BEC (Business Email Compromise) / Executive Fraud indicator
    if "urgency" in keyword_matches and "financial" in keyword_matches:
        detected_flags.append("Urgent financial transfer demand (BEC / Executive fraud indicator)")
        heuristic_score += 15

    # 2. Sender spoofing check (using RFC 5322 address parsing)
    sender_name, sender_email = email.utils.parseaddr(sender)
    sender_lower = sender.lower()
    email_lower = (sender_email or sender).lower()
    domain_part = email_lower.split("@")[-1] if "@" in email_lower else email_lower

    # Check major brand impersonation and typo-squatting in sender
    for brand, typos in SPOOFED_BRANDS:
        # Check if the display name or the email domain invokes the brand or its lookalike typos
        claims_brand = (
            (brand in sender_name.lower()) or 
            (brand in domain_part) or 
            any(t in domain_part for t in typos)
        )
        if claims_brand:
            # Check if domain authentically belongs to this brand
            if not is_legitimate_brand_domain(domain_part, brand):
                detected_flags.append(f"Sender domain mismatch: claims {brand.capitalize()} but email is '{sender}'")
                heuristic_score += 30
                break

    # Check suspicious sender TLD
    for tld in SUSPICIOUS_TLDS:
        if domain_part.endswith(tld):
            detected_flags.append(f"Sender email utilizes high-risk TLD ({tld})")
            heuristic_score += 20
            break

    # 3. URL inspections
    extracted_urls = extract_urls(body)
    url_analyses = [analyze_url(u) for u in extracted_urls]
    suspicious_urls = [u for u in url_analyses if u["is_suspicious"]]

    if suspicious_urls:
        heuristic_score += min(40, len(suspicious_urls) * 20)
        for s_url in suspicious_urls[:3]:
            for ind in s_url["indicators"]:
                if ind not in detected_flags:
                    detected_flags.append(ind)

    # Co-occurrence synergy (e.g. urgency + credential request is a classic phishing indicator)
    if "urgency" in keyword_matches and "credentials" in keyword_matches:
        heuristic_score += 15

    return {
        "heuristic_score": min(100, heuristic_score),
        "detected_flags": detected_flags,
        "keyword_matches": keyword_matches,
        "extracted_urls": extracted_urls,
        "url_analyses": url_analyses,
        "suspicious_url_count": len(suspicious_urls)
    }

def preprocess_email_text(subject: str = "", sender: str = "", body: str = "") -> str:
    """
    Standardized Text Preprocessor for both Training and Inference.
    - Preserves structural tokens (URLs, raw IPs, domain extensions).
    - Normalizes raw IP addresses to TOKEN_RAW_IP.
    - Normalizes URLs to TOKEN_URL while preserving the domain tokens.
    - Extracts sender domain and combines subject, sender, and body cleanly.
    """
    subject = str(subject or "").strip()
    sender = str(sender or "").strip()
    body = str(body or "").strip()

    # Extract sender display and domain
    _, sender_email = email.utils.parseaddr(sender)
    sender_domain = sender_email.split("@")[-1] if "@" in sender_email else sender

    combined = f"{subject} {sender} {sender_domain} {body}"

    # Normalize raw IP addresses
    combined = IP_DOMAIN_PATTERN.sub(" token_raw_ip ", combined)

    # Normalize standard URLs but keep the domain token
    def _url_token_repl(match):
        u = match.group(0)
        try:
            parsed = urllib.parse.urlparse(u)
            host = parsed.hostname or ""
            return f" token_url {host} "
        except Exception:
            return " token_url "

    combined = URL_PATTERN.sub(_url_token_repl, combined)

    # Normalize excessive punctuation and whitespace
    combined = re.sub(r"[\r\n\t]+", " ", combined)
    combined = re.sub(r"\s+", " ", combined)

    return combined.strip().lower()

__all__ = [
    "extract_urls",
    "analyze_url",
    "extract_heuristic_features",
    "preprocess_email_text",
    "is_legitimate_brand_domain",
    "SUSPICIOUS_KEYWORDS",
    "SUSPICIOUS_TLDS",
    "URL_SHORTENERS",
    "KNOWN_BRAND_DOMAINS"
]
