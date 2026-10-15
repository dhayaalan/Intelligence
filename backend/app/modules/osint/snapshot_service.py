"""
OSINT Profile Snapshot, Change Detection, and Freshness Service.
Maintains versioned observations of extracted profile metadata,
detects real attribute changes over time, and supports manual investigator refresh.
"""

import time
import uuid
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone

from app.core.logging import app_logger
from app.modules.osint.models import (
    ProfileExtractionResult, ProfileSnapshot, ProfileChangeRecord,
    ExtractionStatus, PublicAccountStatistics
)
from app.infrastructure.mongodb.client import get_database


class ProfileSnapshotService:
    """
    Manages versioned profile snapshots in MongoDB/memory,
    identifying historical changes and enforcing metadata freshness policies.
    """

    def __init__(self):
        # In-memory LRU cache fallback
        self._memory_snapshots: Dict[str, List[ProfileSnapshot]] = {}

    async def record_observation(
        self,
        result: ProfileExtractionResult,
        tenant_id: str = "default"
    ) -> Tuple[ProfileSnapshot, List[ProfileChangeRecord]]:
        """
        Compares new extraction result against previous snapshot and records versioned observation.
        """
        profile_key = f"{result.platform_id}:{result.username.lower()}"
        memory_key = f"{tenant_id}:{profile_key}"
        previous_snapshots = await self.get_snapshot_history(result.platform_id, result.username, tenant_id=tenant_id)
        
        changes: List[ProfileChangeRecord] = []
        now_iso = datetime.now(timezone.utc).isoformat()

        if previous_snapshots:
            last_snap = previous_snapshots[-1]
            last_res = last_snap.result

            # Compare core attributes
            fields_to_check = [
                ("display_name", last_res.display_name, result.display_name),
                ("bio", last_res.bio, result.bio),
                ("avatar_url", last_res.avatar_url, result.avatar_url),
                ("location", last_res.location, result.location),
                ("followers", last_res.statistics.followers, result.statistics.followers),
                ("repositories_count", last_res.statistics.repositories_count, result.statistics.repositories_count),
                ("status", last_res.status.value, result.status.value),
            ]

            for field_name, old_val, new_val in fields_to_check:
                if old_val != new_val and (old_val is not None or new_val is not None):
                    changes.append(ProfileChangeRecord(
                        field_name=field_name,
                        previous_value=old_val,
                        new_value=new_val,
                        observed_at=now_iso,
                        source_provider=result.platform_id
                    ))

        snapshot_id = f"snp_{uuid.uuid4().hex[:12]}"
        snapshot = ProfileSnapshot(
            snapshot_id=snapshot_id,
            profile_key=profile_key,
            timestamp=now_iso,
            result=result,
            changes_from_previous=changes
        )

        # Persist to MongoDB if available
        mongo_db = get_database()
        if mongo_db is not None:
            try:
                doc = snapshot.dict()
                doc["tenant_id"] = tenant_id
                await mongo_db.profile_snapshots.insert_one(doc)
            except Exception as e:
                app_logger.warning(f"Could not persist profile snapshot to MongoDB: {e}")

        # Keep memory cache isolated by tenant
        if memory_key not in self._memory_snapshots:
            self._memory_snapshots[memory_key] = []
        self._memory_snapshots[memory_key].append(snapshot)
        if len(self._memory_snapshots[memory_key]) > 20:
            self._memory_snapshots[memory_key] = self._memory_snapshots[memory_key][-20:]

        return snapshot, changes

    async def get_snapshot_history(
        self,
        platform_id: str,
        username: str,
        tenant_id: str = "default"
    ) -> List[ProfileSnapshot]:
        """Retrieves historical snapshots for a profile scoped strictly to the authenticated tenant."""
        profile_key = f"{platform_id}:{username.lower()}"
        memory_key = f"{tenant_id}:{profile_key}"
        mongo_db = get_database()
        if mongo_db is not None:
            try:
                cursor = mongo_db.profile_snapshots.find({
                    "profile_key": profile_key,
                    "tenant_id": tenant_id
                }).sort("timestamp", 1)
                docs = await cursor.to_list(length=50)
                if docs:
                    return [ProfileSnapshot(**{k: v for k, v in d.items() if k != "_id"}) for d in docs]
            except Exception as e:
                app_logger.warning(f"MongoDB snapshot lookup failed: {e}")

        return self._memory_snapshots.get(memory_key, [])

    async def refresh_profile(self, platform_id: str, username: str, tenant_id: str = "default") -> Tuple[ProfileExtractionResult, List[ProfileChangeRecord]]:
        """
        Executes a live refresh for a specific platform profile and records any detected changes.
        """
        from app.modules.osint.platform_catalog_data import PLATFORM_CATALOG_RAW
        from app.modules.osint.catalog_adapter import OSINTPlatformAdapter
        from app.module_sdk.provider_adapter import ProviderRequest

        target_raw = None
        for raw in PLATFORM_CATALOG_RAW:
            if raw["platform_id"] == platform_id or f"osint_{raw['platform_id']}" == platform_id:
                target_raw = raw
                break

        if not target_raw:
            # Fallback to generic representation
            res = ProfileExtractionResult(
                platform_id=platform_id,
                platform_name=platform_id.capitalize(),
                username=username,
                canonical_url=f"https://{platform_id}.com/{username}",
                status=ExtractionStatus.PROFILE_VALIDATED,
                fetched_at=datetime.now(timezone.utc).isoformat()
            )
            return res, []

        adapter = OSINTPlatformAdapter(target_raw)
        req = ProviderRequest(query=username, target_type="username")
        resp = await adapter.execute(req)

        raw_data = resp.raw_data or {}
        extracted_dict = raw_data.get("extraction_result")
        if extracted_dict:
            res = ProfileExtractionResult(**extracted_dict)
        else:
            res = ProfileExtractionResult(
                platform_id=target_raw["platform_id"],
                platform_name=target_raw["name"],
                username=username,
                canonical_url=raw_data.get("profile_url", ""),
                status=ExtractionStatus(raw_data.get("status", "PROFILE_VALIDATED")),
                fetched_at=datetime.now(timezone.utc).isoformat()
            )

        res.is_cached = False
        _, changes = await self.record_observation(res, tenant_id=tenant_id)
        return res, changes


profile_snapshot_service = ProfileSnapshotService()
