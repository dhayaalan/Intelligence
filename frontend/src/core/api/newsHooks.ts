import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiRequest } from './client';

export type SearchMode = 'SEMANTIC' | 'EXACT' | 'BOOLEAN' | 'ENTITY' | 'TEMPORAL' | 'GEOGRAPHIC';
export type ContentCategory = 'all' | 'articles' | 'videos' | 'images' | 'social' | 'claims' | 'sources' | 'entities' | 'narratives' | 'evidence';

export interface QueryExpansionItem {
  parent_query_id: string;
  generated_query: string;
  generated_reason: string;
}

export interface GlobalCoverageItem {
  country: string;
  region: string;
  publisher: string;
  headline: string;
  framing: string;
  stance: 'CRITICAL' | 'SUPPORTIVE' | 'NEUTRAL' | 'ALARMIST';
  publication_date?: string;
  omitted_facts: string[];
  highlighted_aspects: string[];
}

export interface StoryCluster {
  cluster_id: string;
  primary_headline: string;
  article_count: number;
  publishers_count: number;
  countries_count: number;
  countries: string[];
  languages: string[];
  primary_source_name: string;
  primary_source_country: string;
  timeline_summary: string;
  independent_sources_count?: number;
  syndicated_count?: number;
  copied_count?: number;
  official_count?: number;
  source_independence_score?: number;
}

export interface NewsSearchResultItem {
  id: string;
  title: string;
  summary: string;
  source: string;
  publisher: string;
  canonical_url: string;
  content_type: 'article' | 'video' | 'image' | 'social_post' | 'claim';
  publication_date?: string;
  relevance_score: number;
  country?: string;
  author?: string;
  category?: string;
  language?: string;
  read_time_minutes?: number;
  cluster_id?: string;
  story_cluster?: StoryCluster;
  source_type?: string;
  is_independent?: boolean;
  detected_entities: string[];
  claim_indicators: string[];
  media_indicators: Record<string, any>;
  investigation_status: string;
  search_explanation: string;
  thumbnail_url?: string;
  hero_image?: string;
}

export interface NewsSearchResponse {
  search_id: string;
  original_query: string;
  normalized_query: string;
  search_mode: string;
  timestamp: string;
  detected_entities: string[];
  query_expansions: QueryExpansionItem[];
  total_results: number;
  results: NewsSearchResultItem[];
  category_counts: Record<string, number>;
  duration_ms: number;
}

export interface NewsSearchRequest {
  query: string;
  search_mode?: SearchMode;
  min_relevance?: number;
  category_filter?: ContentCategory;
  date_filter?: string;
  location_filter?: string;
  source_filter?: string;
  language_filter?: string;
  content_type_filter?: string;
}

export interface ExtractedClaim {
  id: string;
  claim_text: string;
  claim_type: string;
  subject?: string;
  predicate?: string;
  object_target?: string;
  quoted_source?: string;
  supporting_evidence_ids: string[];
  contradicting_evidence_ids: string[];
  status: string;
  confidence: number;
  provenance_reference: string;
}

export interface NewsEvidenceItem {
  id: string;
  title?: string;
  type?: string;
  evidence_type?: string;
  source: string;
  publisher?: string;
  source_url?: string;
  original_publication_time?: string;
  timestamp?: string;
  collection_time?: string;
  hash_value: string;
  extracted_text: string;
  claim_relationship: 'DIRECTLY_RELEVANT' | 'RELATED' | 'CONTEXTUAL' | 'UNRELATED' | 'SUPPORTS' | 'CONTRADICTS';
  retrieval_reason: string;
  reliability_score: number;
  verification_status: string;
  analyst_notes?: string;
  evidence_code?: string;
  extraction_method?: string;
  provenance_quality?: number | string;
}

