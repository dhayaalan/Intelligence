from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field


class SearchMode(str, Enum):
    SEMANTIC = "SEMANTIC"
    EXACT = "EXACT"
    BOOLEAN = "BOOLEAN"
    ENTITY = "ENTITY"
    TEMPORAL = "TEMPORAL"
    GEOGRAPHIC = "GEOGRAPHIC"


class ContentCategory(str, Enum):
    ALL = "all"
    ARTICLES = "articles"
    VIDEOS = "videos"
    IMAGES = "images"
    SOCIAL = "social"
    CLAIMS = "claims"
    SOURCES = "sources"
    ENTITIES = "entities"
    NARRATIVES = "narratives"
    EVIDENCE = "evidence"


class ClaimType(str, Enum):
    FACTUAL = "factual"
    STATISTICAL = "statistical"
    HISTORICAL = "historical"
    GEOGRAPHIC = "geographic"
    POLITICAL = "political"
    SCIENTIFIC = "scientific"
    FINANCIAL = "financial"
    ATTRIBUTION = "attribution"
    QUOTATION = "quotation"
    VISUAL = "visual"
    TEMPORAL = "temporal"
    IDENTITY = "identity"
    EVENT = "event"


class VerificationVerdict(str, Enum):
    VERIFIED = "VERIFIED"
    LIKELY_TRUE = "LIKELY TRUE"
    PARTIALLY_TRUE = "PARTIALLY TRUE"
    MISLEADING = "MISLEADING"
    FALSE = "FALSE"
    OUT_OF_CONTEXT = "OUT OF CONTEXT"
    AUTHENTIC_MEDIA_FALSE_CONTEXT = "AUTHENTIC MEDIA (FALSE CONTEXT)"
    MANIPULATED = "MANIPULATED"
    FABRICATED = "FABRICATED"
    SATIRE = "SATIRE"
    UNVERIFIED = "UNVERIFIED"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT EVIDENCE"


class InvestigationStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    PARTIAL = "PARTIAL"
    NO_DATA = "NO_DATA"
    REQUIRES_REVIEW = "REQUIRES_REVIEW"


# --- Search Schemas ---

class QueryExpansionItem(BaseModel):
    parent_query_id: str
    generated_query: str
    generated_reason: str


class NewsSearchRequest(BaseModel):
    query: str
    search_mode: SearchMode = SearchMode.SEMANTIC
    min_relevance: float = 70.0  # 0 to 100 percentage
    category_filter: ContentCategory = ContentCategory.ALL
    date_filter: Optional[str] = None  # "today", "yesterday", "week", "month", or "YYYY-MM-DD..YYYY-MM-DD"
    location_filter: Optional[str] = None
    source_filter: Optional[str] = None
    language_filter: Optional[str] = "en"
    content_type_filter: Optional[str] = None


class GlobalCoverageItem(BaseModel):
    country: str
    region: str
    publisher: str
    headline: str
    framing: str
    stance: str = "NEUTRAL"  # CRITICAL, SUPPORTIVE, NEUTRAL, ALARMIST
    publication_date: Optional[str] = None
    omitted_facts: List[str] = Field(default_factory=list)
    highlighted_aspects: List[str] = Field(default_factory=list)


class StoryCluster(BaseModel):
    cluster_id: str
    primary_headline: str
    article_count: int = 1
    publishers_count: int = 1
    countries_count: int = 1
    countries: List[str] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=list)
    primary_source_name: str
    primary_source_country: str = "International Wire"
    timeline_summary: str = ""
    independent_sources_count: int = 1
    syndicated_count: int = 0
    copied_count: int = 0
    official_count: int = 0
    source_independence_score: float = 75.0


class NewsSearchResultItem(BaseModel):
    id: str
    title: str
    summary: str
    source: str
    publisher: str
    canonical_url: str
    content_type: str  # article, video, image, social_post, claim
    publication_date: Optional[str] = None
    relevance_score: float  # 0 to 100
    country: str = "International"
    author: Optional[str] = None
    category: str = "Global News"
    language: str = "en"
    read_time_minutes: int = 4
    cluster_id: Optional[str] = None
    story_cluster: Optional[StoryCluster] = None
    detected_entities: List[str] = Field(default_factory=list)
    claim_indicators: List[str] = Field(default_factory=list)
    media_indicators: Dict[str, Any] = Field(default_factory=dict)
    investigation_status: str = "UNASSESSED"
    search_explanation: str = ""
    thumbnail_url: Optional[str] = None
    hero_image: Optional[str] = None
    source_type: str = "NEWS"  # PRIMARY, SECONDARY, TERTIARY, OFFICIAL, NEWS, ACADEMIC, ARCHIVE, SOCIAL
    is_independent: bool = True


