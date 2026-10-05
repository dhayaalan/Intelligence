import threading
from typing import Any, Dict, List, Optional
from datetime import datetime

class DataStore:
    """Thread-safe transactional in-memory and persistence-ready store for multi-tenancy."""
    
    def __init__(self):
        self._lock = threading.RLock()
        self.tenants: Dict[str, Dict[str, Any]] = {}
        self.users: Dict[str, Dict[str, Any]] = {}
        self.investigations: Dict[str, Dict[str, Any]] = {}
        self.entities: Dict[str, Dict[str, Any]] = {}
        self.relationships: Dict[str, Dict[str, Any]] = {}
        self.evidence: Dict[str, Dict[str, Any]] = {}
        self.searches: Dict[str, Dict[str, Any]] = {}
        self.audit_logs: List[Dict[str, Any]] = []
        self.module_configs: Dict[str, Dict[str, Any]] = {} # keyed by (tenant_id, module_id)
        
    def clear(self):
        with self._lock:
            self.tenants.clear()
            self.users.clear()
            self.investigations.clear()
            self.entities.clear()
            self.relationships.clear()
            self.evidence.clear()
            self.searches.clear()
            self.audit_logs.clear()
            self.module_configs.clear()

db = DataStore()
