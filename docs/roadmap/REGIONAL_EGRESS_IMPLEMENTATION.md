# Regional VPN Egress & OPSEC Implementation Guide

## 1. Architectural Overview
The Sential Intelligence Platform enforces Zero Trust Architecture (NIST SP 800-207) for all outbound investigative operations. Outbound requests requiring specific geographic perspectives (e.g. India, United States, United Kingdom) or isolated scanning nets must route exclusively through approved, verified regional egress endpoints.

If a regional route is required and the endpoint is offline or fails verification, the platform **fails closed** immediately, prohibiting silent direct fallback that would deanonymize the investigator or leak queries through host IP addresses.

---

## 2. Supported Regional Profiles

| Region Profile | Target Country | Environment Configuration | Verification Strategy |
|---|---|---|---|
| `DIRECT` | Unconstrained | Default host route | Direct socket connection authorized. |
| `INDIA` | India (`IN`) | `VPN_INDIA_PROXY` or `GATEWAY_SOUTH_ASIA_PROXY` | Live IP probe verifying `IN` GeoIP registration. |
| `UNITED_STATES` | United States (`US`) | `VPN_US_PROXY` or `GATEWAY_INTERNATIONAL_PROXY` | Live IP probe verifying `US` GeoIP registration. |
| `UNITED_KINGDOM` | United Kingdom (`GB`) | `VPN_UK_PROXY` | Live IP probe verifying `GB` GeoIP registration. |
| `ISOLATED_SCANNER`| Isolated Sandbox | `GATEWAY_SCANNER_PROXY` | Network namespace check preventing LAN access. |

---

## 3. Route Verification States

- `ROUTE_VERIFIED`: Egress IP was verified externally via HTTPS probe and matches expected geography.
- `CONFIG_REQUIRED`: Regional proxy or WireGuard interface is not configured in `.env`.
- `TUNNEL_UNAVAILABLE`: Configured interface or proxy is unreachable (e.g., connection refused, timeout).
- `EGRESS_VERIFICATION_FAILED`: Egress verification probe returned unexpected payload or failed integrity check.
- `REGION_MISMATCH`: Egress IP resolved to a geographic region differing from the requested profile.

---

## 4. Client Transport Isolation
The application creates dedicated `httpx.AsyncClient` instances bound specifically to the regional egress proxy using `egress_controller.get_httpx_client_for_route()`. This prevents DNS leakage and ensures requests never use host default interfaces.
