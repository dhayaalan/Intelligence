from app.module_sdk.manifest import ModuleManifest, ModuleConfigField

MEDIA_INTELLIGENCE_MANIFEST = ModuleManifest(
    id="media_intelligence",
    name="Unified Media Forensics & Cross-Modal Intelligence",
    version="1.0.0",
    description=(
        "Comprehensive media forensics engine supporting image EXIF/GPS extraction, dual dHash/pHash perceptual hashing, "
        "cryptographic verification, C2PA Content Credentials provenance, OCR text extraction, video scene-cut frame sampling, "
        "audio stream inspection, speech-to-text timestamped transcription, and clue-to-clue investigation evidence linkage."
    ),
    capabilities=[
        "image_forensics",
        "video_analysis",
        "audio_analysis",
        "ocr_extraction",
        "c2pa_provenance",
        "perceptual_hashing",
        "duplicate_detection",
        "cross_modal_correlation",
        "investigation_evidence_vault"
    ],
    permissions=[
        "media_search",
        "media_upload",
        "media_analyze",
        "media_investigate"
    ],
    providers=[
        "media_hasher",
        "exif_metadata_extractor",
        "phash_perceptual_matcher",
        "c2pa_provenance_scanner",
        "pytesseract_ocr",
        "video_scene_sampler",
        "audio_stream_inspector",
        "whisper_transcription"
    ],
    configuration_schema=[
        ModuleConfigField(
            key="max_upload_size_mb",
            label="Maximum Upload Size (MB)",
            type="number",
            required=False,
            default=50.0,
            description="Maximum allowed media payload size in megabytes"
        ),
        ModuleConfigField(
            key="ocr_enabled",
            label="Enable OCR Text Extraction",
            type="boolean",
            required=False,
            default=True,
            description="Automatically run optical character recognition on uploaded images and video keyframes"
        ),
        ModuleConfigField(
            key="video_max_keyframes",
            label="Maximum Video Keyframes Sampled",
            type="number",
            required=False,
            default=24,
            description="Upper bound on extracted keyframes per video stream to prevent memory exhaustion"
        )
    ],
    ui_metadata={
        "icon": "Camera",
        "badge": "Media Forensics Engine",
        "color": "emerald"
    }
)