class NewsSearchResponse(BaseModel):
    search_id: str
    original_query: str
    normalized_query: str
    search_mode: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    detected_entities: List[str] = Field(default_factory=list)
    query_expansions: List[QueryExpansionItem] = Field(default_factory=list)
    total_results: int
    results: List[NewsSearchResultItem] = Field(default_factory=list)
    category_counts: Dict[str, int] = Field(default_factory=dict)
    duration_ms: float = 0.0


# --- Investigation Pipeline Schemas ---

class ExtractedClaim(BaseModel):
    id: str
    claim_text: str
    claim_type: ClaimType
    subject: Optional[str] = None
    predicate: Optional[str] = None
    object_target: Optional[str] = None
    date: Optional[str] = None
    location: Optional[str] = None
    entities: List[str] = Field(default_factory=list)
    supporting_evidence_ids: List[str] = Field(default_factory=list)
    contradicting_evidence_ids: List[str] = Field(default_factory=list)
    confidence: float = 0.0
    provenance: str = ""
    verification_status: str = "UNVERIFIED"


class NewsEvidenceItem(BaseModel):
    id: str
    investigation_id: str
    type: str  # ARCHIVED_REPORT, PRIMARY_STATEMENT, MEDIA_METADATA, CROSS_REFERENCE, CORROBORATION
    source: str
    source_url: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    original_publication_time: Optional[str] = None
    hash_value: str
    extracted_text: str
    screenshot_url: Optional[str] = None
    claim_relationship: str  # SUPPORTS, CONTRADICTS, CONTEXTUAL
    reliability_score: float  # 0 to 100
    verification_status: str = "VERIFIED"
    analyst_notes: Optional[str] = None
    retrieval_reason: str = ""  # Explain why this evidence was found
    evidence_code: Optional[str] = None  # EV-001, EV-002, etc.
    extraction_method: str = "forensic_verification"
    provenance_quality: Union[float, str] = 90.0


class SourceLineageNode(BaseModel):
    id: str
    name: str
    domain: str
    role: str  # ORIGINAL_SOURCE, WIRE_SERVICE, SYNDICATED_COPY, REWRITE, SOCIAL_AMPLIFIER
    first_publication_time: Optional[str] = None
    independence_score: float  # 0 to 100
    is_duplicate_copy: bool = False
    inherited_from_id: Optional[str] = None


class SourceLineageEdge(BaseModel):
    source_id: str
    target_id: str
    relationship: str  # SYNDICATED_TO, REWRITTEN_BY, AMPLIFIED_BY, CITED_BY


class TemporalTimelineEvent(BaseModel):
    id: str
    timestamp: str
    title: str
    description: str
    source_name: str
    event_type: str  # FIRST_PUBLICATION, REPOST, AMPLIFICATION, CORRECTION, CONTRADICTION
    evidence_id: Optional[str] = None
    is_anomaly: bool = False
    anomaly_note: Optional[str] = None


class VideoTimelineSegment(BaseModel):
    start_time: str
    end_time: str
    segment_type: str  # SCENE_CONTEXT, PERSON_DETECTED, TEXT_LOGO, REUSED_FOOTAGE
    description: str
    evidence_id: Optional[str] = None
    visual_match_score: Optional[float] = None
    frame_preview_url: Optional[str] = None


class VideoForensicsData(BaseModel):
    media_url: Optional[str] = None
    duration_seconds: float = 0.0
    resolution: str = ""
    container_format: str = ""
    perceptual_fingerprint: str = ""
    sha256_hash: str = ""
    timeline_segments: List[VideoTimelineSegment] = Field(default_factory=list)
    is_authentic_media_false_context: bool = False
    is_manipulated_media: bool = False
    earliest_known_appearance: Optional[str] = None
    earliest_source: Optional[str] = None
    contextual_verdict: str = ""


class ImageForensicsData(BaseModel):
    image_url: Optional[str] = None
    dimensions: str = ""
    sha256_hash: str = ""
    perceptual_hash: str = ""
    exif_metadata: Dict[str, Any] = Field(default_factory=dict)
    ocr_detected_text: List[str] = Field(default_factory=list)
    detected_logos: List[str] = Field(default_factory=list)
    reverse_matches: List[Dict[str, Any]] = Field(default_factory=list)
    reused_or_recycled: bool = False


class NarrativeCluster(BaseModel):
    id: str
    narrative_title: str
    core_assertion: str
    framing_angle: str
    first_detected_date: str
    recurrence_count: int
    amplification_speed: str  # HIGH, MODERATE, LOW
    associated_entities: List[str] = Field(default_factory=list)
    associated_claims: List[str] = Field(default_factory=list)
    counter_evidence_summary: Optional[str] = None


