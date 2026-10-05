# Multi-Layer Authorization Pipeline

Module execution and access require passing 5 consecutive authorization checks:

```text
1. Platform Module Check
   Is the module registered and globally enabled in the platform?
               │
               ▼
2. Tenant Entitlement Check
   Is the requesting user's tenant organization licensed for this module?
               │
               ▼
3. Role Permission Check
   Does the user's role possess the 'search:execute' permission?
               │
               ▼
4. User Module Assignment Check
   Has the tenant administrator explicitly assigned this module to the user?
               │
               ▼
5. Effective Module Access Granted
```

If any check fails, the module is omitted from the effective execution plan for that request without causing an error.
