from app.module_sdk.manifest import ModuleManifest, ModuleConfigField

THREAT_INTEL_MANIFEST = ModuleManifest(
    id="threat_intelligence",
    name="Threat Intelligence",
    version="1.0.0",
    description="Proactive cybersecurity intelligence, threat indicator enrichment, vulnerability assessment, and attack surface analytics.",
    capabilities=["search", "enrichment", "threat_assessment", "vulnerability_intel"],
    permissions=["search", "view_results"],
    providers=["dns_intel", "host_discovery", "service_discovery", "zap_scanner", "vulnerability_intel", "ioc_feed", "tls_inspector", "web_crawler"],
    configuration_schema=[
        ModuleConfigField(
            key="zap_api_endpoint",
            label="OWASP ZAP API Endpoint",
            type="url",
            required=False,
            default="http://localhost:8080",
            description="REST endpoint for automated vulnerability scanning"
        ),
        ModuleConfigField(
            key="ioc_feed_threshold",
            label="IOC Threat Score Minimum Threshold",
            type="integer",
            required=False,
            default=50,
            description="Minimum threat score (0-100) to trigger an active threat indicator alert"
        ),
        ModuleConfigField(
            key="enable_active_probing",
            label="Enable Active Port & Service Probing",
            type="boolean",
            required=False,
            default=True,
            description="Allows non-intrusive TCP socket handshake verification for exposed services"
        )
    ],
    ui_metadata={
        "icon": "ShieldAlert",
        "badge": "Threat Surface & IOCs",
        "color": "rose"
    }
)