class EvidenceMatrixRow(BaseModel):
    claim_id: str
    claim_text: str
    claim_type: str
    supporting_evidence: List[str] = Field(default_factory=list)
    contradicting_evidence: List[str] = Field(default_factory=list)
    status: str
    confidence: float


class ConfidenceBreakdown(BaseModel):
    evidence_quality: float = 0.0
    source_independence: float = 0.0
    temporal_consistency: float = 0.0
    media_verification: float = 0.0
    cross_source_corroboration: float = 0.0
    contradiction_strength: float = 0.0
    overall_confidence: float = 0.0


class WhyMisleadingReason(BaseModel):
    id: str
    summary_text: str
    linked_evidence_id: Optional[str] = None
    factor_category: str  # TEMPORAL_MISMATCH, LOCATION_MISMATCH, SOURCE_FABRICATION, EDITED_FOOTAGE, RECYCLED_MEDIA


class InvestigationAssessment(BaseModel):
    verdict: VerificationVerdict
    confidence_breakdown: ConfidenceBreakdown
    primary_reason: str
    detailed_explanation: str
    why_misleading_reasons: List[WhyMisleadingReason] = Field(default_factory=list)
    context_verification: Dict[str, str] = Field(default_factory=dict)  # What was claimed vs what happened, etc.


class InvestigationArtifact(BaseModel):
    id: str
    title: str
    subtitle: Optional[str] = None
    author: Optional[str] = None
    publisher: Optional[str] = None
    publication_date: Optional[str] = None
    updated_date: Optional[str] = None
    canonical_url: Optional[str] = None
    domain: Optional[str] = None
    language: str = "en"
    article_body: str = ""
    paragraphs: List[str] = Field(default_factory=list)
    extracted_images: List[str] = Field(default_factory=list)
    extracted_videos: List[str] = Field(default_factory=list)
    hyperlinks: List[str] = Field(default_factory=list)
    quoted_individuals: List[str] = Field(default_factory=list)
    cited_statistics: List[str] = Field(default_factory=list)


class NewsInvestigationRecord(BaseModel):
    id: str
    tenant_id: str
    investigator_id: str
    investigator_name: str
    title: str
    original_query: str
    normalized_query: str
    search_id: Optional[str] = None
    status: InvestigationStatus = InvestigationStatus.PENDING
    artifact: InvestigationArtifact
    claims: List[ExtractedClaim] = Field(default_factory=list)
    evidence_vault: List[NewsEvidenceItem] = Field(default_factory=list)
    source_lineage_nodes: List[SourceLineageNode] = Field(default_factory=list)
    source_lineage_edges: List[SourceLineageEdge] = Field(default_factory=list)
    timeline: List[TemporalTimelineEvent] = Field(default_factory=list)
    video_forensics: Optional[VideoForensicsData] = None
    image_forensics: Optional[ImageForensicsData] = None
    narratives: List[NarrativeCluster] = Field(default_factory=list)
    evidence_matrix: List[EvidenceMatrixRow] = Field(default_factory=list)
    assessment: Optional[InvestigationAssessment] = None
    associated_case_id: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# --- Long-form Investigative News Article Schemas (DisInfoLab-inspired Information Architecture) ---
class RelatedNewsItem(BaseModel):
    id: str
    title: str
    publisher: str
    country: str = "International"
    published_date: Optional[str] = None
    relevance_score: float = 85.0
    connection_reason: str = ""
    thumbnail_url: Optional[str] = None
    canonical_url: Optional[str] = None


class ArticleSection(BaseModel):
    heading: str
    paragraphs: List[str] = Field(default_factory=list)
    quote: Optional[str] = None
    quote_author: Optional[str] = None
    data_table: Optional[Dict[str, Any]] = None


class ResolvedEntity(BaseModel):
    canonical_id: str
    canonical_name: str
    aliases: List[str] = Field(default_factory=list)
    entity_type: str = "ORGANIZATION"  # PERSON, ORGANIZATION, LOCATION, EVENT, PRODUCT
    confidence: float = 90.0
    role: str = "Subject"
    mention_count: int = 1
    wikidata_id: Optional[str] = None


class StoryGraphNode(BaseModel):
    id: str
    label: str
    node_type: str  # EVENT, ARTICLE, CLAIM, SOURCE, MEDIA, ACCOUNT, NARRATIVE, EVIDENCE
    metadata: Dict[str, Any] = Field(default_factory=dict)


class StoryGraphEdge(BaseModel):
    source_id: str
    target_id: str
    relationship: str  # published, mentioned, quoted, supports, contradicts, references, reposted, amplified, originated, related_to
    confidence: float = 1.0


class StoryGraph(BaseModel):
    nodes: List[StoryGraphNode] = Field(default_factory=list)
    edges: List[StoryGraphEdge] = Field(default_factory=list)


