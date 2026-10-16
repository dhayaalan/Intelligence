import asyncio
from typing import Optional, Dict, Any
from neo4j import AsyncGraphDatabase, AsyncDriver
from app.core.config import settings
from app.core.logging import app_logger

class Neo4jClient:
    """
    Asynchronous connection manager and schema initializer for Neo4j Graph Database.
    Provides connection pooling, health checks, parameterized Cypher execution,
    and graceful error handling.
    """
    def __init__(self):
        self._driver: Optional[AsyncDriver] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._is_initialized = False
        self._lock: Optional[asyncio.Lock] = None

    def _get_lock(self) -> asyncio.Lock:
        if self._lock is None:
            self._lock = asyncio.Lock()
        return self._lock

    async def get_driver(self) -> Optional[AsyncDriver]:
        try:
            current_loop = asyncio.get_running_loop()
        except RuntimeError:
            current_loop = None

        if self._driver is not None:
            if self._loop is None or self._loop == current_loop:
                return self._driver
            # Loop has changed (e.g., between pytest test cases)
            self._driver = None

        lock = self._get_lock()
        async with lock:
            if self._driver is not None and (self._loop is None or self._loop == current_loop):
                return self._driver
            try:
                self._driver = AsyncGraphDatabase.driver(
                    settings.NEO4J_URI,
                    auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD),
                    max_connection_lifetime=settings.NEO4J_MAX_CONNECTION_LIFETIME,
                    max_connection_pool_size=settings.NEO4J_MAX_CONNECTION_POOL_SIZE,
                    connection_timeout=settings.NEO4J_CONNECTION_TIMEOUT,
                )
                self._loop = current_loop
                # Verify connectivity
                await self._driver.verify_connectivity()
                app_logger.info(f"Connected to Neo4j graph cluster at {settings.NEO4J_URI}")
                return self._driver
            except Exception as e:
                app_logger.warning(f"Neo4j connection attempt to {settings.NEO4J_URI} failed: {e}")
                self._driver = None
                return None

    async def close(self):
        if self._driver is not None:
            try:
                await self._driver.close()
                app_logger.info("Closed Neo4j driver connection.")
            except Exception as e:
                app_logger.warning(f"Error closing Neo4j driver: {e}")
            finally:
                self._driver = None
                self._is_initialized = False

    async def verify_connectivity(self) -> bool:
        res = await self.ping()
        return res.get("status") == "healthy"

    async def ping(self) -> Dict[str, Any]:
        """Pings Neo4j and returns connectivity status and server version."""
        driver = await self.get_driver()
        if not driver:
            return {"status": "unavailable", "message": "Neo4j driver not connected"}
        try:
            async with driver.session() as session:
                result = await session.run("RETURN 1 AS ping")
                record = await result.single()
                if record and record["ping"] == 1:
                    return {"status": "healthy", "uri": settings.NEO4J_URI}
                return {"status": "degraded", "message": "Unexpected ping return value"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    async def init_schema(self) -> bool:
        """
        Idempotently initializes indexes and constraints in Neo4j.
        Safe for community and enterprise editions.
        """
        driver = await self.get_driver()
        if not driver:
            return False

        schema_queries = [
            # Entity uniqueness and tenant indices
            "CREATE CONSTRAINT entity_id_unique IF NOT EXISTS FOR (e:Entity) REQUIRE e.id IS UNIQUE",
            "CREATE INDEX entity_tenant_idx IF NOT EXISTS FOR (e:Entity) ON (e.tenant_id)",
            "CREATE INDEX entity_tenant_val_idx IF NOT EXISTS FOR (e:Entity) ON (e.tenant_id, e.value)",
            "CREATE INDEX entity_type_idx IF NOT EXISTS FOR (e:Entity) ON (e.tenant_id, e.type)",
            # Relationship constraints
            "CREATE CONSTRAINT rel_id_unique IF NOT EXISTS FOR ()-[r:INVESTIGATION_REL]-() REQUIRE r.id IS UNIQUE",
        ]

        async with driver.session() as session:
            for q in schema_queries:
                try:
                    await session.run(q)
                except Exception as e:
                    # Log but continue (e.g. if community edition has syntax variance)
                    app_logger.debug(f"Neo4j schema init statement '{q}' returned: {e}")

        self._is_initialized = True
        app_logger.info("Neo4j relationship graph schema and indexes verified.")
        return True

neo4j_client = Neo4jClient()
