from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import app_logger
from app.api.v1.router import api_v1_router
from app.module_registry.registry import module_registry
from app.modules.osint.module import osint_module
from app.modules.threat_intelligence.module import threat_intelligence_module
from app.modules.test_intelligence.module import test_intelligence_module
from app.identity.bootstrap import bootstrap_super_admin
from app.infrastructure.mongodb.client import connect_to_mongo, close_mongo_connection
from app.modules.example_intelligence.module import example_module


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Modular Investigator-First OSINT & Threat Intelligence SaaS Platform"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API v1 router
app.include_router(api_v1_router, prefix=settings.API_V1_PREFIX)

@app.on_event("startup")
async def startup_event():
    app_logger.info("Initializing Sential Intelligence Platform Core with MongoDB...")
    
    # Connect to MongoDB and create collection indexes
    await connect_to_mongo()
    
    # 1. Register Independent Modules with Module Registry
    module_registry.register(osint_module, default_enabled=True)
    module_registry.register(threat_intelligence_module, default_enabled=True)
    module_registry.register(example_module, default_enabled=True)
    module_registry.register(test_intelligence_module, default_enabled=True)
    
    # 2. Bootstrap Secure Super Admin only (NO fake business data, NO demo tenants)
    await bootstrap_super_admin()
    
    app_logger.info("Sential Platform successfully started. Core is ready with MongoDB.")

@app.on_event("shutdown")
async def shutdown_event():
    await close_mongo_connection()

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "modules_registered": len(module_registry.list_all_modules())
    }

