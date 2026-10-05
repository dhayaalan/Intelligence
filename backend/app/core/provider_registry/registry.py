import threading
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from app.core.provider_registry.schemas import ProviderMetadata, ProviderStats
from app.module_sdk.provider_adapter import ProviderAdapter

logger = logging.getLogger("sential.provider_registry")

class ProviderRegistry:
    """
    Central Dynamic Provider Registry for the Sential Platform.
    Manages 300+ OSINT platform providers and 33 Threat Intelligence engines
    with full metadata, capability filtering, operational health tracking, and zero Core coupling.
    """
    
    def __init__(self):
        self._providers: Dict[str, ProviderAdapter] = {}
        self._metadata: Dict[str, ProviderMetadata] = {}
        self._lock = threading.RLock()

    def register(self, provider: ProviderAdapter, metadata: ProviderMetadata) -> None:
        """Registers a provider adapter with its rich operational metadata."""
        with self._lock:
            pid = provider.provider_id
            self._providers[pid] = provider
            self._metadata[pid] = metadata
            logger.debug(f"Registered provider '{pid}' ({metadata.name}) under module '{metadata.module_id}'")

    def unregister(self, provider_id: str) -> bool:
        """Removes a provider from the registry."""
        with self._lock:
            if provider_id in self._providers:
                del self._providers[provider_id]
                self._metadata.pop(provider_id, None)
                return True
            return False

    def enable(self, provider_id: str) -> bool:
        """Enables a provider."""
        with self._lock:
            meta = self._metadata.get(provider_id)
            if meta:
                meta.is_enabled = True
                meta.status = "HEALTHY"
                return True
            return False

    def disable(self, provider_id: str) -> bool:
        """Disables a provider."""
        with self._lock:
            meta = self._metadata.get(provider_id)
            if meta:
                meta.is_enabled = False
                meta.status = "DISABLED"
                return True
            return False

    def get_adapter(self, provider_id: str) -> Optional[ProviderAdapter]:
        with self._lock:
            return self._providers.get(provider_id)

    def get_metadata(self, provider_id: str) -> Optional[ProviderMetadata]:
        with self._lock:
            return self._metadata.get(provider_id)

    def list_providers(
        self,
        module_id: Optional[str] = None,
        category: Optional[str] = None,
        capability: Optional[str] = None,
        target_type: Optional[str] = None,
        search: Optional[str] = None,
        status: Optional[str] = None,
        enabled_only: bool = False
    ) -> List[ProviderMetadata]:
        """Queries and filters registered providers."""
        with self._lock:
            results = list(self._metadata.values())

            if enabled_only:
                results = [m for m in results if m.is_enabled]

            if module_id and module_id.upper() != "ALL":
                results = [m for m in results if m.module_id.lower() == module_id.lower()]

            if category and category.upper() != "ALL":
                results = [m for m in results if m.category.lower() == category.lower()]

            if capability and capability.upper() != "ALL":
                c_low = capability.lower()
                results = [m for m in results if any(c_low == cap.lower() for cap in m.capabilities)]

            if target_type and target_type.upper() != "ALL":
                t_low = target_type.lower()
                results = [m for m in results if any(t_low == t.lower() for t in m.supported_targets)]

            if status and status.upper() != "ALL":
                results = [m for m in results if m.status.lower() == status.lower()]

            if search and search.strip():
                q = search.strip().lower()
                results = [
                    m for m in results
                    if q in m.name.lower() or q in m.provider_id.lower() or q in m.category.lower()
                ]

            return sorted(results, key=lambda x: (x.module_id, x.category, x.name))

    def get_stats(self) -> ProviderStats:
        """Returns computed operational statistics across all registered providers."""
        with self._lock:
            all_meta = list(self._metadata.values())
            total = len(all_meta)
            osint_count = sum(1 for m in all_meta if m.module_id == "osint")
            ti_count = sum(1 for m in all_meta if m.module_id == "threat_intelligence")
            enabled = sum(1 for m in all_meta if m.is_enabled)
            healthy = sum(1 for m in all_meta if m.status in ("HEALTHY", "READY", "VERIFIED"))

            cats: Dict[str, int] = {}
            for m in all_meta:
                cats[m.category] = cats.get(m.category, 0) + 1

            return ProviderStats(
                total_providers=total,
                total_osint_providers=osint_count,
                total_threat_intel_providers=ti_count,
                enabled_providers=enabled,
                healthy_providers=healthy,
                categories=cats
            )

    async def health_check_all(self, module_id: Optional[str] = None) -> Dict[str, Any]:
        """Runs health checks across registered providers."""
        with self._lock:
            providers_to_check = list(self._providers.items())
            if module_id:
                providers_to_check = [
                    (pid, p) for pid, p in providers_to_check
                    if self._metadata.get(pid) and self._metadata[pid].module_id == module_id
                ]

        results = {}
        for pid, provider in providers_to_check:
            try:
                res = await provider.health_check()
                results[pid] = {
                    "status": res.status.value,
                    "message": res.message,
                    "checked_at": datetime.utcnow().isoformat()
                }
                with self._lock:
                    if pid in self._metadata:
                        self._metadata[pid].last_health_check = datetime.utcnow()
                        self._metadata[pid].status = res.status.value.upper()
            except Exception as e:
                results[pid] = {
                    "status": "error",
                    "message": str(e),
                    "checked_at": datetime.utcnow().isoformat()
                }
        return results

# Singleton instance
provider_registry = ProviderRegistry()
