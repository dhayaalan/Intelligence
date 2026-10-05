# Multi-Tenancy Architecture & Boundary Enforcement

## Strict Isolation Guarantee

1. **Context Derivation**:
   Tenant identity is derived strictly from the validated JWT token (`get_current_tenant_id` in `app.tenancy.context`). Tenant IDs sent in request bodies or query parameters are never trusted for scoping.

2. **Database Boundary**:
   Every resource (Investigation, Entity, Evidence, Search, Audit Log) is scoped by `tenant_id`.

3. **Cross-Tenant Prevention**:
   ```python
   data = db.investigations.get(investigation_id)
   if not data or data.get("tenant_id") != current_user.tenant_id:
       raise HTTPException(status_code=404, detail="Investigation not found in this tenant")
   ```

4. **Automated Verification**:
   The test suite includes `test_tenant_isolation.py` proving that a user from Tenant A receives 404/empty responses when requesting resources owned by Tenant B.
