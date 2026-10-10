from app.module_sdk.manifest import ModuleManifest, ModuleConfigField

SOCIAL_MEDIA_INTELLIGENCE_MANIFEST = ModuleManifest(
    id="social_media_intelligence",
    name="Social Media Intelligence & Inauthentic Behavior Engine",
    version="2.0.0",
    description="Multi-platform social media intelligence collection (Bluesky, Telegram, Reddit, Mastodon, YouTube) with Coordinated Inauthentic Behavior (CIB) detection, bot credibility scoring, and AI agent investigation workflows.",
    capabilities=[
        "social_search",
        "live_firehose_monitoring",
        "channel_telemetry",
        "cib_cluster_analysis",
        "credibility_scoring",
        "youtube_video_intelligence",
        "persona_correlation",
        "evidence_correlation"
    ],
    permissions=["social_search", "social_investigate", "cib_detection"],
    providers=[
        "bluesky_collector",
        "telegram_collector",
        "reddit_collector",
        "mastodon_collector",
        "youtube_collector",
        "cib_engine",
        "credibility_engine"
    ],
    configuration_schema=[
        ModuleConfigField(
            key="enable_live_firehose",
            label="Enable Bluesky Live Firehose",
            type="boolean",
            required=False,
            default=True,
            description="Allow live streaming connection to Bluesky Jetstream firehose"
        ),
        ModuleConfigField(
            key="cib_burst_window_seconds",
            label="CIB Temporal Burst Window (s)",
            type="number",
            required=False,
            default=60.0,
            description="Max duration between posts across accounts to consider synchronized amplification"
        ),
        ModuleConfigField(
            key="min_credibility_threshold",
            label="Credibility Score Threshold",
            type="number",
            required=False,
            default=40.0,
            description="Threshold below which accounts are flagged as suspicious or likely inauthentic"
        )
    ],
    ui_metadata={
        "icon": "Share2",
        "badge": "Multi-Platform OSINT & CIB Engine",
        "color": "cyan"
    }
)
