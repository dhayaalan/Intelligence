import asyncio
import time
from typing import Any, Dict, List, Optional
from datetime import datetime
from app.core.logging import app_logger
from app.core.database import db
from app.module_sdk.contract import IntelligenceModule
from app.module_sdk.models import ModuleHealthStatus
from app.module_registry.schemas import ModuleLifecycleState, ModuleRegistryItem

class ModuleRegistry:
    """Central registry managing the discovery, lifecycle, health, and execution routing for intelligence modules."""
    
    def __init__(self):
        self._modules: Dict[str, IntelligenceModule] = {}
        self._status_records: Dict[str, ModuleRegistryItem] = {}
        
    def register(self, module: IntelligenceModule, default_enabled: bool = True) -> None:
        """Registers an independent intelligence module with the platform core."""
        manifest = module.manifest
        mod_id = manifest.id
        
        self._modules[mod_id] = module
        
        record = ModuleRegistryItem(
            id=mod_id,
            name=manifest.name,
            version=manifest.version,
            description=manifest.description,
            enabled=default_enabled,
            lifecycle_state=ModuleLifecycleState.AVAILABLE if default_enabled else ModuleLifecycleState.REGISTERED,
            health_status=ModuleHealthStatus.HEALTHY,
            capabilities=manifest.capabilities,
            permissions=manifest.permissions,
            providers=manifest.providers,
            provider_statuses={p: "ready" for p in manifest.providers},
            configuration_schema=manifest.configuration_schema,
            ui_metadata=manifest.ui_metadata
        )
        self._status_records[mod_id] = record
        app_logger.info(f"Registered intelligence module: '{mod_id}' v{manifest.version}")

    def get_module(self, module_id: str) -> Optional[IntelligenceModule]:
        return self._modules.get(module_id)

    def is_module_enabled(self, module_id: str) -> bool:
        rec = self._status_records.get(module_id)
        return rec is not None and rec.enabled

    def enable_module(self, module_id: str) -> bool:
        rec = self._status_records.get(module_id)
        if not rec:
            return False
        rec.enabled = True
        rec.lifecycle_state = ModuleLifecycleState.AVAILABLE
        app_logger.info(f"Module '{module_id}' enabled by admin")
        return True

    def disable_module(self, module_id: str) -> bool:
        rec = self._status_records.get(module_id)
        if not rec:
            return False
        rec.enabled = False
        rec.lifecycle_state = ModuleLifecycleState.REGISTERED
        app_logger.info(f"Module '{module_id}' disabled by admin")
        return True

    def list_all_modules(self) -> List[ModuleRegistryItem]:
        return list(self._status_records.values())

    def list_modules(self) -> List[str]:
        return list(self._modules.keys())

    def get_module_info(self, module_id: str) -> Optional[ModuleRegistryItem]:
        return self._status_records.get(module_id)

    async def check_module_health(self, module_id: str) -> Optional[ModuleRegistryItem]:
        module = self._modules.get(module_id)
        rec = self._status_records.get(module_id)
        if not module or not rec:
            return None
            
        start = time.time()
        try:
            health = await module.health_check()
            rec.health_status = health.status
            rec.health_message = health.message
            rec.latency_ms = round((time.time() - start) * 1000, 2)
            if health.provider_statuses:
                rec.provider_statuses.update(health.provider_statuses)
        except Exception as e:
            rec.health_status = ModuleHealthStatus.DEGRADED
            rec.health_message = f"Health check failed: {str(e)}"
            rec.latency_ms = round((time.time() - start) * 1000, 2)
            
        return rec

    async def check_all_health(self) -> List[ModuleRegistryItem]:
        tasks = [self.check_module_health(mid) for mid in self._modules.keys()]
        await asyncio.gather(*tasks, return_exceptions=True)
        return self.list_all_modules()

    def record_execution(self, module_id: str, success: bool, latency_ms: float = 0.0):
        rec = self._status_records.get(module_id)
        if rec:
            rec.total_executions += 1
            if success:
                rec.successful_executions += 1
            else:
                rec.failed_executions += 1
            rec.last_executed_at = datetime.utcnow()
            rec.latency_ms = latency_ms

    def configure_module(self, tenant_id: str, module_id: str, config: Dict[str, Any]):
        with db._lock:
            key = f"{tenant_id}:{module_id}"
            db.module_configs[key] = config

    def get_module_config(self, tenant_id: str, module_id: str) -> Dict[str, Any]:
        with db._lock:
            key = f"{tenant_id}:{module_id}"
            return db.module_configs.get(key, {})

# Global singleton module registry
module_registry = ModuleRegistry()