export interface SourceLineageNode {
  id: string;
  label: string;
  node_type: 'ORIGINAL_SOURCE' | 'PRIMARY_ARTICLE' | 'SYNDICATE_REPRINT' | 'AGGREGATOR' | 'SOCIAL_AMPLIFIER' | 'DISCREDITED_OUTLET';
  published_at?: string;
  is_independent: boolean;
  amplification_rank: number;
}

export interface SourceLineageEdge {
  source_id: string;
  target_id: string;
  relationship_type: 'REPOSTED' | 'QUOTED' | 'AMPLIFIED' | 'COPIED_VERBATIM' | 'CONTRADICTED' | 'ORIGINATED';
  confidence: number;
}

export interface TemporalTimelineEvent {
  id: string;
  timestamp_label: string;
  iso_timestamp?: string;
  title: string;
  description: string;
  event_category: 'FIRST_KNOWN_APPEARANCE' | 'VIRAL_AMPLIFICATION' | 'REPRINT' | 'MAINSTREAM_REPORT' | 'FACT_CHECK_CORRECTION' | 'COUNTER_STATEMENT';
  actor_or_source: string;
  is_contradiction: boolean;
  evidence_id?: string;
}

export interface VideoTimelineSegment {
  start_timestamp: string;
  end_timestamp: string;
  segment_title: string;
  detection_type: 'SCENE_TRANSITION' | 'PERSON_DETECTED' | 'TEXT_OCR' | 'POTENTIAL_REUSED_SEGMENT' | 'AUDIO_DESYNC';
  keyframe_thumbnail_url?: string;
  description: string;
  confidence: number;
}

export interface VideoForensicsData {
  media_url?: string;
  duration_seconds: number;
  resolution: string;
  container_format: string;
  perceptual_fingerprint: string;
  sha256_hash: string;
  timeline_segments: VideoTimelineSegment[];
  is_authentic_media_false_context: boolean;
  is_manipulated_media: boolean;
  earliest_known_appearance?: string;
  earliest_source?: string;
  contextual_verdict: string;
}

export interface ImageForensicsData {
  image_url?: string;
  dimensions: string;
  sha256_hash: string;
  perceptual_hash: string;
  exif_metadata: Record<string, any>;
  ocr_detected_text: string[];
  detected_logos: string[];
  reverse_matches: Array<Record<string, any>>;
  reused_or_recycled: boolean;
}

export interface NarrativeCluster {
  id: string;
  narrative_title: string;
  core_assertion: string;
  framing_angle: string;
  first_detected_date: string;
  recurrence_count: number;
  amplification_speed: string;
  associated_entities: string[];
  associated_claims: string[];
  counter_evidence_summary?: string;
}

export interface EvidenceMatrixRow {
  claim_id: string;
  claim_text: string;
  claim_type: string;
  supporting_evidence: string[];
  contradicting_evidence: string[];
  status: string;
  confidence: number;
}

export interface ConfidenceBreakdown {
  evidence_quality: number;
  source_independence: number;
  temporal_consistency: number;
  media_verification: number;
  cross_source_corroboration: number;
  contradiction_strength: number;
  overall_confidence: number;
}

export interface WhyMisleadingReason {
  id: string;
  summary_text: string;
  linked_evidence_id?: string;
  factor_category: string;
}

export interface InvestigationAssessment {
  verdict: 'VERIFIED' | 'LIKELY TRUE' | 'PARTIALLY TRUE' | 'MISLEADING' | 'FALSE' | 'OUT OF CONTEXT' | 'MANIPULATED' | 'SATIRE' | 'UNVERIFIED' | 'INSUFFICIENT EVIDENCE';
  confidence_breakdown: ConfidenceBreakdown;
  primary_reason: string;
  detailed_explanation: string;
  why_misleading_reasons: WhyMisleadingReason[];
  context_verification: Record<string, string>;
}

export interface InvestigationArtifact {
  id: string;
  title: string;
  subtitle?: string;
  author?: string;
  publisher?: string;
  publication_date?: string;
  updated_date?: string;
  canonical_url?: string;
  domain?: string;
  language: string;
  article_body: string;
  paragraphs: string[];
  extracted_images: string[];
  extracted_videos: string[];
  hyperlinks: string[];
  quoted_individuals: string[];
  cited_statistics: string[];
}

