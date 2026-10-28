import requests
import json
import uuid

def test_live_api():
    base_url = "http://127.0.0.1:8000"
    
    # 1. Health check (public endpoint)
    res = requests.get(f"{base_url}/api/health")
    assert res.status_code == 200, f"Health check failed: {res.status_code}"
    health_data = res.json()
    print("Health Check:", health_data)
    assert health_data["model_loaded"] is True
    
    # 2. Authenticate session server-side to obtain valid JWT Bearer token
    session_res = requests.post(f"{base_url}/api/auth/session", json={
        "user_id": f"live_analyst_{uuid.uuid4().hex[:6]}"
    })
    assert session_res.status_code == 200, f"Session init failed: {session_res.status_code}"
    session_data = session_res.json()
    token = session_data["token"]
    headers = {"Authorization": f"Bearer {token}"}
    print(f"\nAuthenticated session initialized for {session_data['user']['user_id']}. Token active.")

    # 3. Simulate batch of emails
    sim_res = requests.post(f"{base_url}/api/emails/simulate-batch", headers=headers)
    assert sim_res.status_code == 200, f"Simulation failed: {sim_res.status_code}"
    print("Simulate Batch Response:", sim_res.json()["message"])
    
    # 4. Fetch Dashboard stats
    stats_res = requests.get(f"{base_url}/api/dashboard/stats", headers=headers)
    assert stats_res.status_code == 200
    stats = stats_res.json()
    print("\n--- DASHBOARD STATS ---")
    print(f"Total Scanned: {stats['total_scanned']}, Phishing Count: {stats['phishing_count']}")
    assert stats["total_scanned"] > 0
    assert stats["phishing_count"] > 0
    
    # 5. Fetch Scanned emails
    emails_res = requests.get(f"{base_url}/api/emails?limit=10", headers=headers)
    assert emails_res.status_code == 200
    email_data = emails_res.json()
    print(f"\nFetched {len(email_data['items'])} scanned emails from API.")
    for item in email_data['items'][:3]:
        print(f"[{item['classification']}] Risk: {item['risk_score']} | Subject: {item['subject'][:40]} | Sender: {item['sender']}")
        
    # 6. Test Custom Analyze endpoint
    custom_payload = {
        "subject": "Wire Transfer of $90,000 for Vendor Invoice",
        "sender": "ceo@executive-payment-transfer.top",
        "body": "Urgent wire transfer needed immediately before 5 PM: http://192.168.1.50/pay",
        "save_result": True
    }
    custom_res = requests.post(f"{base_url}/api/emails/analyze-custom", json=custom_payload, headers=headers)
    assert custom_res.status_code == 200
    custom_data = custom_res.json()
    print("\nCustom Analysis Result:")
    print(f"Classification: {custom_data['classification']}, Risk Score: {custom_data['risk_score']}")
    print("Detected flags:", custom_data['detected_flags'])
    assert custom_data['classification'] == "PHISHING"
    
    # 7. Test Google Auth status endpoint
    auth_res = requests.get(f"{base_url}/api/auth/status", headers=headers)
    assert auth_res.status_code == 200
    auth_data = auth_res.json()
    print("\nGmail Auth Status:", auth_data)
    assert "is_connected" in auth_data
    
    print("\nAll live end-to-end API tests PASSED!")

if __name__ == "__main__":
    test_live_api()
