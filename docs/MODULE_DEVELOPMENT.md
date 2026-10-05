# Module Development Guide

## Checklist for Adding a New Module (e.g. `dark_web` or `crypto`)

To add a new intelligence module without modifying Core Search or Investigation logic:

1. **Create Module Directory**:
   ```bash
   mkdir -p backend/app/modules/<module_name>/{domain,application,infrastructure,providers,schemas,normalization}
   mkdir -p frontend/src/modules/<module_name>
   ```

2. **Define Declarative Manifest (`manifest.py`)**:
   ```python
   from app.module_sdk.manifest import ModuleManifest, ModuleConfigField

   DARK_WEB_MANIFEST = ModuleManifest(
       id="dark_web",
       name="Dark Web Intelligence",
       version="1.0.0",
       capabilities=["search", "enrichment"],
       providers=["tor_indexer", "breach_forums"],
       configuration_schema=[
           ModuleConfigField(key="tor_proxy_url", label="Tor SOCKS5 Proxy", default="socks5://localhost:9050")
       ]
   )
   ```

3. **Implement Provider Adapters (`providers/*.py`)**:
   Implement `ProviderAdapter` subclassing `execute()` and `health_check()`.

4. **Implement Module Class (`module.py`)**:
   Subclass `IntelligenceModule` and implement `search()` returning `NormalizedModuleResult`.

5. **Register Module**:
   In `backend/app/main.py`:
   ```python
   module_registry.register(dark_web_module)
   ```

6. **Frontend Extension (`frontend/src/modules/<module_name>/index.tsx`)**:
   Call `frontendModuleRegistry.registerExtension({ id, SearchResultComponent, ... })`.

Existing modules and Core Search remain completely untouched.
