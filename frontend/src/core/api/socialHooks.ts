import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiRequest } from './client';

export type SocialPlatformType = 'bluesky' | 'telegram' | 'reddit' | 'mastodon' | 'youtube';
export type CredibilityBand = 'HIGH' | 'MODERATE' | 'LOW' | 'INAUTHENTIC';

export interface SocialPost {
  id: string;
  platform: SocialPlatformType;
  author: string;
  author_id: string;
  text: string;
  created_at: string;
  url: string;
  langs: string[];
  links: string[];
  likes_count: number;
  reposts_count: number;
  views_count?: number;
  channel_name?: string;
  media_urls: string[];
  is_forwarded?: boolean;
  forwarded_from?: string;
  sentiment?: string;
  entities: string[];
  credibility_score?: number;
}

export interface CibCluster {
  cluster_id: string;
  primary_topic: string;
  post_count: number;
  account_count: number;
  accounts: string[];
  start_time: string;
  end_time: string;
  duration_seconds: number;
  synchronization_velocity: number;
  shared_urls: string[];
  identical_phrases: string[];
  coordination_confidence: number;
  caveat_warning: string;
}

export interface CredibilityScore {
  target: string;
  platform: SocialPlatformType;
  overall_score: number;
  band: CredibilityBand;
  account_age_days?: number;
  post_velocity_per_day: number;
  has_custom_avatar: boolean;
  text_repetition_rate: number;
  domain_diversity_score: number;
  bot_probability: number;
  factors: Record<string, number>;
  rationale: string;
}

export interface YouTubeSubtitleSegment {
  start_seconds: number;
  duration_seconds: number;
  text: string;
}

export interface YouTubeSubtitleTrack {
  language: string;
  is_auto_generated: boolean;
  segments: YouTubeSubtitleSegment[];
  full_text: string;
}

export interface YouTubeComment {
  id: string;
  author: string;
  text: string;
  likes: number;
  published_at: string;
  sentiment?: string;
}

export interface YouTubeMetadata {
  video_id: string;
  url: string;
  title: string;
  channel_title: string;
  channel_id: string;
  channel_url: string;
  duration_seconds: number;
  view_count: number;
  like_count: number;
  comment_count: number;
  upload_date: string;
  description: string;
  thumbnail_url: string;
  tags: string[];
}

export interface YouTubeInvestigationResult {
  metadata: YouTubeMetadata;
  subtitles?: YouTubeSubtitleTrack;
  top_comments: YouTubeComment[];
  detected_entities: string[];
  detected_claims: string[];
  sentiment_summary: Record<string, any>;
}

export interface SocialSearchRequest {
  query: string;
  platforms?: SocialPlatformType[];
  limit?: number;
  min_credibility?: number;
  detect_cib?: boolean;
}

export interface SocialSearchResponse {
  search_id: string;
  query: string;
  total_results: number;
  results: SocialPost[];
  cib_clusters: CibCluster[];
  provider_statuses?: Record<string, string>;
  execution_time_ms: number;
}

export function useSocialSearch() {
  return useMutation<SocialSearchResponse, Error, SocialSearchRequest>({
    mutationFn: (req) => apiRequest<SocialSearchResponse>('/social/search', {
      method: 'POST',
      body: JSON.stringify(req),
    }),
  });
}

export function useCibAnalysis() {
  return useMutation<CibCluster[], Error, SocialPost[]>({
    mutationFn: (posts) => apiRequest<CibCluster[]>('/social/analyze/cib', {
      method: 'POST',
      body: JSON.stringify(posts),
    }),
  });
}

export function useCredibilityAnalysis() {
  return useMutation<CredibilityScore, Error, { target: string; platform: SocialPlatformType; posts: SocialPost[] }>({
    mutationFn: (data) => apiRequest<CredibilityScore>('/social/analyze/credibility', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  });
}

export function useYouTubeInvestigation() {
  return useMutation<YouTubeInvestigationResult, Error, { video_url_or_id: string }>({
    mutationFn: (data) => apiRequest<YouTubeInvestigationResult>('/social/youtube/video', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  });
}

export type RegionalGeography = 'SOUTH_INDIA' | 'NORTH_INDIA' | 'PAKISTAN' | 'BANGLADESH' | 'INTERNATIONAL';

export interface RegionalClaimItem {
  claim_text: string;
  original_language: string;
  translated_text?: string;
  speaker_or_attribution?: string;
  source_url: string;
  publisher: string;
  publication_time: string;
}

export interface RegionalPerspective {
  region: RegionalGeography;
  region_label: string;
  sample_size: number;
  primary_framing: string;
  observed_sentiment_summary: string;
  distinctive_regional_terms: string[];
  claims: RegionalClaimItem[];
  top_sources: string[];
  supporting_evidence_count: number;
  conflicting_evidence_count: number;
  collection_coverage_notes: string;
}

export interface RegionalNarrativeComparisonRequest {
  topic: string;
  seed_urls?: string[];
  selected_regions?: RegionalGeography[];
  preferred_languages?: string[];
  collection_limit?: number;
  egress_route?: 'DIRECT' | 'REGIONAL_GATEWAY_APPROVED' | 'ISOLATED_SCANNER';
  fail_closed?: boolean;
}

export interface RegionalNarrativeComparisonResponse {
  comparison_id: string;
  topic: string;
  timestamp: string;
  egress_status?: {
    route_type: string;
    gateway_name: string;
    is_active: boolean;
    fail_closed: boolean;
    egress_ip_masked: string;
    diagnostics: string;
  };
  regions_compared: RegionalPerspective[];
  key_similarities: string[];
  key_divergences: string[];
  media_reuse_detected: boolean;
  media_reuse_details?: string;
  controlled_variables: string[];
  uncontrolled_limitations: string[];
  investigator_advisory: string;
}

export function useRegionalNarrativeComparison() {
  return useMutation<RegionalNarrativeComparisonResponse, Error, RegionalNarrativeComparisonRequest>({
    mutationFn: (req) => apiRequest<RegionalNarrativeComparisonResponse>('/social/regional/compare', {
      method: 'POST',
      body: JSON.stringify(req),
    }),
  });
}

