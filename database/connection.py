import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
import asyncio

logger = logging.getLogger("app.database")

class DatabaseService:
    def __init__(self):
        self.client = None
        self.db = None
        self.use_fallback = False
        self.fallback_file = os.path.join(os.path.dirname(__file__), "local_storage.json")
        self._memory_data = {
            "scanned_emails": [],
            "threat_logs": [],
            "user_tokens": None
        }
        self._load_fallback()

    def _load_fallback(self):
        try:
            if os.path.exists(self.fallback_file):
                with open(self.fallback_file, "r", encoding="utf-8") as f:
                    self._memory_data = json.load(f)
        except Exception as e:
            logger.warning(f"Could not load fallback file: {e}")

    def _persist_fallback(self):
        try:
            with open(self.fallback_file, "w", encoding="utf-8") as f:
                json.dump(self._memory_data, f, default=str, indent=2)
        except Exception as e:
            logger.warning(f"Could not persist fallback: {e}")

    async def connect(self, mongodb_url: str = "mongodb://localhost:27017", db_name: str = "phishing_detector"):
        try:
            from motor.motor_asyncio import AsyncIOMotorClient
            logger.info(f"Attempting connection to MongoDB at {mongodb_url}...")
            self.client = AsyncIOMotorClient(mongodb_url, serverSelectionTimeoutMS=2000)
            # Trigger server check
            await self.client.admin.command('ping')
            self.db = self.client[db_name]
            self.use_fallback = False
            logger.info(f"Successfully connected to MongoDB: database '{db_name}'")
        except Exception as e:
            logger.warning(f"MongoDB not available ({e}). Using resilient local storage fallback.")
            self.use_fallback = True

    async def save_email(self, email_dict: Dict[str, Any]) -> Dict[str, Any]:
        if not self.use_fallback and self.db is not None:
            try:
                # Upsert by id
                await self.db.scanned_emails.update_one(
                    {"id": email_dict["id"]},
                    {"$set": email_dict},
                    upsert=True
                )
                return email_dict
            except Exception as e:
                logger.error(f"MongoDB error in save_email: {e}. Falling back.")

        # Fallback in-memory
        existing_idx = next((i for i, em in enumerate(self._memory_data["scanned_emails"]) if em.get("id") == email_dict["id"]), None)
        if existing_idx is not None:
            self._memory_data["scanned_emails"][existing_idx] = email_dict
        else:
            self._memory_data["scanned_emails"].insert(0, email_dict)
        self._persist_fallback()
        return email_dict

    async def get_emails(
        self,
        skip: int = 0,
        limit: int = 50,
        classification: Optional[str] = None,
        search: Optional[str] = None
    ) -> Dict[str, Any]:
        if not self.use_fallback and self.db is not None:
            try:
                query = {}
                if classification and classification.upper() != "ALL":
                    query["classification"] = classification.upper()
                if search:
                    query["$or"] = [
                        {"subject": {"$regex": search, "$options": "i"}},
                        {"sender": {"$regex": search, "$options": "i"}},
                        {"body_plain": {"$regex": search, "$options": "i"}}
                    ]
                total = await self.db.scanned_emails.count_documents(query)
                cursor = self.db.scanned_emails.find(query).sort("created_at", -1).skip(skip).limit(limit)
                items = await cursor.to_list(length=limit)
                for item in items:
                    if "_id" in item:
                        del item["_id"]
                return {"items": items, "total": total}
            except Exception as e:
                logger.error(f"MongoDB error in get_emails: {e}. Falling back.")

        # Fallback
        items = list(self._memory_data["scanned_emails"])
        if classification and classification.upper() != "ALL":
            items = [i for i in items if i.get("classification") == classification.upper()]
        if search:
            s = search.lower()
            items = [i for i in items if s in i.get("subject", "").lower() or s in i.get("sender", "").lower() or s in i.get("body_plain", "").lower()]

        total = len(items)
        paged = items[skip:skip+limit]
        return {"items": paged, "total": total}

    async def get_email_by_id(self, email_id: str) -> Optional[Dict[str, Any]]:
        if not self.use_fallback and self.db is not None:
            try:
                doc = await self.db.scanned_emails.find_one({"id": email_id})
                if doc and "_id" in doc:
                    del doc["_id"]
                return doc
            except Exception as e:
                logger.error(f"MongoDB error in get_email_by_id: {e}. Falling back.")

        for em in self._memory_data["scanned_emails"]:
            if em.get("id") == email_id:
                return em
        return None

    async def delete_email(self, email_id: str) -> bool:
        if not self.use_fallback and self.db is not None:
            try:
                res = await self.db.scanned_emails.delete_one({"id": email_id})
                await self.db.threat_logs.delete_many({"email_id": email_id})
                return res.deleted_count > 0
            except Exception as e:
                logger.error(f"MongoDB error in delete_email: {e}. Falling back.")

        self._memory_data["scanned_emails"] = [e for e in self._memory_data["scanned_emails"] if e.get("id") != email_id]
        self._memory_data["threat_logs"] = [t for t in self._memory_data["threat_logs"] if t.get("email_id") != email_id]
        self._persist_fallback()
        return True

    async def save_threat(self, threat_dict: Dict[str, Any]):
        if not self.use_fallback and self.db is not None:
            try:
                await self.db.threat_logs.insert_one(threat_dict)
                return
            except Exception as e:
                logger.error(f"MongoDB error in save_threat: {e}.")

        self._memory_data["threat_logs"].insert(0, threat_dict)
        if len(self._memory_data["threat_logs"]) > 50:
            self._memory_data["threat_logs"] = self._memory_data["threat_logs"][:50]
        self._persist_fallback()

    async def get_recent_threats(self, limit: int = 10) -> List[Dict[str, Any]]:
        if not self.use_fallback and self.db is not None:
            try:
                cursor = self.db.threat_logs.find().sort("timestamp", -1).limit(limit)
                items = await cursor.to_list(length=limit)
                for item in items:
                    if "_id" in item:
                        del item["_id"]
                return items
            except Exception as e:
                logger.error(f"MongoDB error in get_recent_threats: {e}.")

        return self._memory_data["threat_logs"][:limit]

    async def get_stats(self) -> Dict[str, Any]:
        emails = []
        if not self.use_fallback and self.db is not None:
            try:
                cursor = self.db.scanned_emails.find({}, {"classification": 1, "risk_score": 1})
                emails = await cursor.to_list(length=10000)
            except Exception as e:
                logger.error(f"MongoDB error in get_stats: {e}. Falling back.")
                emails = self._memory_data["scanned_emails"]
        else:
            emails = self._memory_data["scanned_emails"]

        total = len(emails)
        safe = sum(1 for e in emails if e.get("classification") == "SAFE")
        suspicious = sum(1 for e in emails if e.get("classification") == "SUSPICIOUS")
        phishing = sum(1 for e in emails if e.get("classification") == "PHISHING")
        avg_risk = round(sum(e.get("risk_score", 0) for e in emails) / total, 1) if total > 0 else 0.0

        user_token = await self.get_user_tokens()
        is_connected = user_token is not None
        connected_email = user_token.get("email") if user_token else None
        last_synced = user_token.get("last_synced_at") if user_token else None

        return {
            "total_scanned": total,
            "safe_count": safe,
            "suspicious_count": suspicious,
            "phishing_count": phishing,
            "avg_risk_score": avg_risk,
            "is_gmail_connected": is_connected,
            "connected_email": connected_email,
            "last_synced_at": last_synced,
            "database_mode": "MongoDB" if not self.use_fallback else "Local Resilient Store"
        }

    async def save_user_tokens(self, token_data: Dict[str, Any]):
        if not self.use_fallback and self.db is not None:
            try:
                await self.db.users.update_one(
                    {"email": token_data["email"]},
                    {"$set": token_data},
                    upsert=True
                )
                return
            except Exception as e:
                logger.error(f"MongoDB error in save_user_tokens: {e}.")

        self._memory_data["user_tokens"] = token_data
        self._persist_fallback()

    async def get_user_tokens(self) -> Optional[Dict[str, Any]]:
        if not self.use_fallback and self.db is not None:
            try:
                doc = await self.db.users.find_one()
                if doc and "_id" in doc:
                    del doc["_id"]
                return doc
            except Exception as e:
                logger.error(f"MongoDB error in get_user_tokens: {e}.")

        return self._memory_data.get("user_tokens")

    async def update_last_sync(self, email: str, sync_time: str):
        if not self.use_fallback and self.db is not None:
            try:
                await self.db.users.update_one(
                    {"email": email},
                    {"$set": {"last_synced_at": sync_time}}
                )
                return
            except Exception as e:
                logger.error(f"MongoDB error in update_last_sync: {e}.")

        if self._memory_data.get("user_tokens"):
            self._memory_data["user_tokens"]["last_synced_at"] = sync_time
            self._persist_fallback()

    async def clear_user_tokens(self):
        if not self.use_fallback and self.db is not None:
            try:
                await self.db.users.delete_many({})
            except Exception as e:
                logger.error(f"MongoDB error in clear_user_tokens: {e}.")

        self._memory_data["user_tokens"] = None
        self._persist_fallback()

db_service = DatabaseService()