class NewsArticle(BaseModel):
    id: str
    title: str
    subtitle: Optional[str] = None
    category: str = "Investigative Research"
    publisher: str
    source: str
    domain: Optional[str] = None
    country: str = "Global"
    language: str = "en"
    author: Optional[str] = None
    publication_date: Optional[str] = None
    updated_date: Optional[str] = None
    relevance_score: float = 95.0
    investigation_status: str = "UNASSESSED"
    canonical_url: Optional[str] = None
    hero_image: Optional[str] = None
    hero_image_caption: Optional[str] = None
    hero_image_forensic_note: Optional[str] = None
    key_takeaways: List[str] = Field(default_factory=list)
    sections: List[ArticleSection] = Field(default_factory=list)
    body_paragraphs: List[str] = Field(default_factory=list)
    detected_entities: List[str] = Field(default_factory=list)
    resolved_entities: List[ResolvedEntity] = Field(default_factory=list)
    claims: List[ExtractedClaim] = Field(default_factory=list)
    timeline: List[TemporalTimelineEvent] = Field(default_factory=list)
    evidence: List[NewsEvidenceItem] = Field(default_factory=list)
    lineage_nodes: List[SourceLineageNode] = Field(default_factory=list)
    lineage_edges: List[SourceLineageEdge] = Field(default_factory=list)
    story_graph: Optional[StoryGraph] = None
    source_independence_breakdown: Optional[Dict[str, Any]] = None
    claim_review_interoperability: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None
    global_coverage: List[GlobalCoverageItem] = Field(default_factory=list)
    narratives: List[NarrativeCluster] = Field(default_factory=list)
    story_cluster: Optional[StoryCluster] = None
    related_news: List[RelatedNewsItem] = Field(default_factory=list)
    assessment: Optional[InvestigationAssessment] = None
    why_misleading_reasons: List[WhyMisleadingReason] = Field(default_factory=list)
    read_time_minutes: int = 5
    video_forensics: Optional[VideoForensicsData] = None
    image_forensics: Optional[ImageForensicsData] = None
    associated_investigation_id: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    is_deleted: bool = False
    deleted_at: Optional[str] = None
    deleted_by: Optional[str] = None
    edited_by: Optional[str] = None
    last_edited_at: Optional[str] = None
    analyst_notes: Optional[str] = None


class UpdateNewsArticleRequest(BaseModel):
    title: Optional[str] = None
    subtitle: Optional[str] = None
    category: Optional[str] = None
    verdict: Optional[str] = None
    key_takeaways: Optional[List[str]] = None
    analyst_notes: Optional[str] = None


class DeleteNewsArticleResponse(BaseModel):
    id: str
    is_deleted: bool
    status: str
    message: str


class InvestigateClaimRequest(BaseModel):
    claim_text: str
    context_article_id: Optional[str] = None


class ClaimInvestigationResult(BaseModel):
    claim_text: str
    claim_type: str = "factual"
    verdict: str = "UNVERIFIED"
    confidence: float = 75.0
    original_source: str = "Primary Wire"
    supporting_sources: List[Dict[str, Any]] = Field(default_factory=list)
    contradicting_sources: List[Dict[str, Any]] = Field(default_factory=list)
    timeline: List[Dict[str, Any]] = Field(default_factory=list)
    assessment_notes: str = ""
    why_reasons: List[str] = Field(default_factory=list)


# --- Investigation Report & Case Attachment Schemas ---
class InvestigationReport(BaseModel):
    report_id: str
    investigation_id: str
    title: str
    generated_at: str
    executive_assessment: str
    original_query: str
    investigated_content: Dict[str, Any]
    core_claims: List[Dict[str, Any]]
    what_was_claimed: str
    what_evidence_shows: str
    source_analysis: str
    media_analysis: str
    timeline_summary: str
    narrative_analysis: str
    network_analysis: str
    supporting_evidence: List[Dict[str, Any]]
    contradicting_evidence: List[Dict[str, Any]]
    confidence_metrics: ConfidenceBreakdown
    limitations: str
    final_verdict: str


class AddToCaseRequest(BaseModel):
    case_id: str
    analyst_notes: Optional[str] = None


class NewsWatchlist(BaseModel):
    id: str
    tenant_id: str
    created_by: str
    topic_query: str
    monitored_entities: List[str] = Field(default_factory=list)
    monitored_domains: List[str] = Field(default_factory=list)
    check_interval_hours: int = 6
    last_triggered_at: Optional[str] = None
    is_active: bool = True
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class NewsWatchlistCreate(BaseModel):
    topic_query: str
    monitored_entities: List[str] = Field(default_factory=list)
    monitored_domains: List[str] = Field(default_factory=list)
    check_interval_hours: int = 6
