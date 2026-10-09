from app.module_sdk.manifest import ModuleManifest, ModuleConfigField

NEWS_INTELLIGENCE_MANIFEST = ModuleManifest(
    id="news_intelligence",
    name="News Intelligence Investigation Engine",
    version="2.0.0",
    description="Search-driven news intelligence investigation engine with deep claim decomposition, multi-source lineage, media forensics, narrative clustering, and explainable confidence scoring.",
    capabilities=[
        "search",
        "investigation",
        "claim_extraction",
        "source_lineage",
        "media_forensics",
        "narrative_clustering",
        "evidence_correlation"
    ],
    permissions=["news_search", "news_investigate"],
    providers=["rss_aggregator", "article_extractor", "media_forensics", "semantic_search"],
    configuration_schema=[
        ModuleConfigField(
            key="min_relevance_threshold",
            label="Default Minimum Relevance (%)",
            type="number",
            required=False,
            default=60.0,
            description="Minimum relevance percentage for primary investigation workspace"
        ),
        ModuleConfigField(
            key="enable_deep_forensics",
            label="Enable Media Forensics & Lineage",
            type="boolean",
            required=False,
            default=True,
            description="Perform perceptual hashing, video timeline segmentation, and copycat lineage detection"
        )
    ],
    ui_metadata={
        "icon": "Newspaper",
        "badge": "Search-Driven Investigation Engine",
        "color": "emerald"
    }
)
