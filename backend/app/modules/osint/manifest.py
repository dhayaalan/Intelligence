from app.module_sdk.manifest import ModuleManifest, ModuleConfigField

OSINT_MANIFEST = ModuleManifest(
    id="osint",
    name="OSINT Intelligence",
    version="1.0.0",
    description="Comprehensive Open Source Intelligence engine covering recon, transforms, and public footprint analysis.",
    capabilities=["search", "enrichment", "entity_discovery"],
    permissions=["search", "view_results"],
    providers=["spiderfoot", "shodan", "maltego", "theharvester", "google_dork", "image_osint", "username_recon"],
    configuration_schema=[
        ModuleConfigField(
            key="spiderfoot_url",
            label="SpiderFoot Server URL",
            type="url",
            required=False,
            default="http://localhost:5001",
            description="REST endpoint for external SpiderFoot server"
        ),
        ModuleConfigField(
            key="shodan_api_key",
            label="Shodan API Key",
            type="secret",
            required=False,
            default="",
            description="Shodan API key for host banner enrichment"
        ),
        ModuleConfigField(
            key="passive_only",
            label="Passive Reconnaissance Only",
            type="boolean",
            required=False,
            default=True,
            description="Enforces strict passive reconnaissance mode without direct active scanning"
        )
    ],
    ui_metadata={
        "icon": "Globe",
        "badge": "Active Recon & Passive Intel",
        "color": "sky"
    }
)
