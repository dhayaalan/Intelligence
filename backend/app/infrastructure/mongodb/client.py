import asyncio
from typing import Optional, Dict, Any, List
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
import pymongo
from pymongo.database import Database as SyncDatabase
from app.core.config import settings
from app.core.logging import app_logger

class MongoDBManager:
    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None
    sync_client: Optional[pymongo.MongoClient] = None
    sync_db: Optional[SyncDatabase] = None

mongo_manager = MongoDBManager()

async def connect_to_mongo():
    try:
        app_logger.info(f"Connecting to MongoDB at {settings.MONGODB_URI} (db: {settings.MONGODB_DATABASE})...")
        mongo_manager.client = AsyncIOMotorClient(
            settings.MONGODB_URI,
            serverSelectionTimeoutMS=3000
        )
        mongo_manager.db = mongo_manager.client[settings.MONGODB_DATABASE]
        # Verify connection
        await mongo_manager.db.command("ping")
        app_logger.info("Successfully connected to async MongoDB via Motor.")
        
        # Also initialize sync client for sync tools & seeds
        try:
            mongo_manager.sync_client = pymongo.MongoClient(
                settings.MONGODB_URI,
                serverSelectionTimeoutMS=3000
            )
            mongo_manager.sync_db = mongo_manager.sync_client[settings.MONGODB_DATABASE]
        except Exception as se:
            app_logger.warning(f"Could not connect sync MongoDB client: {se}")

        # Create core collection indexes
        await create_indexes()
        
        # Restore data from MongoDB into in-memory store
        await restore_data_from_mongo()
        
    except Exception as e:
        app_logger.warning(f"Could not connect to MongoDB ({e}). Falling back to memory-synced repository mode.")

async def close_mongo_connection():
    if mongo_manager.client:
        mongo_manager.client.close()
        app_logger.info("Async MongoDB connection closed.")
    if mongo_manager.sync_client:
        mongo_manager.sync_client.close()
        app_logger.info("Sync MongoDB connection closed.")

async def create_indexes():
    """Initializes primary, unique, and compound indexes across all collections."""
    db = mongo_manager.db
    if db is None:
        return
        
    try:
        # Tenants
        await db.tenants.create_index("id", unique=True)
        await db.tenants.create_index("slug", unique=True)
        
        # Users
        await db.users.create_index("id", unique=True)
        await db.users.create_index("email", unique=True)
        await db.users.create_index([("tenant_id", 1), ("role", 1)])
        
        # Modules & Configurations
        await db.modules.create_index("id", unique=True)
        await db.module_configurations.create_index([("tenant_id", 1), ("module_id", 1)], unique=True)
        
        # Searches
        await db.searches.create_index("id", unique=True)
        await db.searches.create_index([("tenant_id", 1), ("created_at", -1)])
        
        # Investigations & Cases
        await db.investigations.create_index("id", unique=True)
        await db.investigations.create_index([("tenant_id", 1), ("status", 1)])
        await db.investigations.create_index([("tenant_id", 1), ("updated_at", -1)])
        await db.investigations.create_index([("tenant_id", 1), ("priority", 1)])
        
        await db.cases.create_index("id", unique=True)
        await db.cases.create_index([("tenant_id", 1), ("status", 1)])
        await db.cases.create_index([("tenant_id", 1), ("updated_at", -1)])
        
        # Entities & Relationships
        await db.entities.create_index("id", unique=True)
        await db.entities.create_index([("tenant_id", 1), ("investigation_id", 1)])
        await db.entities.create_index([("tenant_id", 1), ("type", 1), ("value", 1)])
        await db.relationships.create_index("id", unique=True)
        await db.relationships.create_index([("tenant_id", 1), ("source_val", 1), ("target_val", 1)])
        
        # Evidence
        await db.evidence.create_index("id", unique=True)
        await db.evidence.create_index([("tenant_id", 1), ("investigation_id", 1)])
        await db.evidence.create_index("hash")
        
        # Findings
        await db.findings.create_index("id", unique=True)
        await db.findings.create_index([("tenant_id", 1), ("investigation_id", 1)])
        await db.findings.create_index([("tenant_id", 1), ("severity", 1)])
        await db.findings.create_index([("tenant_id", 1), ("status", 1)])
        
        # Reports
        await db.reports.create_index("id", unique=True)
        await db.reports.create_index([("tenant_id", 1), ("investigation_id", 1)])
        await db.reports.create_index([("tenant_id", 1), ("created_at", -1)])
        
        # Jobs
        await db.jobs.create_index("job_id", unique=True)
        await db.jobs.create_index([("tenant_id", 1), ("search_id", 1)])
        
        # Audit Logs
        await db.audit_logs.create_index("id", unique=True)
        await db.audit_logs.create_index([("tenant_id", 1), ("timestamp", -1)])
        
        app_logger.info("MongoDB collection indexes initialized successfully.")
    except Exception as e:
        app_logger.error(f"Error creating MongoDB indexes: {e}")

async def restore_data_from_mongo():
    """Restores previously persisted MongoDB records into memory cache on startup."""
    db = mongo_manager.db
    if db is None:
        return
        
    try:
        from app.core.database import db as mem_db
        with mem_db._lock:
            # 1. Tenants
            async for t in db.tenants.find({}, {"_id": 0}):
                mem_db.tenants[t["id"]] = t
            # 2. Users
            async for u in db.users.find({}, {"_id": 0}):
                mem_db.users[u["id"]] = u
            # 3. Investigations
            async for inv in db.investigations.find({}, {"_id": 0}):
                mem_db.investigations[inv["id"]] = inv
            # 4. Entities
            async for ent in db.entities.find({}, {"_id": 0}):
                mem_db.entities[ent["id"]] = ent
            # 5. Relationships
            async for rel in db.relationships.find({}, {"_id": 0}):
                mem_db.relationships[rel["id"]] = rel
            # 6. Evidence
            async for ev in db.evidence.find({}, {"_id": 0}):
                mem_db.evidence[ev["id"]] = ev
            # 7. Searches
            async for s in db.searches.find({}, {"_id": 0}):
                mem_db.searches[s["id"]] = s
            # 8. Audit logs
            audit_docs = await db.audit_logs.find({}, {"_id": 0}).to_list(length=1000)
            mem_db.audit_logs.extend(audit_docs)
            
        app_logger.info("Successfully restored state from MongoDB into runtime memory cache.")
    except Exception as e:
        app_logger.error(f"Error restoring state from MongoDB: {e}")

def get_database() -> Optional[AsyncIOMotorDatabase]:
    return mongo_manager.db

def get_sync_database() -> Optional[SyncDatabase]:
    return mongo_manager.sync_db
