import base64
import email
from email import policy
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

logger = logging.getLogger("app.gmail")

def decode_base64_payload(data_str: str) -> str:
    """Safely decode base64url encoded Gmail message bodies."""
    if not data_str:
        return ""
    try:
        clean_str = data_str.replace('-', '+').replace('_', '/')
        # Add padding if needed
        padding = len(clean_str) % 4
        if padding > 0:
            clean_str += '=' * (4 - padding)
        decoded_bytes = base64.b64decode(clean_str)
        return decoded_bytes.decode('utf-8', errors='replace')
    except Exception as e:
        logger.warning(f"Error decoding base64 payload: {e}")
        return ""

def extract_body_from_parts(payload: Dict[str, Any]) -> Dict[str, str]:
    """Recursively extract plain text and HTML from MIME parts."""
    plain_text = ""
    html_text = ""

    mime_type = payload.get("mimeType", "")
    body = payload.get("body", {})
    data = body.get("data", "")

    if data:
        decoded = decode_base64_payload(data)
        if "text/plain" in mime_type:
            plain_text += decoded
        elif "text/html" in mime_type:
            html_text += decoded

    parts = payload.get("parts", [])
    for part in parts:
        nested = extract_body_from_parts(part)
        if nested["plain"]:
            plain_text += "\n" + nested["plain"]
        if nested["html"]:
            html_text += "\n" + nested["html"]

    return {"plain": plain_text.strip(), "html": html_text.strip()}

