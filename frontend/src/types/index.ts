export type UserRole = 'SUPER_ADMIN' | 'TENANT_ADMIN' | 'ANALYST' | 'USER';

export interface User {
  id: string;
  email: string;
  name: string;
  role: UserRole;
  tenant_id: string;
  assigned_modules: string[];
  status: string;
  created_at: string;
  last_login?: string;
}

export interface Tenant {
  id: string;
  name: string;
  slug: string;
  entitled_modules: string[];
  status: string;
  created_at: string;
}

export interface Entity {
  id?: string;
  type: string;
  value: string;
  confidence: number;
  sources: string[];
  metadata: Record<string, any>;
  first_seen?: string;
  last_seen?: string;
}

export interface Relationship {
  id?: string;
  source_entity_value: string;
  target_entity_value: string;
  relationship_type: string;
  confidence: number;
  sources: string[];
  metadata: Record<string, any>;
}

export interface Evidence {
  id: string;
  source: string;
  provider: string;
  module: string;
  collection_method: string;
  reference: string;
  confidence: number;
  raw_data: any;
  hash: string;
  timestamp: string;
}

export interface TimelineEvent {
  id: string;
  timestamp: string;
  title: string;
  description: string;
  author: string;
  event_type: string;
  metadata: Record<string, any>;
}

export interface InvestigationNote {
  id: string;
  author_id: string;
  author_name: string;
  content: string;
  created_at: string;
}

export interface Investigation {
  id: string;
  tenant_id: string;
  title: string;
  description: string;
  summary?: string;
  priority?: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  status: 'open' | 'in_progress' | 'closed' | 'archived';
  target: string;
  target_type: string;
  selected_modules?: string[];
  search_id?: string;
  created_by: string;
  entity_ids: string[];
  evidence_ids: string[];
  relationships?: any[];
  timeline: TimelineEvent[];
  notes: InvestigationNote[];
  investigative_summary?: {
    what_we_know: string[];
    what_we_dont_know: string[];
    key_findings: Array<{
      title: string;
      description: string;
      confidence: string;
      severity: string;
    }>;
    investigative_leads: Array<{
      lead: string;
      why_it_matters: string;
      confidence: string;
      recommended_action: string;
    }>;
  };
  open_questions?: Array<{
    id: string;
    question: string;
    search_query: string;
  }>;
  recommended_actions?: Array<{
    id: string;
    title: string;
    description: string;
  }>;
  investigation_health?: {
    evidence_coverage: 'HIGH' | 'MEDIUM' | 'LOW';
    source_diversity: 'HIGH' | 'MEDIUM' | 'LOW';
    entity_resolution: 'HIGH' | 'MEDIUM' | 'LOW';
    temporal_coverage: 'HIGH' | 'MEDIUM' | 'LOW';
    unresolved_questions_count: number;
    conflicting_claims_count: number;
    primary_source_coverage: 'HIGH' | 'MEDIUM' | 'LOW';
  };
  created_at: string;
  updated_at: string;
}

export interface KeyFindingItem {
  id: string;
  title: string;
  description: string;
  why_it_matters: string;
  confidence: 'HIGH' | 'MEDIUM' | 'LOW';
  priority: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  evidence_count: number;
  sources: string[];
  action_type?: string;
  action_target?: string;
}

export interface InvestigativeLeadItem {
  id: string;
  lead: string;
  why_it_matters: string;
  evidence_refs: string[];
  confidence: 'HIGH' | 'MEDIUM' | 'LOW';
  recommended_action: string;
}

export interface PipelineTraceStage {
  stage: string;
  status: string;
  duration_ms: number;
  details: string;
}

export interface InvestigationSnapshot {
  relevant_findings_count: number;
  entities_count: number;
  relationships_count: number;
  evidence_count: number;
  sources_count: number;
  news_stories_count: number;
  high_priority_leads_count: number;
  potential_contradictions_count: number;
  unverified_claims_count: number;
}

export interface PaginatedInvestigationsResponse {
  items: Investigation[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  module_counts: Record<string, number>;
}

export interface ModuleConfigField {
  key: string;
  label: string;
  type: string;
  required: boolean;
  default?: any;
  description: string;
}

export interface ModuleRegistryItem {
  id: string;
  name: string;
  version: string;
  description: string;
  enabled: boolean;
  lifecycle_state: string;
  health_status: 'healthy' | 'degraded' | 'unavailable';
  health_message: string;
  latency_ms: number;
  capabilities: string[];
  permissions: string[];
  providers: string[];
  provider_statuses: Record<string, string>;
  configuration_schema: ModuleConfigField[];
  ui_metadata: Record<string, any>;
  total_executions: number;
  successful_executions: number;
  failed_executions: number;
  last_executed_at?: string;
}

export interface ModuleJobStatusRecord {
  module: string;
  module_name: string;
  job_id: string;
  status: string;
  duration_ms: number;
  sources: string[];
  error?: string;
}

export interface SearchResponse {
  search_id: string;
  query: string;
  target_type: string;
  intent?: string;
  intent_explanation?: string;
  selected_scopes?: string[];
  status: 'completed' | 'partial' | 'failed';
  investigation_id?: string;
  partial_warning?: string;
  module_jobs: ModuleJobStatusRecord[];
  entities: Entity[];
  relationships: Relationship[];
  evidence: Evidence[];
  investigation_snapshot?: InvestigationSnapshot;
  key_findings?: KeyFindingItem[];
  investigative_leads?: InvestigativeLeadItem[];
  pipeline_trace?: PipelineTraceStage[];
  stats: {
    total_duration_ms: number;
    modules_executed: number;
    entities_count: number;
    relationships_count: number;
    evidence_count: number;
  };
  executed_at: string;
}

export interface AuditLog {
  id: string;
  timestamp: string;
  tenant_id: string;
  user_id: string;
  action: string;
  resource_type: string;
  resource_id: string;
  details: Record<string, any>;
  ip_address: string;
}

export interface ProviderMetadata {
  provider_id: string;
  name: string;
  module_id: string;
  category: string;
  provider_type: string;
  capabilities: string[];
  supported_targets: string[];
  version: string;
  is_enabled: boolean;
  status: string;
  auth_required: boolean;
  timeout_seconds: number;
  rate_limit?: string;
  execution_count?: number;
  success_rate?: number;
}

export interface ProviderStats {
  total_providers: number;
  total_osint_providers: number;
  total_threat_intel_providers: number;
  enabled_providers: number;
  healthy_providers: number;
  categories: Record<string, number>;
}