export interface NewsInvestigationRecord {
  id: string;
  tenant_id: string;
  investigator_id: string;
  investigator_name: string;
  title: string;
  original_query: string;
  normalized_query: string;
  search_id?: string;
  status: 'PENDING' | 'RUNNING' | 'COMPLETED' | 'FAILED' | 'PARTIAL' | 'NO_DATA' | 'REQUIRES_REVIEW';
  artifact: InvestigationArtifact;
  claims: ExtractedClaim[];
  evidence_vault: NewsEvidenceItem[];
  source_lineage_nodes: SourceLineageNode[];
  source_lineage_edges: SourceLineageEdge[];
  timeline: TemporalTimelineEvent[];
  video_forensics?: VideoForensicsData;
  image_forensics?: ImageForensicsData;
  narratives: NarrativeCluster[];
  evidence_matrix: EvidenceMatrixRow[];
  assessment?: InvestigationAssessment;
  associated_case_id?: string;
  created_at: string;
  updated_at: string;
}

export interface InvestigationReport {
  report_id: string;
  investigation_id: string;
  title: string;
  generated_at: string;
  executive_assessment: string;
  original_query: string;
  investigated_content: Record<string, any>;
  core_claims: Array<Record<string, any>>;
  what_was_claimed: string;
  what_evidence_shows: string;
  source_analysis: string;
  media_analysis: string;
  timeline_summary: string;
  narrative_analysis: string;
  network_analysis: string;
  supporting_evidence: Array<Record<string, any>>;
  contradicting_evidence: Array<Record<string, any>>;
  confidence_metrics: ConfidenceBreakdown;
  limitations: string;
  final_verdict: string;
}

export interface NewsWatchlist {
  id: string;
  tenant_id: string;
  created_by: string;
  topic_query: string;
  monitored_entities: string[];
  monitored_domains: string[];
  check_interval_hours: number;
  last_triggered_at?: string;
  is_active: boolean;
  created_at: string;
}

export interface CreateInvestigationPayload {
  original_query: string;
  target_input: string;
  canonical_url?: string;
  preset_title?: string;
  search_id?: string;
}

// --- React Query Hooks ---

export function useNewsSearch() {
  return useMutation<NewsSearchResponse, Error, NewsSearchRequest>({
    mutationFn: (req) => apiRequest<NewsSearchResponse>('/news/search', {
      method: 'POST',
      body: JSON.stringify(req),
    }),
  });
}

export function useNewsSearchHistory() {
  return useQuery<Array<{
    search_id: string;
    query: string;
    search_mode: string;
    total_results: number;
    timestamp: string;
  }>>({
    queryKey: ['news', 'search', 'history'],
    queryFn: () => apiRequest('/news/search/history'),
  });
}

export function useNewsInvestigations() {
  return useQuery<NewsInvestigationRecord[]>({
    queryKey: ['news', 'investigations'],
    queryFn: () => apiRequest('/news/investigations'),
  });
}

export function useNewsInvestigation(investigationId: string | null) {
  return useQuery<NewsInvestigationRecord>({
    queryKey: ['news', 'investigations', investigationId],
    queryFn: () => apiRequest(`/news/investigations/${investigationId}`),
    enabled: Boolean(investigationId),
  });
}

export function useCreateNewsInvestigation() {
  const queryClient = useQueryClient();
  return useMutation<NewsInvestigationRecord, Error, CreateInvestigationPayload>({
    mutationFn: (payload) => apiRequest<NewsInvestigationRecord>('/news/investigations', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['news', 'investigations'] });
    },
  });
}

