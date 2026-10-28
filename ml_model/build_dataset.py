import os
import sys
import csv
import random
import re
from typing import List, Dict, Any

csv.field_size_limit(10 * 1024 * 1024)

# Set seeds for reproducibility
RANDOM_SEED = 42
random.seed(RANDOM_SEED)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(BASE_DIR, "dataset")
RAW_CEAS_PATH = os.path.join(DATASET_DIR, "raw_ceas_08.csv")
MASTER_CSV_PATH = os.path.join(DATASET_DIR, "phishing_dataset.csv")
SPLITS_DIR = os.path.join(DATASET_DIR, "splits")
os.makedirs(SPLITS_DIR, exist_ok=True)

# 1. Cleaned and formatted baseline samples (fixing the CSV unquoted comma bugs)
CURATED_MODERN_SAMPLES = [
    # Phishing (label 1)
    {
        "label": 1,
        "subject": "URGENT: Your PayPal Account Has Been Suspended",
        "sender": "security-alert@paypa1-support.com",
        "body": "Dear Customer, We have detected unauthorized activity on your PayPal account. Your account has been temporarily suspended for your security. Please click here to verify your identity immediately: http://192.168.1.100/verify-paypal. Failure to do so within 24 hours will result in permanent account termination."
    },
    {
        "label": 1,
        "subject": "Immediate Action Required: Wire Transfer Verification",
        "sender": "cfo-office@executive-funds.top",
        "body": "Greetings, I am currently in a closed-door board meeting and need an urgent wire transfer of $45,200 processed to our new supplier before 3 PM today. Please find the wire details here: http://bit.ly/wire-transfer-doc2026. Do not call me as I cannot take calls right now."
    },
    {
        "label": 1,
        "subject": "Alert: Unusual sign-in attempt detected on your Microsoft 365",
        "sender": "support@m1crosoft-office365-verify.com",
        "body": "Security Alert: We blocked a suspicious login attempt to your Microsoft 365 account from IP address 185.220.101.5 in Moscow, Russia. If this was not you, confirm your credentials immediately to avoid mailbox lockout: http://login-microsoft365-secure.xyz/auth."
    },
    {
        "label": 1,
        "subject": "Congratulations! You won $1,500,000 in the International Lottery",
        "sender": "claims@winner-lottery-promo.buzz",
        "body": "Dear Lucky Winner, Your email address was chosen among 50,000 participants in the global Mega Millions Draw. To claim your cash prize of $1,500,000 USD, send your full name, bank account number, and SSN to claims@winner-lottery-promo.buzz or claim online: http://mega-jackpot-winner.tk/claim."
    },
    {
        "label": 1,
        "subject": "CRITICAL: Netflix Membership Cancellation Notice",
        "sender": "billing@netflx-account-renew.info",
        "body": "We were unable to validate your monthly billing details for Netflix. Your subscription will be cancelled within 48 hours unless you update your credit card information. Click the link below to verify your payment method: http://update-netflix-card.cc/login."
    },
    {
        "label": 1,
        "subject": "IRS Tax Refund Pending - Claim $850.00",
        "sender": "refunds@irs-tax-gov-portal.com",
        "body": "Internal Revenue Service Notification: After the latest annual tax recalculation, you are eligible for an outstanding tax refund of $850.00. Please submit the tax refund claim form with your debit card details: http://194.26.29.11/irs-refund."
    },
    {
        "label": 1,
        "subject": "Security Notification: Your Apple ID is locked",
        "sender": "appleid@secure-icloud-login.net",
        "body": "Dear Apple Customer, Your Apple ID has been locked due to multiple failed password attempts. You must unlock your Apple account within 12 hours to prevent data wipe: http://appleid-unlock-support.top/verify. Apple Support Team."
    },
    {
        "label": 1,
        "subject": "HR Department: Mandatory Employee Salary & Benefit Survey",
        "sender": "hr-department@internal-staff-portal.xyz",
        "body": "Dear Employee, Please complete the mandatory 2026 Compensation and Benefits Survey before end of day. Failure to complete will impact your upcoming quarterly bonus payout. Access the internal portal: http://survey-benefits-portal.xyz/login."
    },
    {
        "label": 1,
        "subject": "Bank of America: Security Compromise Detected",
        "sender": "alerts@bofa-security-service.com",
        "body": "Dear Valued Client, We detected unauthorized transactions on your debit card. We have placed a temporary freeze on your checking account. To restore full access, enter your online banking credentials here: http://bofa-customer-verify.com/signon."
    },
    {
        "label": 1,
        "subject": "FedEx Delivery Notice: Package held at distribution depot",
        "sender": "tracking@fedx-parcels-express.com",
        "body": "Your FedEx package with tracking number FX-92819230 could not be delivered due to an incorrect delivery address and an unpaid customs fee of $2.99. Pay the customs fee and reschedule delivery: http://fedx-package-release.info/track."
    },
    {
        "label": 1,
        "subject": "Warning: Mailbox Quota Exceeded - Incoming Emails Blocked",
        "sender": "admin@webmail-quota-increase.net",
        "body": "Warning: Your webmail storage has reached 99.8% capacity. You will be unable to send or receive new emails. To upgrade your mailbox quota for free and retrieve pending emails, click: http://webmail-storage-update.top/quota."
    },
    {
        "label": 1,
        "subject": "Crypto Alert: Claim 500 USDT Airdrop from Binance",
        "sender": "rewards@binance-airdrop-bonus.org",
        "body": "Binance anniversary giveaway! As an active crypto trader, you are eligible to claim 500 USDT in free airdrop tokens. Connect your Web3 wallet or enter your private key to claim: http://binance-claim-reward.xyz/wallet."
    },
    {
        "label": 1,
        "subject": "DocuSign: Please review and sign Employment Termination Agreement",
        "sender": "docusign@docs-electronic-signature.top",
        "body": "HR Legal has sent you a document via DocuSign: 'Severance & Mutual Release Agreement'. Please review and electronically sign this urgent document: http://docusign-secure-document.xyz/sign. Document ID: 4891-B829."
    },
    {
        "label": 1,
        "subject": "Chase Bank: Suspicious Zelle payment of $980.00 attempted",
        "sender": "fraud@chase-fraud-prevention.net",
        "body": "Chase Fraud Alert: Did you attempt a Zelle transfer of $980.00 to SAMUEL K? If NO, reply STOP and click here immediately to secure your bank account: http://chase-security-fraud.com/verify."
    },
    {
        "label": 1,
        "subject": "Final Notice: Domain name expiration warning",
        "sender": "billing@domain-renewals-registrar.info",
        "body": "URGENT: Your domain registration is set to expire in 24 hours. Your website and email services will be disconnected immediately unless you renew your domain now: http://renew-domain-dns.top/payment."
    },
    {
        "label": 1,
        "subject": "DHL Express: Undelivered parcel notification #DH-892182",
        "sender": "delivery@dhl-express-reschedule.com",
        "body": "We attempted to deliver your parcel on Sep 11 at 11:20 AM. The courier was unable to access your premises. Please confirm your delivery address and pay redelivery fee: http://dhl-express-delivery.info/redeliver."
    },
    {
        "label": 1,
        "subject": "Wells Fargo: Your online banking profile requires verification",
        "sender": "support@wellsfargo-profile-update.com",
        "body": "Wells Fargo Online Security Update: Due to recent regulatory requirements, all customers must re-verify their personal identity and debit PIN. Click here to confirm your information: http://wellsfargo-verify-security.cc/portal."
    },
    {
        "label": 1,
        "subject": "Metamask Security: Upgrade your wallet to V3 to prevent asset loss",
        "sender": "security@metamask-v3-upgrade.org",
        "body": "Immediate warning for all Ethereum and Web3 wallet users: Metamask V2 is being deprecated. Upgrade to Metamask V3 immediately to protect your cryptocurrencies: http://metamask-v3-upgrade.xyz/restore. Enter seed phrase."
    },
    {
        "label": 1,
        "subject": "eBay: Your recent purchase of iPhone 15 Pro Max $1,199",
        "sender": "support@ebay-orders-cancellation.info",
        "body": "Thank you for your order! Your payment of $1,199.00 for Apple iPhone 15 Pro Max has been approved. If you did not make this purchase, call our fraud department or cancel order immediately: http://ebay-order-dispute.top/cancel."
    },
    {
        "label": 1,
        "subject": "Office 365: You have 7 pending quarantined messages",
        "sender": "quarantine@office365-security-admin.com",
        "body": "You have 7 incoming emails currently held in your Microsoft 365 quarantine box. These messages will be permanently deleted in 24 hours. Review quarantined emails here: http://office365-quarantine-release.xyz/inbox."
    },
    {
        "label": 1,
        "subject": "Coinbase Security: Unauthorized withdrawal of 0.85 BTC detected",
        "sender": "security@coinbase-account-alerts.info",
        "body": "Security Alert: A withdrawal of 0.85 BTC (~$55,000 USD) to external wallet 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa has been requested. If you did not authorize this, cancel immediately: http://coinbase-fraud-protection.cc/cancel."
    },
    {
        "label": 1,
        "subject": "Dropbox: Your file storage has expired and will be wiped",
        "sender": "support@dropbox-storage-renewal.top",
        "body": "Dear Dropbox user, Your 1TB cloud storage plan has expired. Your photos, documents, and backups will be permanently wiped within 48 hours. Reactivate your subscription now: http://dropbox-renew-plan.xyz/checkout."
    },
    {
        "label": 1,
        "subject": "American Express: Card suspended due to suspicious international charge",
        "sender": "alerts@amex-account-verification.info",
        "body": "American Express Alert: We detected an overseas transaction of $1,240.00 in London, UK. Your card has been temporarily deactivated. Click here to confirm your cardholder identity: http://amex-protection-service.com/unlock."
    },
    {
        "label": 1,
        "subject": "Adobe Creative Cloud: Payment failed - subscription terminating",
        "sender": "billing@adobe-subscription-billing.top",
        "body": "We could not process your recurring payment for Adobe Creative Cloud All Apps. Your access to Photoshop, Illustrator, and Premiere Pro will terminate today. Update payment information: http://adobe-account-update.xyz/pay."
    },
    {
        "label": 1,
        "subject": "Steam Guard: Access from unrecognized browser in China",
        "sender": "support@steam-community-login.top",
        "body": "Steam Guard Code: 98124. Someone attempted to log in to your Steam account from Shanghai, China. If this was not you, change your password immediately to protect your Steam inventory: http://steamcommunity-login-verify.top/auth."
    },

    # Legitimate / Safe Emails (label 0) - including challenging emails with links, urgency, or business terms
    {
        "label": 0,
        "subject": "Team sync meeting notes and action items",
        "sender": "sarah.jenkins@acme-corp.com",
        "body": "Hi Team, Thanks for attending today's project sync. Here are the key action items: 1. Finalize the Q3 roadmap by Thursday. 2. Review the pull request for the auth service. Let me know if you have any questions or updates before Friday."
    },
    {
        "label": 0,
        "subject": "Your Amazon order #402-9821381 has shipped",
        "sender": "shipment-tracking@amazon.com",
        "body": "Hello, Good news! Your package is on its way. Estimated delivery date: Tomorrow by 8 PM. You can track your package status on your Amazon account dashboard anytime: https://www.amazon.com/gp/css/order-history."
    },
    {
        "label": 0,
        "subject": "Google Cloud Platform: Monthly invoice available",
        "sender": "cloud-noreply@google.com",
        "body": "Hello, Your Google Cloud Platform invoice for last month is now ready to view. Total amount billed: $14.20. You can download your PDF invoice from the Google Cloud Console billing section: https://console.cloud.google.com/billing."
    },
    {
        "label": 0,
        "subject": "Invitation: Product Design Review @ Wed Sep 16",
        "sender": "alex.rivera@company.io",
        "body": "You have been invited to attend Product Design Review. When: Wednesday, September 16, 2:00 PM - 3:00 PM EST. Where: Google Meet (meet.google.com/abc-defg-hij). Agenda: Review final mobile navigation mocks."
    },
    {
        "label": 0,
        "subject": "Your weekly GitHub digest for repository updates",
        "sender": "notifications@github.com",
        "body": "Here is your weekly summary of activity across your subscribed repositories: 12 pull requests merged, 4 issues closed, 3 releases published. Visit https://github.com to see full commit activity."
    },
    {
        "label": 0,
        "subject": "Receipt for your payment to Spotify Premium",
        "sender": "no-reply@spotify.com",
        "body": "Thank you for your payment of $10.99 for Spotify Premium. Subscription Period: Sep 12 to Oct 12. Your receipt has been archived in your Spotify account overview: https://www.spotify.com/account/subscription."
    },
    {
        "label": 0,
        "subject": "Weekly Newsletter: Latest in Artificial Intelligence & Python",
        "sender": "newsletter@techinsider.org",
        "body": "Welcome to this week's edition of Tech Insider. In this issue: Deep dive into open source LLM fine-tuning, Python 3.13 performance improvements, and vector search benchmarks. Read the full article on our blog."
    },
    {
        "label": 0,
        "subject": "Your Zoom meeting link for Client Onboarding",
        "sender": "meetings@zoom.us",
        "body": "Hi David, Your Zoom meeting 'Client Onboarding' is scheduled for today at 4:30 PM. Join Zoom Meeting: https://zoom.us/j/98127391823. Meeting ID: 981 2739 1823. Passcode: 482910."
    },
    {
        "label": 0,
        "subject": "Slack: New messages in #engineering",
        "sender": "notifications@slack.com",
        "body": "You have 5 unread messages in #engineering from Marcus and Elena: 'Marcus: I pushed the fix for the database connection pool.' View messages in Slack: https://slack.com/app."
    },
    {
        "label": 0,
        "subject": "Flight confirmation: San Francisco to New York",
        "sender": "reservations@delta.com",
        "body": "Thank you for booking with Delta Air Lines. Your confirmation code is H8K2P9. Flight DL 482 departs SFO on Oct 5 at 8:00 AM. Access your boarding pass: https://www.delta.com/mytrips."
    },
    {
        "label": 0,
        "subject": "Docker Hub: Security scan report for your image",
        "sender": "no-reply@docker.com",
        "body": "Docker Scout completed an automated vulnerability scan for your repository 'myorg/web-service:latest'. 0 critical, 1 medium, 3 low severity vulnerabilities found. See report: https://hub.docker.com/repository/docker/myorg/web-service."
    },
    {
        "label": 0,
        "subject": "Stripe: Payout of $2,450.00 is on the way",
        "sender": "notifications@stripe.com",
        "body": "Your payout of $2,450.00 is currently processing and should arrive in your bank account ending in 4102 within 1-2 business days. View your payout history at https://dashboard.stripe.com/payouts."
    },
    {
        "label": 0,
        "subject": "Your LinkedIn connections are talking about AI agents",
        "sender": "messages-noreply@linkedin.com",
        "body": "See what your network is sharing: 4 connections recently posted updates about AI agents and cybersecurity. View post on LinkedIn: https://www.linkedin.com/feed/update/urn:li:activity:789234."
    },
    {
        "label": 0,
        "subject": "Atlassian Jira: Issue assigned to you PROJ-1049",
        "sender": "jira@atlassian.net",
        "body": "Michael Chang assigned Jira issue PROJ-1049 to you: 'Optimize SQL queries on user dashboard'. Priority: High. View issue: https://yourcompany.atlassian.net/browse/PROJ-1049."
    },
    {
        "label": 0,
        "subject": "Google Calendar: Daily agenda for tomorrow",
        "sender": "calendar-notification@google.com",
        "body": "Here is your schedule for Monday: 9:30 AM Sprint Planning, 1:00 PM 1-on-1 with Manager, 4:00 PM Architecture Review. View Google Calendar: https://calendar.google.com."
    },
    {
        "label": 0,
        "subject": "Coursera: New course recommendation based on your interests",
        "sender": "no-reply@coursera.org",
        "body": "Explore our latest course: 'Machine Learning Specialization with Python and Scikit-Learn'. Start your 7-day free trial today: https://www.coursera.org/learn/machine-learning."
    },
    {
        "label": 0,
        "subject": "GitLab: Pipeline #48192 succeeded for branch main",
        "sender": "gitlab@gitlab.com",
        "body": "Pipeline #48192 for commit b4f8a12 on branch main has passed successfully. Duration: 3m 42s. View details: https://gitlab.com/project/pipelines/48192."
    },
    {
        "label": 0,
        "subject": "Medium Daily Digest: Top stories in Software Engineering",
        "sender": "noreply@medium.com",
        "body": "Stories for you today: 'Building Real-time Apps with WebSockets and FastAPI', '10 Clean Code Principles Every Dev Should Know'. Read stories on Medium: https://medium.com."
    },
    {
        "label": 0,
        "subject": "Figma: Comments added on 'Design System v2.0'",
        "sender": "notifications@figma.com",
        "body": "Elena commented on Design System v2.0: 'Updated the button color palette and typography tokens.' Open in Figma: https://www.figma.com/file/abcdef123."
    },
    {
        "label": 0,
        "subject": "Uber: Your ride with Driver Ahmed on Friday evening",
        "sender": "uber.receipts@uber.com",
        "body": "Thanks for riding with Uber! Total paid: $22.50. Pickup: Market St, San Francisco. Dropoff: 4th St, San Francisco. View your full ride receipt: https://www.uber.com/trips."
    },
    {
        "label": 0,
        "subject": "Airbnb: Reservation confirmed for Austin, TX",
        "sender": "automated@airbnb.com",
        "body": "You are going to Austin! Confirmation code: HM482K. Check-in: Friday, Oct 10, 3:00 PM. Check-out: Sunday, Oct 12, 11:00 AM. View reservation details on Airbnb: https://www.airbnb.com/trips."
    },
    {
        "label": 0,
        "subject": "Hacker News: Top posts of the day",
        "sender": "digest@hackernews.com",
        "body": "Top submissions today: 'Show HN: Fast and lightweight vector database', 'PostgreSQL 17 released'. Visit Hacker News: https://news.ycombinator.com."
    },
    {
        "label": 0,
        "subject": "Vercel: Deployment complete for project 'dashboard-app'",
        "sender": "notifications@vercel.com",
        "body": "Your deployment 'dashboard-app-prod' is now live at https://dashboard-app.vercel.app. Build time: 42s. View deployment dashboard on Vercel."
    },
    {
        "label": 0,
        "subject": "Stack Overflow: Weekly newsletter for Python developers",
        "sender": "do-not-reply@stackoverflow.email",
        "body": "Top questions this week: 'How does asyncio event loop schedule coroutines?', 'Best practices for REST API rate limiting'. Read answers on Stack Overflow: https://stackoverflow.com."
    },
    {
        "label": 0,
        "subject": "Notion: Maria shared a workspace page with you",
        "sender": "notify@notion.so",
        "body": "Maria invited you to view the page 'Q4 Engineering OKRs & Goals'. Click here to open the page in Notion: https://notion.so/workspace/okrs-2026."
    },
    # Edge Cases: Legitimate emails with urgent language, security notifications, or links
    {
        "label": 0,
        "subject": "Urgent: Please review and sign vendor NDA before 5 PM today",
        "sender": "legal@acme-corp.com",
        "body": "Hi Team, We have an urgent contract deadline with our cloud partner today. Please review the updated non-disclosure agreement in our internal shared drive and approve it before 5 PM EST. Thank you for your prompt attention."
    },
    {
        "label": 0,
        "subject": "Security alert: New sign-in to your Google Account from Chrome on Windows",
        "sender": "no-reply@accounts.google.com",
        "body": "We noticed a new sign-in to your Google Account on a Windows device. If this was you, you don't need to do anything. If not, we'll help you secure your account. Check activity: https://myaccount.google.com/notifications."
    },
    {
        "label": 0,
        "subject": "Immediate action required: Complete your annual compliance training",
        "sender": "compliance-officer@enterprise-corp.com",
        "body": "All employees must complete the mandatory annual cyber security awareness training module by Friday. Immediate completion is required by our SOC2 auditor. Access the company training portal on your intranet."
    },
    {
        "label": 0,
        "subject": "DocuSign: Completed copy of your Mutual NDA",
        "sender": "dse@docusign.net",
        "body": "All signers have completed signing the document: 'Mutual Non-Disclosure Agreement'. A completed copy is attached for your records, or view it at https://na2.docusign.net/Member/Document.aspx."
    },
    {
        "label": 0,
        "subject": "Your Microsoft 365 security verification code",
        "sender": "account-security-noreply@accountprotection.microsoft.com",
        "body": "Use security code 491823 for Microsoft authentication. If you did not request this code, you can safely ignore this email. Someone may have entered your email address by mistake."
    }
]

