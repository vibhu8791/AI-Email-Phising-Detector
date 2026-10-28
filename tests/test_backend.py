import os
import sys

# Add root and backend to sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root_dir)
sys.path.insert(0, os.path.join(root_dir, "backend"))

from backend.app.services.analyzer import analyzer
from database.connection import db_service
import asyncio

def test_analyzer():
    print("Testing ML Model and Heuristic Analyzer...")
    assert analyzer.is_loaded, "Model should be loaded"

    # Test Phishing email
    phish_res = analyzer.analyze(
        subject="URGENT: Your PayPal Account Has Been Suspended",
        sender="security-alert@paypa1-support.com",
        body="We detected unauthorized activity. Verify immediately: http://192.168.1.100/verify-paypal within 24 hours."
    )
    print("\n--- PHISHING TEST ---")
    print(f"Classification: {phish_res['classification']}")
    print(f"Risk Score:     {phish_res['risk_score']}/100")
    print(f"ML Probability: {phish_res['ml_phishing_probability'] * 100:.1f}%")
    print(f"Flags Detected: {phish_res['detected_flags']}")
    assert phish_res['classification'] == "PHISHING", f"Expected PHISHING, got {phish_res['classification']}"
    assert phish_res['risk_score'] >= 70, f"Expected risk >= 70, got {phish_res['risk_score']}"

    # Test Safe email
    safe_res = analyzer.analyze(
        subject="Sprint Planning Notes & Roadmap",
        sender="alex.manager@techcorp.com",
        body="Hi Team, Here are the action items from our sprint planning meeting. Have a great week!"
    )
    print("\n--- SAFE TEST ---")
    print(f"Classification: {safe_res['classification']}")
    print(f"Risk Score:     {safe_res['risk_score']}/100")
    print(f"ML Probability: {safe_res['ml_phishing_probability'] * 100:.1f}%")
    print(f"Flags Detected: {safe_res['detected_flags']}")
    assert safe_res['classification'] == "SAFE", f"Expected SAFE, got {safe_res['classification']}"
    assert safe_res['risk_score'] <= 35, f"Expected risk <= 35, got {safe_res['risk_score']}"

    # Test Suspicious email
    susp_res = analyzer.analyze(
        subject="Survey: Employee Contact Update",
        sender="hr-team@benefits-survey-portal.xyz",
        body="Please confirm your home address on http://benefits-survey-portal.xyz/login today."
    )
    print("\n--- SUSPICIOUS / MALICIOUS TLD TEST ---")
    print(f"Classification: {susp_res['classification']}")
    print(f"Risk Score:     {susp_res['risk_score']}/100")
    assert susp_res['classification'] in ["SUSPICIOUS", "PHISHING"]

    # Test Legitimate Brand Alert (Zero False Positive Check)
    google_res = analyzer.analyze(
        subject="Security alert: New sign-in from Chrome on Windows",
        sender="Google <no-reply@accounts.google.com>",
        body="A new sign-in occurred on your Google Account from a Windows device. Review your devices at https://myaccount.google.com/device-activity immediately."
    )
    print("\n--- LEGITIMATE GOOGLE SECURITY ALERT (FALSE POSITIVE CHECK) ---")
    print(f"Classification: {google_res['classification']}")
    print(f"Risk Score:     {google_res['risk_score']}/100")
    print(f"ML Probability: {google_res['ml_phishing_probability'] * 100:.1f}%")
    assert google_res['classification'] == "SAFE", f"Expected SAFE for genuine Google alert, got {google_res['classification']}"
    assert google_res['risk_score'] <= 35

    # Test Urgent Corporate Legal Review (Urgency False Positive Check)
    legal_res = analyzer.analyze(
        subject="URGENT: Please review NDA draft by 5:00 PM today",
        sender="Sarah Jenkins <legal@enterprise-corp.com>",
        body="Hi Team, please find attached the revised mutual NDA for Project Horizon. We need legal signoff by 5:00 PM sharp to submit to the client."
    )
    print("\n--- LEGITIMATE URGENT BUSINESS EMAIL (FALSE POSITIVE CHECK) ---")
    print(f"Classification: {legal_res['classification']}")
    print(f"Risk Score:     {legal_res['risk_score']}/100")
    print(f"ML Probability: {legal_res['ml_phishing_probability'] * 100:.1f}%")
    assert legal_res['classification'] == "SAFE", f"Expected SAFE for genuine urgent business email, got {legal_res['classification']}"
    assert legal_res['risk_score'] <= 35

    # Test CEO BEC Wire Fraud (False Negative Check)
    bec_res = analyzer.analyze(
        subject="Immediate Wire Transfer Required - Confidential",
        sender="Mark Zuckerberg <ceo-direct@vip-offices-global.com>",
        body="I am currently in an urgent meeting with our acquisition partners. Please execute an immediate wire transfer of $45,000 to the attached vendor account today. Keep this strictly confidential."
    )
    print("\n--- CEO BEC WIRE FRAUD TEST ---")
    print(f"Classification: {bec_res['classification']}")
    print(f"Risk Score:     {bec_res['risk_score']}/100")
    print(f"ML Probability: {bec_res['ml_phishing_probability'] * 100:.1f}%")
    assert bec_res['classification'] == "PHISHING", f"Expected PHISHING for BEC wire fraud, got {bec_res['classification']}"
    assert bec_res['risk_score'] >= 70

    print("\nAll Analyzer assertions and False-Positive/False-Negative guardrails passed!")

async def test_database():
    print("\nTesting Database Service...")
    await db_service.connect("mongodb://localhost:27017", "phishing_detection_test_db")
    stats = await db_service.get_stats()
    print(f"Database Mode: {stats['database_mode']}")
    print(f"Total Scanned: {stats['total_scanned']}")
    print("Database Service operational!")

if __name__ == "__main__":
    test_analyzer()
    asyncio.run(test_database())