export function useReanalyzeNewsInvestigation() {
  const queryClient = useQueryClient();
  return useMutation<NewsInvestigationRecord, Error, string>({
    mutationFn: (investigationId) => apiRequest<NewsInvestigationRecord>(`/news/investigations/${investigationId}/analyze`, {
      method: 'POST',
    }),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['news', 'investigations', data.id] });
      queryClient.invalidateQueries({ queryKey: ['news', 'investigations'] });
    },
  });
}

export function useAddToCaseNewsInvestigation() {
  const queryClient = useQueryClient();
  return useMutation<any, Error, { investigationId: string; caseId: string; analystNotes?: string }>({
    mutationFn: ({ investigationId, caseId, analystNotes }) => apiRequest(`/news/investigations/${investigationId}/add-to-case`, {
      method: 'POST',
      body: JSON.stringify({ case_id: caseId, analyst_notes: analystNotes }),
    }),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['news', 'investigations', variables.investigationId] });
      queryClient.invalidateQueries({ queryKey: ['cases'] });
    },
  });
}

export function useNewsInvestigationReport(investigationId: string | null) {
  return useQuery<InvestigationReport>({
    queryKey: ['news', 'investigations', investigationId, 'report'],
    queryFn: () => apiRequest(`/news/investigations/${investigationId}/report`, {
      method: 'POST',
    }),
    enabled: Boolean(investigationId),
  });
}

export function useNewsWatchlists() {
  return useQuery<NewsWatchlist[]>({
    queryKey: ['news', 'watchlists'],
    queryFn: () => apiRequest('/news/watchlists'),
  });
}

export function useCreateNewsWatchlist() {
  const queryClient = useQueryClient();
  return useMutation<NewsWatchlist, Error, {
    topic_query: string;
    monitored_entities?: string[];
    monitored_domains?: string[];
    check_interval_hours?: number;
  }>({
    mutationFn: (payload) => apiRequest<NewsWatchlist>('/news/watchlists', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['news', 'watchlists'] });
    },
  });
}

export function useDeleteNewsWatchlist() {
  const queryClient = useQueryClient();
  return useMutation<any, Error, string>({
    mutationFn: (watchlistId) => apiRequest(`/news/watchlists/${watchlistId}`, {
      method: 'DELETE',
    }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['news', 'watchlists'] });
    },
  });
}

// --- Long-form Investigative News Article Interfaces & Hooks ---

export interface RelatedNewsItem {
  id: string;
  title: string;
  publisher: string;
  country: string;
  published_date?: string;
  relevance_score: number;
  connection_reason: string;
  thumbnail_url?: string;
  canonical_url?: string;
}

export interface ArticleSection {
  heading: string;
  paragraphs: string[];
  quote?: string;
  quote_author?: string;
  data_table?: {
    headers: string[];
    rows: string[][];
  };
}

export interface ResolvedEntity {
  canonical_id: string;
  canonical_name: string;
  aliases: string[];
  entity_type: string;
  confidence: number;
  role?: string;
  mention_count?: number;
  wikidata_id?: string;
}

export interface StoryGraphNode {
  id: string;
  label: string;
  node_type: string;
  metadata?: Record<string, any>;
}

export interface StoryGraphEdge {
  source_id: string;
  target_id: string;
  relationship: string;
  confidence?: number;
}

export interface StoryGraph {
  nodes: StoryGraphNode[];
  edges: StoryGraphEdge[];
}

