import os
import sys
import unittest
import uuid
import time
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient
import jwt

# Add root and backend to sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)
backend_dir = os.path.join(root_dir, "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.main import app
from app.core.config import settings
from app.core.security import (
    create_access_token, 
    verify_access_token, 
    generate_oauth_state, 
    verify_oauth_state,
    encrypt_token,
    decrypt_token
)
from database.connection import db_service, DatabaseService

class TestAuthSecurityAndProduction(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.user_a = f"security_user_a_{uuid.uuid4().hex[:6]}"
        cls.user_b = f"security_user_b_{uuid.uuid4().hex[:6]}"
        
        # Valid signed JWT tokens
        cls.token_a = create_access_token(user_id=cls.user_a, email=f"{cls.user_a}@corp.local")
        cls.token_b = create_access_token(user_id=cls.user_b, email=f"{cls.user_b}@corp.local")

        cls.headers_a = {"Authorization": f"Bearer {cls.token_a}"}
        cls.headers_b = {"Authorization": f"Bearer {cls.token_b}"}

    def test_01_unauthenticated_requests_return_401(self):
        """Verify that requests missing Bearer tokens are rejected with 401 Unauthorized."""
        endpoints = [
            ("GET", "/api/dashboard/stats"),
            ("GET", "/api/emails"),
            ("GET", "/api/auth/accounts"),
            ("GET", "/api/auth/status"),
            ("GET", "/api/auth/me"),
            ("POST", "/api/emails/sync"),
            ("POST", "/api/dashboard/reset")
        ]
        for method, path in endpoints:
            if method == "GET":
                res = self.client.get(path)
            else:
                res = self.client.post(path)
            self.assertEqual(
                res.status_code, 401, 
                f"Expected 401 for unauthenticated {method} {path}, got {res.status_code}"
            )
            self.assertIn("WWW-Authenticate", res.headers)

    def test_02_client_supplied_user_id_header_ignored_without_jwt(self):
        """Verify client cannot spoof identity by passing X-User-ID without valid JWT."""
        spoofed_headers = {"X-User-ID": "admin_victim"}
        res = self.client.get("/api/dashboard/stats", headers=spoofed_headers)
        self.assertEqual(res.status_code, 401, "Server must not trust client-supplied X-User-ID header")

    def test_03_invalid_and_tampered_jwt_rejected(self):
        """Verify tampered or forged JWT signature is rejected with 401."""
        # Forged token signed with different key
        forged_payload = {
            "sub": "attacker_user",
            "iat": int(time.time()),
            "exp": int(time.time()) + 3600,
            "iss": "ai-phishing-shield"
        }
        forged_token = jwt.encode(forged_payload, "completely_wrong_secret_key_123456", algorithm="HS256")
        res = self.client.get("/api/auth/me", headers={"Authorization": f"Bearer {forged_token}"})
        self.assertEqual(res.status_code, 401, "Forged token signature must return 401")

        # Malformed garbage token
        res_malformed = self.client.get("/api/auth/me", headers={"Authorization": "Bearer not.a.valid.jwt"})
        self.assertEqual(res_malformed.status_code, 401, "Malformed token must return 401")

    def test_04_expired_jwt_rejected(self):
        """Verify expired JWT is rejected with 401."""
        expired_token = create_access_token(
            user_id="expired_tester",
            expires_delta=timedelta(seconds=-10)
        )
        res = self.client.get("/api/auth/me", headers={"Authorization": f"Bearer {expired_token}"})
        self.assertEqual(res.status_code, 401, "Expired token must return 401")

    def test_05_valid_jwt_authenticates_user_identity(self):
        """Verify valid JWT grants access and verifies server-side identity."""
        res = self.client.get("/api/auth/me", headers=self.headers_a)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["user_id"], self.user_a)

    def test_06_cross_user_data_isolation(self):
        """Verify User A's scanned emails and threats cannot be read or deleted by User B."""
        # 1. User A analyzes and saves a phishing email
        email_payload = {
            "subject": "Confidential Salary Report",
            "sender": "payroll@spoofed-company.com",
            "body": "Download payroll records immediately: http://spoofed-company.com/payroll",
            "save_result": True
        }
        create_res = self.client.post("/api/emails/analyze-custom", json=email_payload, headers=self.headers_a)
        self.assertEqual(create_res.status_code, 200)
        created_email = create_res.json()
        email_id = created_email["id"]

        # 2. User A can see their email
        list_a = self.client.get("/api/emails", headers=self.headers_a).json()
        self.assertTrue(any(e["id"] == email_id for e in list_a["items"]))

        # 3. User B CANNOT see User A's email in list or details
        list_b = self.client.get("/api/emails", headers=self.headers_b).json()
        self.assertFalse(any(e["id"] == email_id for e in list_b["items"]))

        detail_b = self.client.get(f"/api/emails/{email_id}", headers=self.headers_b)
        self.assertEqual(detail_b.status_code, 404, "User B should receive 404 when querying User A's email")

        # 4. User B CANNOT delete User A's email
        del_b = self.client.delete(f"/api/emails/{email_id}", headers=self.headers_b)
        self.assertEqual(del_b.status_code, 404, "User B should receive 404 when attempting to delete User A's email")

        # 5. User A CAN delete their own email
        del_a = self.client.delete(f"/api/emails/{email_id}", headers=self.headers_a)
        self.assertEqual(del_a.status_code, 200)

    def test_07_gmail_account_ownership_and_isolation(self):
        """Verify User B cannot access, select, or disconnect User A's connected Gmail accounts."""
        # 1. Connect a simulated account for User A
        conn_res = self.client.post(
            "/api/auth/accounts/demo-connect",
            json={"email": f"{self.user_a}@gmail.com", "display_name": "User A Mailbox"},
            headers=self.headers_a
        )
        self.assertEqual(conn_res.status_code, 200)
        account_a = conn_res.json()["account"]
        account_id_a = account_a["id"]

        # 2. User B list accounts does NOT include User A's account
        accounts_b = self.client.get("/api/auth/accounts", headers=self.headers_b).json()
        self.assertFalse(any(a["id"] == account_id_a for a in accounts_b["accounts"]))

        # 3. User B cannot select User A's account
        select_b = self.client.post(f"/api/auth/accounts/{account_id_a}/select", headers=self.headers_b)
        self.assertEqual(select_b.status_code, 404, "User B cannot select User A's account")

        # 4. User B cannot disconnect User A's account
        disc_b = self.client.post(f"/api/auth/accounts/{account_id_a}/disconnect", headers=self.headers_b)
        self.assertEqual(disc_b.status_code, 404, "User B cannot disconnect User A's account")

        # 5. User A CAN disconnect their own account
        disc_a = self.client.post(f"/api/auth/accounts/{account_id_a}/disconnect", headers=self.headers_a)
        self.assertEqual(disc_a.status_code, 200)

    def test_08_oauth_state_tampering_and_expiration(self):
        """Verify Google OAuth callback rejects tampered or expired state tokens."""
        # Tampered state string (do not auto-follow redirects to inspect 307 location)
        res_tampered = self.client.get(
            "/api/auth/google/callback",
            params={"code": "dummy_code", "state": "tampered_ciphertext_xyz"},
            follow_redirects=False
        )
        self.assertEqual(res_tampered.status_code, 307)
        self.assertIn("auth_error=InvalidOrExpiredState", res_tampered.headers["location"])

        # Missing state string
        res_no_state = self.client.get(
            "/api/auth/google/callback",
            params={"code": "dummy_code"},
            follow_redirects=False
        )
        self.assertEqual(res_no_state.status_code, 307)
        self.assertIn("auth_error=MissingState", res_no_state.headers["location"])

    def test_09_tokens_never_exposed_in_api_responses(self):
        """Verify OAuth access/refresh tokens and encryption keys are stripped from responses."""
        # Connect demo mailbox for User A
        self.client.post(
            "/api/auth/accounts/demo-connect",
            json={"email": f"{self.user_a}_safety@gmail.com"},
            headers=self.headers_a
        )

        # Inspect /auth/accounts
        res = self.client.get("/api/auth/accounts", headers=self.headers_a).json()
        for acc in res["accounts"]:
            self.assertNotIn("access_token", acc)
            self.assertNotIn("refresh_token", acc)
            self.assertNotIn("access_token_encrypted", acc)
            self.assertNotIn("refresh_token_encrypted", acc)

        # Inspect /auth/status
        status_res = self.client.get("/api/auth/status", headers=self.headers_a).json()
        self.assertNotIn("access_token", status_res)
        self.assertNotIn("refresh_token", status_res)

    def test_10_production_database_enforcement(self):
        """Verify that in production mode, failing to connect to MongoDB raises RuntimeError."""
        import asyncio
        test_db_svc = DatabaseService()

        # Temporarily mock production environment
        original_env = settings.ENVIRONMENT
        original_require = settings.REQUIRE_PERSISTENT_DB
        try:
            settings.ENVIRONMENT = "production"
            settings.REQUIRE_PERSISTENT_DB = True

            # Attempting to connect to an unreachable port in production MUST raise RuntimeError
            async def run_failing_connect():
                await test_db_svc.connect(mongodb_url="mongodb://127.0.0.1:9999", db_name="test_prod_fail")

            with self.assertRaises(RuntimeError) as cm:
                asyncio.run(run_failing_connect())
            
            self.assertIn("Production persistent database connection failed", str(cm.exception))
        finally:
            if test_db_svc.client:
                test_db_svc.client.close()
            settings.ENVIRONMENT = original_env
            settings.REQUIRE_PERSISTENT_DB = original_require

    def test_11_oauth_route_compatibility_and_redirects(self):
        """Verify un-prefixed OAuth routes gracefully redirect to canonical /api/auth routes preserving query params."""
        # 1. Un-prefixed /auth/google/login redirect
        res_login = self.client.get("/auth/google/login?prompt=select_account", follow_redirects=False)
        self.assertEqual(res_login.status_code, 307)
        self.assertEqual(res_login.headers["location"], "/api/auth/google/login?prompt=select_account")

        # 2. Un-prefixed /auth/google/callback redirect
        res_cb = self.client.get("/auth/google/callback?code=test_code_123&state=test_state_456", follow_redirects=False)
        self.assertEqual(res_cb.status_code, 307)
        self.assertEqual(res_cb.headers["location"], "/api/auth/google/callback?code=test_code_123&state=test_state_456")

        # 3. Canonical /api/auth/google/login initiates Google OAuth redirect
        orig_client_id = settings.GOOGLE_CLIENT_ID
        try:
            settings.GOOGLE_CLIENT_ID = "mock_client_id_123.apps.googleusercontent.com"
            res_canonical = self.client.get("/api/auth/google/login?prompt=select_account", follow_redirects=False)
            self.assertEqual(res_canonical.status_code, 307)
            self.assertTrue(res_canonical.headers["location"].startswith("https://accounts.google.com/o/oauth2/v2/auth"))
            self.assertIn("prompt=select_account", res_canonical.headers["location"])
            self.assertIn("mock_client_id_123", res_canonical.headers["location"])
        finally:
            settings.GOOGLE_CLIENT_ID = orig_client_id

    def test_12_production_oauth_redirect_and_guard(self):
        """Verify production OAuth configuration guards and automatic Render URL derivation."""
        orig_env = settings.ENVIRONMENT
        orig_raw_google = settings.RAW_GOOGLE_REDIRECT_URI
        orig_raw_frontend = settings.RAW_FRONTEND_REDIRECT_URL
        orig_render_url = os.environ.get("RENDER_EXTERNAL_URL")
        orig_render = os.environ.get("RENDER")

        try:
            # 1. Development mode defaults to localhost safely
            settings.ENVIRONMENT = "development"
            settings.RAW_GOOGLE_REDIRECT_URI = None
            settings.RAW_FRONTEND_REDIRECT_URL = None
            os.environ.pop("RENDER_EXTERNAL_URL", None)
            os.environ.pop("RENDER", None)
            self.assertEqual(settings.GOOGLE_REDIRECT_URI, "http://localhost:8000/api/auth/google/callback")
            self.assertEqual(settings.FRONTEND_REDIRECT_URL, "http://localhost:5173")

            # 2. Render environment automatically derives production URLs
            os.environ["RENDER_EXTERNAL_URL"] = "https://phishshield-api-xgbd.onrender.com"
            os.environ["RENDER"] = "true"
            self.assertEqual(settings.GOOGLE_REDIRECT_URI, "https://phishshield-api-xgbd.onrender.com/api/auth/google/callback")
            self.assertEqual(settings.FRONTEND_REDIRECT_URL, "https://ai-email-phising-detector.onrender.com")

            # 3. Production mode without Render URL or explicit HTTPS raises RuntimeError on localhost
            os.environ.pop("RENDER_EXTERNAL_URL", None)
            os.environ.pop("RENDER", None)
            settings.ENVIRONMENT = "production"
            settings.RAW_GOOGLE_REDIRECT_URI = "http://localhost:8000/api/auth/google/callback"
            with self.assertRaises(RuntimeError) as cm:
                _ = settings.GOOGLE_REDIRECT_URI
            self.assertIn("cannot point to localhost", str(cm.exception))

            settings.RAW_FRONTEND_REDIRECT_URL = "http://localhost:5173"
            with self.assertRaises(RuntimeError) as cm_fe:
                _ = settings.FRONTEND_REDIRECT_URL
            self.assertIn("cannot point to localhost", str(cm_fe.exception))

            # 4. Verified production OAuth initiation uses canonical production callback URL
            settings.RAW_GOOGLE_REDIRECT_URI = "https://phishshield-api-xgbd.onrender.com/api/auth/google/callback"
            settings.RAW_FRONTEND_REDIRECT_URL = "https://ai-email-phising-detector.onrender.com"
            settings.GOOGLE_CLIENT_ID = "prod_client_id.apps.googleusercontent.com"
            res = self.client.get("/api/auth/google/login?prompt=select_account", follow_redirects=False)
            self.assertEqual(res.status_code, 307)
            self.assertIn("redirect_uri=https://phishshield-api-xgbd.onrender.com/api/auth/google/callback", res.headers["location"])
        finally:
            settings.ENVIRONMENT = orig_env
            settings.RAW_GOOGLE_REDIRECT_URI = orig_raw_google
            settings.RAW_FRONTEND_REDIRECT_URL = orig_raw_frontend
            if orig_render_url is not None:
                os.environ["RENDER_EXTERNAL_URL"] = orig_render_url
            else:
                os.environ.pop("RENDER_EXTERNAL_URL", None)
            if orig_render is not None:
                os.environ["RENDER"] = orig_render
            else:
                os.environ.pop("RENDER", None)

if __name__ == "__main__":
    unittest.main()
