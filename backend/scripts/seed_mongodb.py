#!/usr/bin/env python3
"""
Production Database Seed Script for MongoDB
Initializes collections, indexes, tenants, role accounts, and core registry records.
"""
import sys
import os
import pymongo
from datetime import datetime

# Add app to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.config import settings
from app.core.security import get_password_hash

def seed_mongodb():
    print(f"Connecting to MongoDB at {settings.MONGODB_URI} (db: {settings.MONGODB_DATABASE})...")
    client = pymongo.MongoClient(settings.MONGODB_URI, serverSelectionTimeoutMS=5000)
    db = client[settings.MONGODB_DATABASE]
    
    # Ping
    db.command("ping")
    print("Connected successfully to MongoDB.")

    # 1. Create collection indexes
    print("Creating MongoDB collection indexes...")
    db.tenants.create_index("id", unique=True)
    db.tenants.create_index("slug", unique=True)
    db.users.create_index("id", unique=True)
    db.users.create_index("email", unique=True)
    db.users.create_index([("tenant_id", 1), ("role", 1)])
    db.investigations.create_index("id", unique=True)
    db.investigations.create_index([("tenant_id", 1), ("status", 1)])
    db.investigations.create_index([("tenant_id", 1), ("updated_at", -1)])
    db.cases.create_index("id", unique=True)
    db.cases.create_index([("tenant_id", 1), ("status", 1)])
    db.entities.create_index("id", unique=True)
    db.entities.create_index([("tenant_id", 1), ("investigation_id", 1)])
    db.relationships.create_index("id", unique=True)
    db.relationships.create_index([("tenant_id", 1), ("source_val", 1), ("target_val", 1)])
    db.evidence.create_index("id", unique=True)
    db.evidence.create_index([("tenant_id", 1), ("investigation_id", 1)])
    db.findings.create_index("id", unique=True)
    db.findings.create_index([("tenant_id", 1), ("investigation_id", 1)])
    db.reports.create_index("id", unique=True)
    db.reports.create_index([("tenant_id", 1), ("investigation_id", 1)])
    db.searches.create_index("id", unique=True)
    db.searches.create_index([("tenant_id", 1), ("created_at", -1)])
    db.audit_logs.create_index("id", unique=True)
    db.audit_logs.create_index([("tenant_id", 1), ("timestamp", -1)])

    # 2. Seed Default Tenants
    print("Seeding tenants...")
    tenants = [
        {
            "id": "tenant_global",
            "name": "Global Operations",
            "slug": "global-ops",
            "entitled_modules": ["osint", "threat_intelligence", "test_intelligence"],
            "status": "active",
            "created_at": "2026-10-01T00:00:00"
        },
        {
            "id": "tenant_acme",
            "name": "Acme Cyber Defense Corp",
            "slug": "acme-corp",
            "entitled_modules": ["osint", "threat_intelligence"],
            "status": "active",
            "created_at": "2026-10-01T00:00:00"
        },
        {
            "id": "tenant_basic",
            "name": "Basic Recon Agency",
            "slug": "basic-recon",
            "entitled_modules": ["osint"],
            "status": "active",
            "created_at": "2026-10-01T00:00:00"
        }
    ]
    for t in tenants:
        db.tenants.update_one({"id": t["id"]}, {"$set": t}, upsert=True)

    # 3. Seed Default RBAC Users
    print("Seeding users...")
    users = [
        {
            "id": "usr_super_admin",
            "email": "superadmin@sential.io",
            "hashed_password": get_password_hash("SuperAdmin123!"),
            "name": "Alex Vance (Super Admin)",
            "role": "SUPER_ADMIN",
            "tenant_id": "tenant_global",
            "assigned_modules": ["osint", "threat_intelligence", "test_intelligence"],
            "status": "active",
            "created_at": "2026-10-01T00:00:00",
            "last_login": None
        },
        {
            "id": "usr_tenant_admin",
            "email": "admin@acme.com",
            "hashed_password": get_password_hash("TenantAdmin123!"),
            "name": "Sarah Connor (Tenant Admin)",
            "role": "TENANT_ADMIN",
            "tenant_id": "tenant_acme",
            "assigned_modules": ["osint", "threat_intelligence"],
            "status": "active",
            "created_at": "2026-10-01T00:00:00",
            "last_login": None
        },
        {
            "id": "usr_analyst",
            "email": "analyst@acme.com",
            "hashed_password": get_password_hash("Analyst123!"),
            "name": "Marcus Wright (Lead Analyst)",
            "role": "ANALYST",
            "tenant_id": "tenant_acme",
            "assigned_modules": ["osint", "threat_intelligence"],
            "status": "active",
            "created_at": "2026-10-01T00:00:00",
            "last_login": None
        },
        {
            "id": "usr_investigator",
            "email": "user@acme.com",
            "hashed_password": get_password_hash("User123!"),
            "name": "Elena Fisher (Investigator)",
            "role": "USER",
            "tenant_id": "tenant_acme",
            "assigned_modules": ["osint"],
            "status": "active",
            "created_at": "2026-10-01T00:00:00",
            "last_login": None
        },
        {
            "id": "usr_basic_admin",
            "email": "admin@basic-recon.com",
            "hashed_password": get_password_hash("BasicAdmin123!"),
            "name": "Basic Admin",
            "role": "TENANT_ADMIN",
            "tenant_id": "tenant_basic",
            "assigned_modules": ["osint"],
            "status": "active",
            "created_at": "2026-10-01T00:00:00",
            "last_login": None
        }
    ]
    for u in users:
        db.users.update_one({"id": u["id"]}, {"$set": u}, upsert=True)

    # 4. Seed Baseline Real Investigations
    print("Seeding baseline investigations...")
    investigations = [
        {
            "id": "inv_dhayaalan",
            "tenant_id": "tenant_acme",
            "title": "Target Investigation: dhayaalan",
            "description": "Cross-platform identity correlation and developer presence reconnaissance across 368 engines.",
            "status": "open",
            "priority": "HIGH",
            "selected_modules": ["osint", "threat_intelligence"],
            "target": "dhayaalan",
            "target_type": "username",
            "created_by": "usr_analyst",
            "entity_ids": ["ent_dhayaalan_gh", "ent_dhayaalan_email"],
            "evidence_ids": ["ev_dhayaalan_p1", "ev_dhayaalan_p2"],
            "timeline": [],
            "notes": [],
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        },
        {
            "id": "inv_acme_defense",
            "tenant_id": "tenant_acme",
            "title": "Infrastructure Audit: acme-defense.org",
            "description": "External perimeter attack surface mapping, open port analysis, and DNS intelligence.",
            "status": "in_progress",
            "priority": "HIGH",
            "selected_modules": ["osint"],
            "target": "acme-defense.org",
            "target_type": "domain",
            "created_by": "usr_analyst",
            "entity_ids": ["ent_acme_ip"],
            "evidence_ids": ["ev_dns_acme"],
            "timeline": [],
            "notes": [],
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        },
        {
            "id": "inv_c2_mesh",
            "tenant_id": "tenant_acme",
            "title": "Adversary Node: 185.220.101.42",
            "description": "Adversary C2 mesh ingress endpoint with live geographic threat indicators.",
            "status": "open",
            "priority": "CRITICAL",
            "selected_modules": ["osint", "threat_intelligence"],
            "target": "185.220.101.42",
            "target_type": "ip",
            "created_by": "usr_analyst",
            "entity_ids": ["ent_c2_host"],
            "evidence_ids": ["ev_c2_shodan"],
            "timeline": [],
            "notes": [],
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
    ]
    for inv in investigations:
        db.investigations.update_one({"id": inv["id"]}, {"$set": inv}, upsert=True)
        db.cases.update_one({"id": inv["id"]}, {"$set": inv}, upsert=True)

    print("\n--- MongoDB Seeding Completed Successfully ---")
    print(f"Tenants in MongoDB:        {db.tenants.count_documents({})}")
    print(f"Users in MongoDB:          {db.users.count_documents({})}")
    print(f"Investigations in MongoDB: {db.investigations.count_documents({})}")
    print(f"Cases in MongoDB:          {db.cases.count_documents({})}")

if __name__ == "__main__":
    seed_mongodb()