class GmailService:
    def __init__(self):
        pass

    def fetch_live_emails(self, access_token: str, refresh_token: Optional[str] = None, max_results: int = 15) -> List[Dict[str, Any]]:
        """Fetch recent emails using Google OAuth 2.0 Credentials and Gmail API."""
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build
        from app.core.config import settings

        creds = Credentials(
            token=access_token,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
            scopes=["https://www.googleapis.com/auth/gmail.readonly"]
        )

        if creds.expired and creds.refresh_token:
            creds.refresh(Request())

        service = build("gmail", "v1", credentials=creds)
        # Fetch list of recent messages
        results = service.users().messages().list(userId="me", maxResults=max_results).execute()
        messages = results.get("messages", [])

        email_items = []
        for msg in messages:
            try:
                full_msg = service.users().messages().get(userId="me", id=msg["id"], format="full").execute()
                payload = full_msg.get("payload", {})
                headers = payload.get("headers", [])

                header_dict = {h["name"].lower(): h["value"] for h in headers}
                subject = header_dict.get("subject", "(No Subject)")
                sender = header_dict.get("from", "Unknown Sender")
                recipient = header_dict.get("to", "")
                date_str = header_dict.get("date", datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT"))

                body_info = extract_body_from_parts(payload)
                snippet = full_msg.get("snippet", "")

                email_items.append({
                    "id": full_msg.get("id") or str(uuid.uuid4()),
                    "message_id": full_msg.get("id"),
                    "subject": subject,
                    "sender": sender,
                    "recipient": recipient,
                    "date": date_str,
                    "snippet": snippet,
                    "body_plain": body_info["plain"] or snippet,
                    "body_html": body_info["html"] or None
                })
            except Exception as e:
                logger.error(f"Error fetching individual email {msg.get('id')}: {e}")

        return email_items

    def get_sample_demo_emails(self) -> List[Dict[str, Any]]:
        """High-fidelity demo emails representing Safe, Suspicious, and Phishing categories for immediate testing."""
        return [
            {
                "id": "demo-phish-01",
                "message_id": "msg-phish-001",
                "subject": "URGENT: Your PayPal Account Has Been Suspended",
                "sender": "security-alert@paypa1-support.com",
                "recipient": "user@gmail.com",
                "date": datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT"),
                "snippet": "Dear Customer, We have detected unauthorized activity on your PayPal account. Please click here to verify...",
                "body_plain": "Dear Customer,\n\nWe have detected unauthorized activity on your PayPal account. Your account has been temporarily suspended for your security.\n\nPlease click here to verify your identity immediately: http://192.168.1.100/verify-paypal\n\nFailure to do so within 24 hours will result in permanent account termination.\n\nSincerely,\nPayPal Security Team",
                "body_html": "<p>Dear Customer,</p><p>We have detected unauthorized activity on your <b>PayPal account</b>. Your account has been temporarily suspended for your security.</p><p><a href='http://192.168.1.100/verify-paypal' style='background-color:#0070ba;color:white;padding:10px 20px;text-decoration:none;'>Verify Identity Immediately</a></p><p>Failure to do so within 24 hours will result in permanent account termination.</p>"
            },
            {
                "id": "demo-safe-01",
                "message_id": "msg-safe-001",
                "subject": "Google Cloud Platform: Monthly invoice available",
                "sender": "cloud-noreply@google.com",
                "recipient": "user@gmail.com",
                "date": datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT"),
                "snippet": "Hello, Your Google Cloud Platform invoice for last month is now ready to view. Total amount billed: $14.20...",
                "body_plain": "Hello,\n\nYour Google Cloud Platform invoice for last month is now ready to view. Total amount billed: $14.20.\n\nYou can download your PDF invoice from the Google Cloud Console billing section: https://console.cloud.google.com/billing\n\nThank you for choosing Google Cloud.",
                "body_html": "<p>Hello,</p><p>Your <b>Google Cloud Platform</b> invoice for last month is now ready to view. Total amount billed: <b>$14.20</b>.</p><p><a href='https://console.cloud.google.com/billing'>Download PDF Invoice</a></p>"
            },
            {
                "id": "demo-phish-02",
                "message_id": "msg-phish-002",
                "subject": "Immediate Action Required: Wire Transfer Verification",
                "sender": "cfo-office@executive-funds.top",
                "recipient": "user@gmail.com",
                "date": datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT"),
                "snippet": "Greetings, I am currently in a closed-door board meeting and need an urgent wire transfer of $45,200...",
                "body_plain": "Greetings,\n\nI am currently in a closed-door board meeting and need an urgent wire transfer of $45,200 processed to our new supplier before 3 PM today.\n\nPlease find the wire details and invoice here: http://bit.ly/wire-transfer-doc2026\n\nDo not call me as I cannot take calls right now. Confirm once executed.\n\nChief Financial Officer",
                "body_html": "<p>Greetings,</p><p>I am currently in a closed-door board meeting and need an urgent wire transfer of <b>$45,200</b> processed before 3 PM today.</p><p><a href='http://bit.ly/wire-transfer-doc2026'>Review Wire Instructions (DocuSign)</a></p>"
            },
            {
                "id": "demo-suspicious-01",
                "message_id": "msg-susp-001",
                "subject": "Survey: Please update your contact details for HR records",
                "sender": "hr-updates@external-survey-portal.xyz",
                "recipient": "user@gmail.com",
                "date": datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT"),
                "snippet": "Hello, kindly verify your home address and emergency contact info for the quarterly HR database update...",
                "body_plain": "Hello,\n\nPlease verify your home address, emergency phone, and direct deposit confirmation at: http://survey-benefits-portal.xyz/login\n\nThank you,\nHR Support",
                "body_html": "<p>Hello,</p><p>Please update your employee record at <a href='http://survey-benefits-portal.xyz/login'>Internal HR Portal</a>.</p>"
            },
            {
                "id": "demo-safe-02",
                "message_id": "msg-safe-002",
                "subject": "Your Amazon order #402-9821381 has shipped",
                "sender": "shipment-tracking@amazon.com",
                "recipient": "user@gmail.com",
                "date": datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT"),
                "snippet": "Hello, Good news! Your package is on its way. Estimated delivery date: Tomorrow by 8 PM...",
                "body_plain": "Hello,\n\nGood news! Your package is on its way.\n\nEstimated delivery date: Tomorrow by 8 PM.\n\nYou can track your package status on your Amazon account dashboard anytime: https://www.amazon.com/gp/css/order-history\n\nThank you for shopping with us.",
                "body_html": "<p>Hello,</p><p>Your package has shipped! <a href='https://www.amazon.com/gp/css/order-history'>Track your package</a>.</p>"
            },
            {
                "id": "demo-phish-03",
                "message_id": "msg-phish-003",
                "subject": "Alert: Unusual sign-in attempt detected on your Microsoft 365",
                "sender": "support@m1crosoft-office365-verify.com",
                "recipient": "user@gmail.com",
                "date": datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT"),
                "snippet": "Security Alert: We blocked a suspicious login attempt to your Microsoft 365 account from Moscow, Russia...",
                "body_plain": "Security Alert:\n\nWe blocked a suspicious login attempt to your Microsoft 365 account from IP address 185.220.101.5 in Moscow, Russia.\n\nIf this was not you, confirm your credentials immediately to avoid mailbox lockout: http://login-microsoft365-secure.xyz/auth\n\nMicrosoft Security Center",
                "body_html": "<p>Security Alert: Blocked sign-in attempt from Russia.</p><p><a href='http://login-microsoft365-secure.xyz/auth'>Unlock Mailbox</a></p>"
            }
        ]

gmail_service = GmailService()