def load_and_filter_ceas_samples(target_phish=2500, target_safe=2500) -> List[Dict[str, Any]]:
    """Load high-quality, balanced, deduplicated emails from CEAS 2008 benchmark."""
    if not os.path.exists(RAW_CEAS_PATH):
        raise FileNotFoundError(f"Raw CEAS 08 dataset not found at {RAW_CEAS_PATH}")

    phish_collected = []
    safe_collected = []
    seen_texts = set()

    with open(RAW_CEAS_PATH, "r", encoding="utf-8", errors="ignore") as f:
        reader = csv.DictReader(f)
        for row in reader:
            lbl_str = row.get("label")
            if lbl_str not in ("0", "1"):
                continue

            lbl = int(lbl_str)
            subj = (row.get("subject") or "").strip()
            sender = (row.get("sender") or "").strip()
            body = (row.get("body") or "").strip()

            combined = f"{subj} {sender} {body}".strip().lower()
            # Clean excessive whitespace
            combined_norm = re.sub(r"\s+", " ", combined)

            if len(combined_norm) < 30 or len(combined_norm) > 15000:
                continue

            if combined_norm in seen_texts:
                continue
            seen_texts.add(combined_norm)

            entry = {
                "label": lbl,
                "subject": subj,
                "sender": sender,
                "body": body
            }

            if lbl == 1 and len(phish_collected) < target_phish:
                phish_collected.append(entry)
            elif lbl == 0 and len(safe_collected) < target_safe:
                safe_collected.append(entry)

            if len(phish_collected) >= target_phish and len(safe_collected) >= target_safe:
                break

    print(f"CEAS sampled: {len(phish_collected)} Phishing, {len(safe_collected)} Safe")
    return phish_collected + safe_collected

