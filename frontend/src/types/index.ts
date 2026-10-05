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
  timeline: TimelineEvent[];
  notes: InvestigationNote[];
  created_at: string;
  updated_at: string;
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
  status: 'completed' | 'partial' | 'failed';
  investigation_id?: string;
  partial_warning?: string;
  module_jobs: ModuleJobStatusRecord[];
  entities: Entity[];
  relationships: Relationship[];
  evidence: Evidence[];
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