export interface NewsArticle {
  id: string;
  title: string;
  subtitle?: string;
  category: string;
  publisher: string;
  source: string;
  domain?: string;
  country: string;
  language: string;
  author?: string;
  publication_date?: string;
  updated_date?: string;
  relevance_score: number;
  investigation_status: string;
  canonical_url?: string;
  hero_image?: string;
  hero_image_caption?: string;
  hero_image_forensic_note?: string;
  key_takeaways: string[];
  sections: ArticleSection[];
  body_paragraphs: string[];
  detected_entities: string[];
  resolved_entities?: ResolvedEntity[];
  claims: ExtractedClaim[];
  timeline: any[];
  evidence: NewsEvidenceItem[];
  lineage_nodes: SourceLineageNode[];
  lineage_edges: SourceLineageEdge[];
  story_graph?: StoryGraph;
  source_independence_breakdown?: Record<string, any>;
  claim_review_interoperability?: any;
  global_coverage: GlobalCoverageItem[];
  narratives: any[];
  story_cluster?: StoryCluster;
  related_news: RelatedNewsItem[];
  assessment?: any;
  why_misleading_reasons?: any[];
  read_time_minutes: number;
  video_forensics?: any;
  image_forensics?: any;
  associated_investigation_id?: string;
  is_deleted?: boolean;
  deleted_at?: string;
  deleted_by?: string;
  edited_by?: string;
  last_edited_at?: string;
  analyst_notes?: string;
}

export interface ClaimInvestigationResult {
  claim_text: string;
  claim_type: string;
  verdict: string;
  confidence: number;
  original_source: string;
  supporting_sources: Array<{ publisher: string; country: string; date: string; stance: string; credibility: number }>;
  contradicting_sources: Array<{ publisher: string; country: string; date: string; stance: string; credibility: number }>;
  timeline: Array<{ timestamp: string; event: string }>;
  assessment_notes: string;
  why_reasons: string[];
}

export function useNewsArticle(articleId: string | null, queryHint?: string) {
  return useQuery<NewsArticle>({
    queryKey: ['news', 'article', articleId, queryHint],
    queryFn: () => {
      const q = queryHint ? `?query_hint=${encodeURIComponent(queryHint)}` : '';
      return apiRequest<NewsArticle>(`/news/articles/${articleId}${q}`);
    },
    enabled: Boolean(articleId),
  });
}

export function useInvestigateClaim() {
  return useMutation<ClaimInvestigationResult, Error, { articleId: string; claimText: string }>({
    mutationFn: ({ articleId, claimText }) => apiRequest<ClaimInvestigationResult>(`/news/articles/${articleId}/investigate-claim`, {
      method: 'POST',
      body: JSON.stringify({ claim_text: claimText }),
    }),
  });
}

export function useCompareCoverage() {
  return useMutation<any, Error, { articleIds: string[] }>({
    mutationFn: ({ articleIds }) => apiRequest('/news/articles/compare', {
      method: 'POST',
      body: JSON.stringify({ article_ids: articleIds }),
    }),
  });
}

export interface UpdateNewsArticlePayload {
  title?: string;
  subtitle?: string;
  category?: string;
  verdict?: string;
  key_takeaways?: string[];
  analyst_notes?: string;
}

export interface DeleteNewsArticleResponse {
  id: string;
  is_deleted: boolean;
  status: string;
  message: string;
}

export function useUpdateNewsArticle() {
  const queryClient = useQueryClient();
  return useMutation<NewsArticle, Error, { articleId: string; updates: UpdateNewsArticlePayload }>({
    mutationFn: ({ articleId, updates }) =>
      apiRequest<NewsArticle>(`/news/articles/${articleId}`, {
        method: 'PUT',
        body: JSON.stringify(updates),
      }),
    onSuccess: (data, variables) => {
      queryClient.setQueryData(['news', 'article', variables.articleId], data);
      queryClient.invalidateQueries({ queryKey: ['news', 'article', variables.articleId] });
      queryClient.invalidateQueries({ queryKey: ['news', 'search'] });
    },
  });
}

export function useDeleteNewsArticle() {
  const queryClient = useQueryClient();
  return useMutation<DeleteNewsArticleResponse, Error, string>({
    mutationFn: (articleId: string) =>
      apiRequest<DeleteNewsArticleResponse>(`/news/articles/${articleId}`, {
        method: 'DELETE',
      }),
    onSuccess: (_, articleId) => {
      queryClient.removeQueries({ queryKey: ['news', 'article', articleId] });
      queryClient.invalidateQueries({ queryKey: ['news', 'search'] });
    },
  });
}

