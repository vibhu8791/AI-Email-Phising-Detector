import os
import sys
import unittest
import uuid
import time
import threading
import requests
from datetime import datetime

# Ensure root directory and backend directory are in sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)
backend_dir = os.path.join(root_dir, "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.core.security import encrypt_token, decrypt_token, generate_oauth_state, verify_oauth_state
from app.api.auth import SCOPES
from database.connection import db_service

class TestMultiAccountAndIsolation(unittest.TestCase):
    BASE_URL = "http://127.0.0.1:8000"

    @classmethod
    def setUpClass(cls):
        # Check if live server is already running on port 8000
        try:
            r = requests.get(f"{cls.BASE_URL}/api/health", timeout=1)
            if r.status_code == 200:
                print(f"[TEST] Using active server at {cls.BASE_URL}")
            else:
                cls._start_test_server(port=8001)
        except Exception:
            cls._start_test_server(port=8001)

        cls.user_a = f"user_a_{uuid.uuid4().hex[:6]}"
        cls.user_b = f"user_b_{uuid.uuid4().hex[:6]}"
        cls.headers_a = {"X-User-ID": cls.user_a}
        cls.headers_b = {"X-User-ID": cls.user_b}

    @classmethod
    def _start_test_server(cls, port=8001):
        import uvicorn
        from app.main import app

        cls.BASE_URL = f"http://127.0.0.1:{port}"
        print(f"[TEST] Spawning embedded server on {cls.BASE_URL}...")
        t = threading.Thread(
            target=lambda: uvicorn.run(app, host="127.0.0.1", port=port, log_level="warning"),
            daemon=True
        )
        t.start()
        # Wait for server to bind
        for _ in range(25):
            try:
                res = requests.get(f"{cls.BASE_URL}/api/health", timeout=1)
                if res.status_code == 200:
                    print("[TEST] Embedded server ready.")
                    return
            except Exception:
                time.sleep(0.2)
        raise RuntimeError("Failed to launch embedded test server.")

    def test_01_minimum_scopes_and_secure_state(self):
        """Requirement 8 & 9: Verify minimum read-only scopes and signed state token."""
        self.assertIn("https://www.googleapis.com/auth/gmail.readonly", SCOPES)
        self.assertNotIn("https://mail.google.com/", SCOPES)
        self.assertNotIn("https://www.googleapis.com/auth/gmail.modify", SCOPES)
        self.assertNotIn("https://www.googleapis.com/auth/gmail.compose", SCOPES)

        state = generate_oauth_state(self.user_a)
        self.assertIsInstance(state, str)
        verified = verify_oauth_state(state)
        self.assertIsNotNone(verified)
        self.assertEqual(verified["user_id"], self.user_a)

        # Tampered state must fail verification
        self.assertIsNone(verify_oauth_state(state + "_tampered"))

    def test_02_connect_two_accounts_for_user_a(self):
        """Requirement 1, 2, 3: Connect two accounts for User A and verify listing & defaults."""
        email_1 = f"alice_work_{uuid.uuid4().hex[:4]}@gmail.com"
        email_2 = f"alice_personal_{uuid.uuid4().hex[:4]}@gmail.com"

        # Connect account 1
        res1 = requests.post(f"{self.BASE_URL}/api/auth/accounts/demo-connect", headers=self.headers_a, json={
            "email": email_1,
            "display_name": "Alice Work"
        })
        self.assertEqual(res1.status_code, 200)
        acc1_data = res1.json()["account"]
        self.assertEqual(acc1_data["email"], email_1)
        self.assertTrue(acc1_data["is_default"])  # First account becomes default

        # Connect account 2
        res2 = requests.post(f"{self.BASE_URL}/api/auth/accounts/demo-connect", headers=self.headers_a, json={
            "email": email_2,
            "display_name": "Alice Personal"
        })
        self.assertEqual(res2.status_code, 200)
        acc2_data = res2.json()["account"]
        self.assertEqual(acc2_data["email"], email_2)

        # List accounts for User A
        list_res = requests.get(f"{self.BASE_URL}/api/auth/accounts", headers=self.headers_a)
        self.assertEqual(list_res.status_code, 200)
        accounts = list_res.json()["accounts"]
        self.assertEqual(len(accounts), 2)
        account_emails = [a["email"] for a in accounts]
        self.assertIn(email_1, account_emails)
        self.assertIn(email_2, account_emails)

        # Requirement 5: Check tokens are never exposed in API responses
        for acc in accounts:
            self.assertNotIn("access_token", acc)
            self.assertNotIn("refresh_token", acc)
            self.assertNotIn("access_token_encrypted", acc)
            self.assertNotIn("refresh_token_encrypted", acc)

        # Save IDs for subsequent tests
        TestMultiAccountAndIsolation.acc1_id = acc1_data["id"]
        TestMultiAccountAndIsolation.acc2_id = acc2_data["id"]
        TestMultiAccountAndIsolation.email_1 = email_1
        TestMultiAccountAndIsolation.email_2 = email_2

    def test_03_switch_active_account(self):
        """Requirement 4: Switch active scanning account and verify default flag."""
        # Switch to account 2
        switch_res = requests.post(
            f"{self.BASE_URL}/api/auth/accounts/{self.acc2_id}/select",
            headers=self.headers_a
        )
        self.assertEqual(switch_res.status_code, 200)

        # Verify status endpoint reflects account 2
        status_res = requests.get(f"{self.BASE_URL}/api/auth/status", headers=self.headers_a)
        self.assertEqual(status_res.status_code, 200)
        status_data = status_res.json()
        self.assertEqual(status_data["email"], self.email_2)
        self.assertEqual(status_data["account_id"], self.acc2_id)

    def test_04_scan_emails_from_selected_account(self):
        """Requirement 4: Scan emails using the production analyzer from the selected account."""
        sync_res = requests.post(
            f"{self.BASE_URL}/api/emails/sync?max_count=3&account_id={self.acc2_id}",
            headers=self.headers_a
        )
        self.assertEqual(sync_res.status_code, 200)
        data = sync_res.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["account_email"], self.email_2)
        self.assertGreater(data["scanned_count"], 0)

        # Check scanned items have account metadata and risk classification
        for item in data["items"]:
            self.assertEqual(item["user_id"], self.user_a)
            self.assertEqual(item["account_id"], self.acc2_id)
            self.assertEqual(item["account_email"], self.email_2)
            self.assertIn(item["classification"], ["SAFE", "SUSPICIOUS", "PHISHING"])
            self.assertIn("timestamp_epoch", item)

        TestMultiAccountAndIsolation.user_a_email_id = data["items"][0]["id"]

    def test_05_disconnect_one_account_keeps_other_active(self):
        """Requirement 7: Disconnecting one account preserves the remaining account and sets it active."""
        # Disconnect account 2
        disc_res = requests.post(
            f"{self.BASE_URL}/api/auth/accounts/{self.acc2_id}/disconnect",
            headers=self.headers_a
        )
        self.assertEqual(disc_res.status_code, 200)

        # List accounts for User A
        list_res = requests.get(f"{self.BASE_URL}/api/auth/accounts", headers=self.headers_a)
        self.assertEqual(list_res.status_code, 200)
        remaining = list_res.json()["accounts"]
        self.assertEqual(len(remaining), 1)
        self.assertEqual(remaining[0]["id"], self.acc1_id)
        self.assertTrue(remaining[0]["is_default"])  # Account 1 promoted to default

    def test_06_multi_user_data_isolation(self):
        """Requirement 6: User A and User B data must remain completely isolated."""
        # Connect an account for User B
        email_b = f"bob_corp_{uuid.uuid4().hex[:4]}@gmail.com"
        res_b = requests.post(f"{self.BASE_URL}/api/auth/accounts/demo-connect", headers=self.headers_b, json={
            "email": email_b,
            "display_name": "Bob Corp"
        })
        self.assertEqual(res_b.status_code, 200)
        acc_b_id = res_b.json()["account"]["id"]

        # User B syncs emails
        sync_b = requests.post(f"{self.BASE_URL}/api/emails/sync?max_count=2", headers=self.headers_b)
        self.assertEqual(sync_b.status_code, 200)
        user_b_email_id = sync_b.json()["items"][0]["id"]

        # Check Account Isolation
        accounts_a = requests.get(f"{self.BASE_URL}/api/auth/accounts", headers=self.headers_a).json()["accounts"]
        accounts_b = requests.get(f"{self.BASE_URL}/api/auth/accounts", headers=self.headers_b).json()["accounts"]
        self.assertNotIn(email_b, [a["email"] for a in accounts_a])
        self.assertNotIn(self.email_1, [a["email"] for a in accounts_b])

        # Check Email History Isolation
        emails_a = requests.get(f"{self.BASE_URL}/api/emails", headers=self.headers_a).json()["items"]
        emails_b = requests.get(f"{self.BASE_URL}/api/emails", headers=self.headers_b).json()["items"]
        a_ids = [e["id"] for e in emails_a]
        b_ids = [e["id"] for e in emails_b]
        self.assertNotIn(user_b_email_id, a_ids)
        self.assertNotIn(self.user_a_email_id, b_ids)

        # Cross-User Security Test 1: User A requests User B's email detail
        cross_get = requests.get(f"{self.BASE_URL}/api/emails/{user_b_email_id}", headers=self.headers_a)
        self.assertEqual(cross_get.status_code, 404)

        # Cross-User Security Test 2: User A attempts to delete User B's email
        cross_del = requests.delete(f"{self.BASE_URL}/api/emails/{user_b_email_id}", headers=self.headers_a)
        self.assertEqual(cross_del.status_code, 404)

        # Cross-User Security Test 3: User A attempts to scan using User B's account ID
        cross_sync = requests.post(f"{self.BASE_URL}/api/emails/sync?account_id={acc_b_id}", headers=self.headers_a)
        self.assertEqual(cross_sync.status_code, 400)

        # Cross-User Security Test 4: User A attempts to disconnect User B's account
        cross_disc = requests.post(f"{self.BASE_URL}/api/auth/accounts/{acc_b_id}/disconnect", headers=self.headers_a)
        self.assertEqual(cross_disc.status_code, 404)

        # Check Dashboard Stats Isolation
        stats_a = requests.get(f"{self.BASE_URL}/api/dashboard/stats", headers=self.headers_a).json()
        stats_b = requests.get(f"{self.BASE_URL}/api/dashboard/stats", headers=self.headers_b).json()
        self.assertEqual(stats_a["connected_accounts_count"], 1)
        self.assertEqual(stats_b["connected_accounts_count"], 1)
        self.assertEqual(stats_a["connected_email"], self.email_1)
        self.assertEqual(stats_b["connected_email"], email_b)

    def test_07_revoked_or_expired_token_handling(self):
        """Requirement 7: Gracefully handle expired or revoked tokens with 401 and clean status."""
        temp_user = f"temp_user_{uuid.uuid4().hex[:6]}"
        headers_temp = {"X-User-ID": temp_user}

        conn_res = requests.post(f"{self.BASE_URL}/api/auth/accounts/demo-connect", headers=headers_temp, json={
            "email": "revoked_account@gmail.com"
        })
        acc_id = conn_res.json()["account"]["id"]

        # Simulate Google token revocation by updating status via API
        stat_res = requests.post(f"{self.BASE_URL}/api/auth/accounts/{acc_id}/status", headers=headers_temp, json={
            "status": "revoked",
            "error_message": "Simulated revocation test"
        })
        self.assertEqual(stat_res.status_code, 200)

        # Attempt to sync should return 401 indicating re-authorization required
        sync_res = requests.post(f"{self.BASE_URL}/api/emails/sync?account_id={acc_id}", headers=headers_temp)
        self.assertEqual(sync_res.status_code, 401)
        self.assertIn("revoked", sync_res.json()["detail"].lower())

if __name__ == "__main__":
    unittest.main()
