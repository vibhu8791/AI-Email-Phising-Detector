import os
import json
import logging
import email.utils
import uuid
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
import asyncio

logger = logging.getLogger("app.database")

# Fixed timezone offset for Asia/Kolkata (IST = UTC+05:30)
IST = timezone(timedelta(hours=5, minutes=30), name="IST")

def parse_to_utc(date_str: Optional[str], fallback_iso: Optional[str] = None) -> datetime:
    """Parse any RFC 2822, ISO 8601, or SQL date string into a timezone-aware UTC datetime."""
    if date_str:
        try:
            dt = email.utils.parsedate_to_datetime(date_str)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
        except Exception:
            pass
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S.%f"):
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.replace(tzinfo=timezone.utc)
            except Exception:
                pass
        try:
            dt = datetime.fromisoformat(date_str)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
        except Exception:
            pass
    if fallback_iso:
        try:
            dt = datetime.fromisoformat(fallback_iso)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
        except Exception:
            pass
    return datetime.now(timezone.utc)

def format_to_ist(dt_utc: datetime) -> str:
    """Format UTC datetime to consistent Asia/Kolkata (IST) display string."""
    return dt_utc.astimezone(IST).strftime("%d %b %Y, %I:%M %p IST")

def normalize_email_timestamps(email_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Ensure consistent timestamp_utc, timestamp_epoch, and date_display (IST) fields."""
    dt_utc = parse_to_utc(email_dict.get("date"), email_dict.get("created_at"))
    email_dict["timestamp_utc"] = dt_utc.strftime("%Y-%m-%dT%H:%M:%SZ")
    email_dict["timestamp_epoch"] = float(dt_utc.timestamp())
    email_dict["date_display"] = format_to_ist(dt_utc)
    # Ensure date has a readable value for legacy consumers
    if not email_dict.get("date"):
        email_dict["date"] = email_dict["date_display"]
    return email_dict

def get_email_sort_key(email_dict: Dict[str, Any]) -> float:
    """Extract numeric epoch seconds for sorting by actual timestamp (newest first)."""
    if "timestamp_epoch" in email_dict and isinstance(email_dict["timestamp_epoch"], (int, float)):
        return float(email_dict["timestamp_epoch"])
    dt_utc = parse_to_utc(email_dict.get("date"), email_dict.get("created_at"))
    return float(dt_utc.timestamp())

def sanitize_account(acc: Dict[str, Any]) -> Dict[str, Any]:
    """Strip sensitive tokens before exposing account metadata to frontend or logs."""
    return {
        "id": acc.get("id"),
        "user_id": acc.get("user_id", "default_user"),
        "email": acc.get("email"),
        "display_name": acc.get("display_name") or acc.get("email"),
        "status": acc.get("status", "active"),
        "error_message": acc.get("error_message"),
        "mode": acc.get("mode", "live"),
        "is_default": acc.get("is_default", False),
        "connected_at": acc.get("connected_at"),
        "last_synced_at": acc.get("last_synced_at")
    }

class DatabaseService:
    def __init__(self):
        self.client = None
        self.db = None
        self.use_fallback = False
        self.fallback_file = os.path.join(os.path.dirname(__file__), "local_storage.json")
        self._memory_data = {
            "scanned_emails": [],
            "threat_logs": [],
            "user_tokens": None,
            "connected_accounts": []
        }
        self._load_fallback()

    def _load_fallback(self):
        try:
            if os.path.exists(self.fallback_file):
                with open(self.fallback_file, "r", encoding="utf-8") as f:
                    self._memory_data = json.load(f)
                
                # Ensure connected_accounts structure exists
                if "connected_accounts" not in self._memory_data or not isinstance(self._memory_data["connected_accounts"], list):
                    self._memory_data["connected_accounts"] = []
                
                # Migrate legacy user_tokens to connected_accounts if needed
                legacy_token = self._memory_data.get("user_tokens")
                if legacy_token and isinstance(legacy_token, dict) and legacy_token.get("email") and not self._memory_data["connected_accounts"]:
                    self._memory_data["connected_accounts"].append({
                        "id": "acc_default",
                        "user_id": legacy_token.get("user_id", "default_user"),
                        "email": legacy_token.get("email"),
                        "display_name": legacy_token.get("email"),
                        "access_token_encrypted": legacy_token.get("access_token_encrypted", ""),
                        "refresh_token_encrypted": legacy_token.get("refresh_token_encrypted"),
                        "expires_at": legacy_token.get("expires_at"),
                        "scopes": legacy_token.get("scopes", ["https://www.googleapis.com/auth/gmail.readonly"]),
                        "status": "active",
                        "mode": legacy_token.get("mode", "live"),
                        "is_default": True,
                        "connected_at": legacy_token.get("connected_at") or datetime.now(timezone.utc).isoformat(),
                        "last_synced_at": legacy_token.get("last_synced_at")
                    })

                # Ensure all emails have user_id and normalized timestamps
                emails = self._memory_data.get("scanned_emails", [])
                for em in emails:
                    if not em.get("user_id"):
                        em["user_id"] = "default_user"
                    normalize_email_timestamps(em)
                emails.sort(key=get_email_sort_key, reverse=True)
                self._memory_data["scanned_emails"] = emails

                # Ensure all threats have user_id
                threats = self._memory_data.get("threat_logs", [])
                for th in threats:
                    if not th.get("user_id"):
                        th["user_id"] = "default_user"
                self._memory_data["threat_logs"] = threats

                self._persist_fallback()
        except Exception as e:
            logger.warning(f"Could not load fallback file: {e}")

    def _persist_fallback(self):
        try:
            with open(self.fallback_file, "w", encoding="utf-8") as f:
                json.dump(self._memory_data, f, default=str, indent=2)
        except Exception as e:
            logger.warning(f"Could not persist fallback: {e}")

    async def connect(self, mongodb_url: str = "mongodb://localhost:27017", db_name: str = "phishing_detector"):
        from app.core.config import settings
        is_production = settings.is_production

        try:
            from motor.motor_asyncio import AsyncIOMotorClient
            logger.info(f"Attempting connection to MongoDB at {mongodb_url}...")
            self.client = AsyncIOMotorClient(mongodb_url, serverSelectionTimeoutMS=2000)
            await self.client.admin.command('ping')
            self.db = self.client[db_name]
            self.use_fallback = False
            logger.info(f"Successfully connected to MongoDB: database '{db_name}'")
        except Exception as e:
            if is_production:
                logger.critical(f"FATAL: Production database connection failed: {e}. Persistent database is required in production.")
                raise RuntimeError(
                    f"Production persistent database connection failed: {e}. "
                    "Silent fallback to local JSON storage is strictly prohibited in production environments."
                ) from e
            logger.warning(f"MongoDB not available ({e}). Using resilient local storage fallback (development mode only).")
            self.use_fallback = True

    # =========================================================================
    # MULTI-ACCOUNT MANAGEMENT
    # =========================================================================

    async def get_account_by_id(self, account_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve account by ID across all records (used for ownership verification)."""
        if not self.use_fallback and self.db is not None:
            try:
                doc = await self.db.connected_accounts.find_one({"id": account_id})
                if doc and "_id" in doc:
                    del doc["_id"]
                return doc
            except Exception as e:
                logger.error(f"MongoDB error in get_account_by_id: {e}")

        for a in self._memory_data.get("connected_accounts", []):
            if a.get("id") == account_id:
                return a
        return None

    async def save_account(self, account_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Save or update a connected Gmail account for a specific user."""
        user_id = account_dict.get("user_id", "default_user")
        email = account_dict.get("email")
        if not account_dict.get("id"):
            account_dict["id"] = f"acc_{uuid.uuid4().hex[:12]}"
        if not account_dict.get("connected_at"):
            account_dict["connected_at"] = datetime.now(timezone.utc).isoformat()
        if not account_dict.get("status"):
            account_dict["status"] = "active"

        if not self.use_fallback and self.db is not None:
            try:
                # Check if this is the first account for user
                existing_count = await self.db.connected_accounts.count_documents({"user_id": user_id})
                if existing_count == 0:
                    account_dict["is_default"] = True
                await self.db.connected_accounts.update_one(
                    {"user_id": user_id, "email": email},
                    {"$set": account_dict},
                    upsert=True
                )
                return sanitize_account(account_dict)
            except Exception as e:
                logger.error(f"MongoDB error in save_account: {e}. Falling back.")

        # Fallback local store
        accounts = self._memory_data.setdefault("connected_accounts", [])
        user_accounts = [a for a in accounts if a.get("user_id", "default_user") == user_id]
        
        # If user has no existing accounts, make this account the default
        if len(user_accounts) == 0:
            account_dict["is_default"] = True

        existing_idx = next(
            (i for i, a in enumerate(accounts) 
             if a.get("user_id", "default_user") == user_id and a.get("email") == email),
            None
        )

        if existing_idx is not None:
            # Preserve existing ID and default flag if not specified
            account_dict["id"] = accounts[existing_idx].get("id", account_dict["id"])
            if "is_default" not in account_dict:
                account_dict["is_default"] = accounts[existing_idx].get("is_default", False)
            accounts[existing_idx].update(account_dict)
        else:
            accounts.append(account_dict)

        # Update legacy user_tokens for backward compatibility if default
        if account_dict.get("is_default"):
            self._memory_data["user_tokens"] = account_dict

        self._persist_fallback()
        return sanitize_account(account_dict)

    async def get_accounts(self, user_id: str = "default_user") -> List[Dict[str, Any]]:
        """Retrieve all connected accounts for a specific user, tokens stripped for security."""
        if not self.use_fallback and self.db is not None:
            try:
                cursor = self.db.connected_accounts.find({"user_id": user_id})
                items = await cursor.to_list(length=100)
                return [sanitize_account(a) for a in items]
            except Exception as e:
                logger.error(f"MongoDB error in get_accounts: {e}. Falling back.")

        accounts = self._memory_data.get("connected_accounts", [])
        return [sanitize_account(a) for a in accounts if a.get("user_id", "default_user") == user_id]

    async def get_account(self, user_id: str = "default_user", account_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Retrieve full account record (internal use only, includes encrypted tokens)."""
        if not self.use_fallback and self.db is not None:
            try:
                query = {"user_id": user_id}
                if account_id:
                    query["id"] = account_id
                else:
                    query["is_default"] = True
                doc = await self.db.connected_accounts.find_one(query)
                if not doc and not account_id:
                    doc = await self.db.connected_accounts.find_one({"user_id": user_id})
                if doc and "_id" in doc:
                    del doc["_id"]
                return doc
            except Exception as e:
                logger.error(f"MongoDB error in get_account: {e}. Falling back.")

        accounts = [a for a in self._memory_data.get("connected_accounts", []) if a.get("user_id", "default_user") == user_id]
        if account_id:
            for a in accounts:
                if a.get("id") == account_id:
                    return a
            return None
        # Return default or first account
        default_acc = next((a for a in accounts if a.get("is_default")), None)
        return default_acc if default_acc else (accounts[0] if accounts else None)

    async def set_default_account(self, user_id: str = "default_user", account_id: str = "") -> bool:
        """Set the active/selected account for scanning for this user."""
        if not self.use_fallback and self.db is not None:
            try:
                await self.db.connected_accounts.update_many(
                    {"user_id": user_id},
                    {"$set": {"is_default": False}}
                )
                res = await self.db.connected_accounts.update_one(
                    {"user_id": user_id, "id": account_id},
                    {"$set": {"is_default": True}}
                )
                return res.modified_count > 0
            except Exception as e:
                logger.error(f"MongoDB error in set_default_account: {e}. Falling back.")

        accounts = self._memory_data.get("connected_accounts", [])
        found = False
        default_account = None
        for a in accounts:
            if a.get("user_id", "default_user") == user_id:
                if a.get("id") == account_id:
                    a["is_default"] = True
                    default_account = a
                    found = True
                else:
                    a["is_default"] = False

        if default_account:
            self._memory_data["user_tokens"] = default_account
        self._persist_fallback()
        return found

    async def disconnect_account(self, user_id: str = "default_user", account_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Disconnect and delete a connected Gmail account belonging to user_id."""
        target = await self.get_account(user_id=user_id, account_id=account_id)
        if not target:
            return None

        target_id = target.get("id")

        if not self.use_fallback and self.db is not None:
            try:
                await self.db.connected_accounts.delete_one({"user_id": user_id, "id": target_id})
                # If deleted account was default, promote another account if available
                if target.get("is_default"):
                    remaining = await self.db.connected_accounts.find_one({"user_id": user_id})
                    if remaining:
                        await self.db.connected_accounts.update_one({"id": remaining["id"]}, {"$set": {"is_default": True}})
                return target
            except Exception as e:
                logger.error(f"MongoDB error in disconnect_account: {e}. Falling back.")

        # Fallback
        accounts = self._memory_data.get("connected_accounts", [])
        self._memory_data["connected_accounts"] = [
            a for a in accounts 
            if not (a.get("user_id", "default_user") == user_id and a.get("id") == target_id)
        ]

        # If removed account was default, promote remaining account
        remaining_user_accounts = [
            a for a in self._memory_data["connected_accounts"] 
            if a.get("user_id", "default_user") == user_id
        ]
        if remaining_user_accounts and not any(a.get("is_default") for a in remaining_user_accounts):
            remaining_user_accounts[0]["is_default"] = True
            self._memory_data["user_tokens"] = remaining_user_accounts[0]
        elif not remaining_user_accounts:
            self._memory_data["user_tokens"] = None

        self._persist_fallback()
        return target

    async def update_account_status(self, user_id: str, account_id: str, status: str, error_message: Optional[str] = None):
        """Update connection status (e.g. active, expired, revoked, error) of an account."""
        if not self.use_fallback and self.db is not None:
            try:
                await self.db.connected_accounts.update_one(
                    {"user_id": user_id, "id": account_id},
                    {"$set": {"status": status, "error_message": error_message}}
                )
                return
            except Exception as e:
                logger.error(f"MongoDB error in update_account_status: {e}. Falling back.")

        for a in self._memory_data.get("connected_accounts", []):
            if a.get("user_id", "default_user") == user_id and a.get("id") == account_id:
                a["status"] = status
                a["error_message"] = error_message
                break
        self._persist_fallback()

    # =========================================================================
    # EMAIL & THREAT MANAGEMENT (WITH USER ISOLATION)
    # =========================================================================

    async def save_email(self, email_dict: Dict[str, Any], user_id: str = "default_user") -> Dict[str, Any]:
        """Save scanned email record isolated under the user's workspace."""
        email_dict["user_id"] = user_id
        normalize_email_timestamps(email_dict)

        if not self.use_fallback and self.db is not None:
            try:
                await self.db.scanned_emails.update_one(
                    {"id": email_dict["id"], "user_id": user_id},
                    {"$set": email_dict},
                    upsert=True
                )
                return email_dict
            except Exception as e:
                logger.error(f"MongoDB error in save_email: {e}. Falling back.")

        existing_idx = next(
            (i for i, em in enumerate(self._memory_data["scanned_emails"]) 
             if em.get("id") == email_dict["id"] and em.get("user_id", "default_user") == user_id), 
            None
        )
        if existing_idx is not None:
            self._memory_data["scanned_emails"][existing_idx] = email_dict
        else:
            self._memory_data["scanned_emails"].append(email_dict)

        self._memory_data["scanned_emails"].sort(key=get_email_sort_key, reverse=True)
        self._persist_fallback()
        return email_dict

    async def get_emails(
        self,
        user_id: str = "default_user",
        account_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
        classification: Optional[str] = None,
        search: Optional[str] = None
    ) -> Dict[str, Any]:
        """Retrieve scanned emails strictly scoped to user_id (and optional account_id)."""
        if not self.use_fallback and self.db is not None:
            try:
                query = {"user_id": user_id}
                if account_id:
                    query["account_id"] = account_id
                if classification and classification.upper() != "ALL":
                    query["classification"] = classification.upper()
                if search:
                    query["$or"] = [
                        {"subject": {"$regex": search, "$options": "i"}},
                        {"sender": {"$regex": search, "$options": "i"}},
                        {"body_plain": {"$regex": search, "$options": "i"}}
                    ]
                total = await self.db.scanned_emails.count_documents(query)
                cursor = self.db.scanned_emails.find(query).sort("timestamp_epoch", -1).skip(skip).limit(limit)
                items = await cursor.to_list(length=limit)
                for item in items:
                    if "_id" in item:
                        del item["_id"]
                return {"items": items, "total": total}
            except Exception as e:
                logger.error(f"MongoDB error in get_emails: {e}. Falling back.")

        # Fallback in-memory
        items = [e for e in self._memory_data["scanned_emails"] if e.get("user_id", "default_user") == user_id]
        if account_id:
            items = [e for e in items if e.get("account_id") == account_id]
        if classification and classification.upper() != "ALL":
            items = [i for i in items if i.get("classification") == classification.upper()]
        if search:
            s = search.lower()
            items = [i for i in items if s in i.get("subject", "").lower() or s in i.get("sender", "").lower() or s in i.get("body_plain", "").lower()]

        items.sort(key=get_email_sort_key, reverse=True)
        total = len(items)
        paged = items[skip:skip+limit]
        return {"items": paged, "total": total}

    async def get_email_by_id(self, email_id: str, user_id: str = "default_user") -> Optional[Dict[str, Any]]:
        """Retrieve email detail only if owned by user_id."""
        if not self.use_fallback and self.db is not None:
            try:
                doc = await self.db.scanned_emails.find_one({"id": email_id, "user_id": user_id})
                if doc and "_id" in doc:
                    del doc["_id"]
                return doc
            except Exception as e:
                logger.error(f"MongoDB error in get_email_by_id: {e}. Falling back.")

        for em in self._memory_data["scanned_emails"]:
            if em.get("id") == email_id and em.get("user_id", "default_user") == user_id:
                return em
        return None

    async def delete_email(self, email_id: str, user_id: str = "default_user") -> bool:
        """Delete an email record only if owned by user_id."""
        if not self.use_fallback and self.db is not None:
            try:
                res = await self.db.scanned_emails.delete_one({"id": email_id, "user_id": user_id})
                await self.db.threat_logs.delete_many({"email_id": email_id, "user_id": user_id})
                return res.deleted_count > 0
            except Exception as e:
                logger.error(f"MongoDB error in delete_email: {e}. Falling back.")

        prev_count = len(self._memory_data["scanned_emails"])
        self._memory_data["scanned_emails"] = [
            e for e in self._memory_data["scanned_emails"] 
            if not (e.get("id") == email_id and e.get("user_id", "default_user") == user_id)
        ]
        self._memory_data["threat_logs"] = [
            t for t in self._memory_data["threat_logs"] 
            if not (t.get("email_id") == email_id and t.get("user_id", "default_user") == user_id)
        ]
        self._persist_fallback()
        return len(self._memory_data["scanned_emails"]) < prev_count

    async def save_threat(self, threat_dict: Dict[str, Any], user_id: str = "default_user"):
        """Save a threat log record scoped to user_id."""
        threat_dict["user_id"] = user_id
        if not self.use_fallback and self.db is not None:
            try:
                await self.db.threat_logs.insert_one(threat_dict)
                return
            except Exception as e:
                logger.error(f"MongoDB error in save_threat: {e}.")

        self._memory_data["threat_logs"].insert(0, threat_dict)
        if len(self._memory_data["threat_logs"]) > 100:
            self._memory_data["threat_logs"] = self._memory_data["threat_logs"][:100]
        self._persist_fallback()

    async def get_recent_threats(self, user_id: str = "default_user", limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve recent threats isolated for user_id."""
        if not self.use_fallback and self.db is not None:
            try:
                cursor = self.db.threat_logs.find({"user_id": user_id}).sort("timestamp", -1).limit(limit)
                items = await cursor.to_list(length=limit)
                for item in items:
                    if "_id" in item:
                        del item["_id"]
                return items
            except Exception as e:
                logger.error(f"MongoDB error in get_recent_threats: {e}.")

        user_threats = [t for t in self._memory_data["threat_logs"] if t.get("user_id", "default_user") == user_id]
        return user_threats[:limit]

    async def get_stats(self, user_id: str = "default_user") -> Dict[str, Any]:
        """Compute aggregate statistics strictly scoped to user_id."""
        emails = []
        if not self.use_fallback and self.db is not None:
            try:
                cursor = self.db.scanned_emails.find({"user_id": user_id}, {"classification": 1, "risk_score": 1})
                emails = await cursor.to_list(length=10000)
            except Exception as e:
                logger.error(f"MongoDB error in get_stats: {e}. Falling back.")
                emails = [e for e in self._memory_data["scanned_emails"] if e.get("user_id", "default_user") == user_id]
        else:
            emails = [e for e in self._memory_data["scanned_emails"] if e.get("user_id", "default_user") == user_id]

        total = len(emails)
        safe = sum(1 for e in emails if e.get("classification") == "SAFE")
        suspicious = sum(1 for e in emails if e.get("classification") == "SUSPICIOUS")
        phishing = sum(1 for e in emails if e.get("classification") == "PHISHING")
        avg_risk = round(sum(e.get("risk_score", 0) for e in emails) / total, 1) if total > 0 else 0.0

        accounts = await self.get_accounts(user_id=user_id)
        default_account = next((a for a in accounts if a.get("is_default")), None) or (accounts[0] if accounts else None)

        return {
            "total_scanned": total,
            "safe_count": safe,
            "suspicious_count": suspicious,
            "phishing_count": phishing,
            "avg_risk_score": avg_risk,
            "is_gmail_connected": len(accounts) > 0,
            "connected_email": default_account.get("email") if default_account else None,
            "connected_accounts_count": len(accounts),
            "connected_accounts": accounts,
            "last_synced_at": default_account.get("last_synced_at") if default_account else None,
            "database_mode": "MongoDB" if not self.use_fallback else "Local Resilient Store"
        }

    async def clear_user_data(self, user_id: str = "default_user"):
        """Clear emails and threat logs for a specific user without impacting other users."""
        if not self.use_fallback and self.db is not None:
            try:
                await self.db.scanned_emails.delete_many({"user_id": user_id})
                await self.db.threat_logs.delete_many({"user_id": user_id})
            except Exception as e:
                logger.error(f"MongoDB error in clear_user_data: {e}.")

        self._memory_data["scanned_emails"] = [
            e for e in self._memory_data["scanned_emails"] if e.get("user_id", "default_user") != user_id
        ]
        self._memory_data["threat_logs"] = [
            t for t in self._memory_data["threat_logs"] if t.get("user_id", "default_user") != user_id
        ]
        self._persist_fallback()

    # Legacy support
    async def save_user_tokens(self, token_data: Dict[str, Any]):
        return await self.save_account(token_data)

    async def get_user_tokens(self, user_id: str = "default_user") -> Optional[Dict[str, Any]]:
        return await self.get_account(user_id=user_id)

    async def update_last_sync(self, email: str, sync_time: str):
        if not self.use_fallback and self.db is not None:
            try:
                await self.db.connected_accounts.update_many(
                    {"email": email},
                    {"$set": {"last_synced_at": sync_time}}
                )
            except Exception as e:
                logger.error(f"MongoDB error in update_last_sync: {e}.")

        for a in self._memory_data.get("connected_accounts", []):
            if a.get("email") == email:
                a["last_synced_at"] = sync_time
        if self._memory_data.get("user_tokens") and self._memory_data["user_tokens"].get("email") == email:
            self._memory_data["user_tokens"]["last_synced_at"] = sync_time
        self._persist_fallback()

    async def clear_user_tokens(self, user_id: str = "default_user"):
        return await self.disconnect_account(user_id=user_id)

db_service = DatabaseService()

db_service = DatabaseService()