def build_dataset():
    print("Building expanded, deduplicated, balanced dataset...")
    
    # 1. Curated modern samples (with fixed quotes and edge cases)
    curated_seen = set()
    clean_curated = []
    for item in CURATED_MODERN_SAMPLES:
        norm = re.sub(r"\s+", " ", f"{item['subject']} {item['sender']} {item['body']}".lower())
        if norm not in curated_seen:
            curated_seen.add(norm)
            clean_curated.append(item)

    # 2. Benchmark CEAS samples (2,475 Phish, 2,475 Safe so total is ~5,000)
    ceas_samples = load_and_filter_ceas_samples(target_phish=2475, target_safe=2475)

    all_samples = clean_curated + ceas_samples
    
    # Deduplicate across entire merged collection
    final_dataset = []
    dedup_seen = set()
    phish_count = 0
    safe_count = 0

    # Shuffle deterministically
    random.shuffle(all_samples)

    for item in all_samples:
        norm = re.sub(r"\s+", " ", f"{item['subject']} {item['sender']} {item['body']}".lower())
        if norm in dedup_seen:
            continue
        dedup_seen.add(norm)
        lbl = item["label"]
        if lbl == 1:
            phish_count += 1
        else:
            safe_count += 1
        final_dataset.append(item)

    print(f"\nFinal Merged Dataset: {len(final_dataset)} total samples")
    print(f"  Phishing (1): {phish_count} ({phish_count / len(final_dataset) * 100:.1f}%)")
    print(f"  Safe     (0): {safe_count} ({safe_count / len(final_dataset) * 100:.1f}%)")

    # Save master dataset CSV
    with open(MASTER_CSV_PATH, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["label", "subject", "sender", "body"])
        writer.writeheader()
        writer.writerows(final_dataset)
    print(f"Saved master dataset -> {MASTER_CSV_PATH}")

    # Create stratified Train (70%), Validation (15%), Test (15%) splits
    phish_pool = [x for x in final_dataset if x["label"] == 1]
    safe_pool = [x for x in final_dataset if x["label"] == 0]

    def split_pool(pool, train_ratio=0.70, val_ratio=0.15):
        n = len(pool)
        n_train = int(n * train_ratio)
        n_val = int(n * val_ratio)
        train = pool[:n_train]
        val = pool[n_train:n_train + n_val]
        test = pool[n_train + n_val:]
        return train, val, test

    p_train, p_val, p_test = split_pool(phish_pool)
    s_train, s_val, s_test = split_pool(safe_pool)

    train_data = p_train + s_train
    val_data = p_val + s_val
    test_data = p_test + s_test

    random.shuffle(train_data)
    random.shuffle(val_data)
    random.shuffle(test_data)

    print(f"\nDataset Splits:")
    print(f"  Train:      {len(train_data)} (Phish: {len(p_train)}, Safe: {len(s_train)})")
    print(f"  Validation: {len(val_data)} (Phish: {len(p_val)}, Safe: {len(s_val)})")
    print(f"  Test:       {len(test_data)} (Phish: {len(p_test)}, Safe: {len(s_test)})")

    # Verify zero leakage across splits
    train_texts = set(re.sub(r"\s+", " ", f"{x['subject']} {x['sender']} {x['body']}".lower()) for x in train_data)
    val_texts = set(re.sub(r"\s+", " ", f"{x['subject']} {x['sender']} {x['body']}".lower()) for x in val_data)
    test_texts = set(re.sub(r"\s+", " ", f"{x['subject']} {x['sender']} {x['body']}".lower()) for x in test_data)

    assert len(train_texts.intersection(val_texts)) == 0, "Data leakage: Train & Val overlap!"
    assert len(train_texts.intersection(test_texts)) == 0, "Data leakage: Train & Test overlap!"
    assert len(val_texts.intersection(test_texts)) == 0, "Data leakage: Val & Test overlap!"
    print("Verification passed: ZERO data leakage across Train / Val / Test splits.")

    # Save splits to disk
    for name, data in [("train.csv", train_data), ("val.csv", val_data), ("test.csv", test_data)]:
        path = os.path.join(SPLITS_DIR, name)
        with open(path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["label", "subject", "sender", "body"])
            writer.writeheader()
            writer.writerows(data)
        print(f"Saved split -> {path}")

if __name__ == "__main__":
    build_dataset()
