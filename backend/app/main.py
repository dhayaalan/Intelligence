from fastapi import FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import app_logger
from app.api.v1.router import api_v1_router
from app.module_registry.registry import module_registry
from app.modules.osint.module import osint_module
from app.modules.threat_intelligence.module import threat_intelligence_module
from app.modules.test_intelligence.module import test_intelligence_module
from app.identity.bootstrap import bootstrap_super_admin
from app.infrastructure.mongodb.client import connect_to_mongo, close_mongo_connection, mongo_manager
from app.modules.example_intelligence.module import example_module
from app.modules.news_intelligence.module import news_intelligence_module
from app.modules.social_media_intelligence.module import social_media_intelligence_module
from app.modules.geo_intelligence.module import geo_intelligence_module


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Modular Investigator-First OSINT & Threat Intelligence SaaS Platform"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API v1 router
app.include_router(api_v1_router, prefix=settings.API_V1_PREFIX)

@app.on_event("startup")
async def startup_event():
    # 0. Validate production security configuration
    settings.validate_production_configuration()
    app_logger.info("Initializing Sential Intelligence Platform Core with MongoDB...")
    
    # Connect to MongoDB and create collection indexes
    await connect_to_mongo()
    
    # 1. Register Independent Modules with Module Registry
    module_registry.register(osint_module, default_enabled=True)
    module_registry.register(threat_intelligence_module, default_enabled=True)
    module_registry.register(news_intelligence_module, default_enabled=True)
    module_registry.register(social_media_intelligence_module, default_enabled=True)
    module_registry.register(geo_intelligence_module, default_enabled=True)
    # Test and demonstration plugins are registered disabled by default
    # to prevent synthetic or mocked data contamination in production searches
    module_registry.register(example_module, default_enabled=False)
    module_registry.register(test_intelligence_module, default_enabled=False)
    
    # 2. Bootstrap Secure Super Admin only (NO fake business data, NO demo tenants)
    await bootstrap_super_admin()
    
    # 3. Initialize Neo4j graph database schema and indexes
    try:
        from app.infrastructure.neo4j.client import neo4j_client
        if await neo4j_client.verify_connectivity():
            await neo4j_client.init_schema()
            app_logger.info("Neo4j relationship graph service initialized with constraints.")
    except Exception as e:
        app_logger.warning(f"Neo4j initialization non-critical deferred: {e}")

    app_logger.info("Sential Platform successfully started. Core is ready with MongoDB.")

@app.on_event("shutdown")
async def shutdown_event():
    try:
        from app.infrastructure.neo4j.client import neo4j_client
        await neo4j_client.close()
    except Exception:
        pass
    await close_mongo_connection()

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "modules_registered": len(module_registry.list_all_modules())
    }

@app.get("/health/liveness")
@app.get("/health/live")
async def liveness_check():
    return {
        "status": "alive",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION
    }

@app.get("/health/readiness")
@app.get("/health/ready")
async def readiness_check(response: Response):
    db_connected = False
    db_details = "disconnected"
    try:
        if mongo_manager.db is not None:
            await mongo_manager.db.command("ping")
            db_connected = True
            db_details = "connected"
        else:
            db_details = "uninitialized"
    except Exception as e:
        db_details = "error"

    neo4j_status = "unavailable"
    try:
        from app.infrastructure.neo4j.client import neo4j_client
        if await neo4j_client.verify_connectivity():
            neo4j_status = "connected"
    except Exception:
        neo4j_status = "error"

    # In production, database connectivity is required for readiness
    is_ready = db_connected if settings.APP_ENV == "production" else True
    modules_count = len(module_registry.list_all_modules())
    if modules_count == 0:
        is_ready = False

    if not is_ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {
            "status": "unready",
            "database": db_details,
            "graph_database": neo4j_status,
            "modules_registered": modules_count,
            "environment": settings.APP_ENV
        }

    return {
        "status": "ready",
        "database": db_details,
        "graph_database": neo4j_status,
        "modules_registered": modules_count,
        "environment": settings.APP_ENV
    }

