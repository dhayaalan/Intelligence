import uuid
from datetime import datetime
from app.core.config import settings
from app.core.logging import app_logger
from app.core.security import get_password_hash
from app.identity.models import UserRole, UserStatus
from app.infrastructure.mongodb.client import get_database, get_sync_database
from app.core.database import db as mem_db

async def bootstrap_super_admin():
    """
    Secure First-Run Super Admin Bootstrap.
    Strictly creates ONLY the platform Super Admin if no Super Admin exists.
    Never creates default tenants, tenant admins, cases, or demo data.
    """
    mongo_db = get_database()
    sync_db = get_sync_database()
    
    # 1. Check if a Super Admin already exists in MongoDB
    has_super_admin = False
    if mongo_db is not None:
        try:
            count = await mongo_db.users.count_documents({"role": UserRole.SUPER_ADMIN.value})
            has_super_admin = count > 0
        except Exception as e:
            app_logger.warning(f"Could not check Super Admin existence in MongoDB: {e}")
    elif sync_db is not None:
        try:
            has_super_admin = sync_db.users.count_documents({"role": UserRole.SUPER_ADMIN.value}) > 0
        except Exception:
            pass

    if has_super_admin:
        app_logger.info("Platform already initialized with Super Admin. Skipping bootstrap.")
        return

    # 2. Check if already marked in system_settings
    if mongo_db is not None:
        try:
            flag = await mongo_db.system_settings.find_one({"key": "super_admin_bootstrapped"})
            if flag:
                return
        except Exception:
            pass

    # 3. Securely create the platform Super Admin from environment
    email = (getattr(settings, "INITIAL_SUPER_ADMIN_EMAIL", None) or "superadmin@sential.io").strip().lower()
    raw_password = getattr(settings, "INITIAL_SUPER_ADMIN_PASSWORD", None) or "SuperAdmin123!"
    
    super_admin_record = {
        "id": "usr_super_admin",
        "email": email,
        "hashed_password": get_password_hash(raw_password),
        "name": "System Super Admin",
        "role": UserRole.SUPER_ADMIN.value,
        "tenant_id": "platform",  # Platform-wide root, not a tenant
        "assigned_modules": ["osint", "threat_intelligence", "news_intelligence"],
        "status": UserStatus.ACTIVE.value,
        "created_at": datetime.utcnow().isoformat(),
        "last_login": None
    }

    # Write to MongoDB
    if mongo_db is not None:
        try:
            await mongo_db.users.update_one(
                {"id": "usr_super_admin"},
                {"$set": super_admin_record},
                upsert=True
            )
            await mongo_db.system_settings.update_one(
                {"key": "super_admin_bootstrapped"},
                {"$set": {"completed": True, "bootstrapped_at": datetime.utcnow().isoformat(), "email": email}},
                upsert=True
            )
            app_logger.info(f"Initialized secure Super Admin account: {email}")
        except Exception as e:
            app_logger.error(f"Error persisting Super Admin to MongoDB: {e}")

    # Synchronize to memory store
    with mem_db._lock:
        mem_db.users["usr_super_admin"] = super_admin_record

    app_logger.info("Super Admin bootstrap completed. Total Tenants: 0, Total Tenant Users: 0.")

def is_platform_initialized() -> bool:
    """Checks whether the platform has an existing Super Admin."""
    sync_db = get_sync_database()
    if sync_db is not None:
        try:
            return sync_db.users.count_documents({"role": UserRole.SUPER_ADMIN.value}) > 0
        except Exception:
            pass
    with mem_db._lock:
        return any(u.get("role") == UserRole.SUPER_ADMIN.value for u in mem_db.users.values())
