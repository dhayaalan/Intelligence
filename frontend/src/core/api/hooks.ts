import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiRequest } from './client';

export interface PlatformDashboardData {
  total_tenants: number;
  active_tenants: number;
  suspended_tenants: number;
  total_users: number;
  tenant_admins: number;
  analysts: number;
  investigators: number;
  total_cases: number;
  active_investigations: number;
  osint_tool_runs: number;
  threat_intelligence_runs: number;
  evidence_collected: number;
  findings_count: number;
  reports_count: number;
  storage_usage_bytes: number;
  system_health: {
    status: string;
    database: string;
    message: string;
  };
  recent_activity: any[];
}

export interface TenantSummary {
  id: string;
  name: string;
  slug: string;
  description?: string;
  industry?: string;
  country?: string;
  timezone?: string;
  status: 'active' | 'suspended';
  entitled_modules: string[];
  created_at: string;
  admin?: {
    id: string;
    name: string;
    email: string;
    phone?: string;
  };
  user_count?: number;
  case_count?: number;
}

export interface ToolItem {
  id: string;
  name: string;
  category: string;
  description: string;
  provider: string;
  module_id: string;
  version: string;
  execution_type: string;
  status: 'AVAILABLE' | 'CONFIG_REQUIRED' | 'COMING_SOON' | 'DISABLED';
  requires_api_key: boolean;
  supported_inputs: string[];
  usage_count: number;
  last_run?: string;
}

export interface DashboardSummary {
  total_cases: number;
  active_investigations: number;
  evidence_collected: number;
  entities_correlated: number;
  total_searches: number;
  total_findings: number;
  critical_threats: number;
  reports_generated: number;
  recent_activity: any[];
}

// 1. Platform & Tenant Hooks
export function usePlatformDashboard() {
  return useQuery<PlatformDashboardData>({
    queryKey: ['platform-dashboard'],
    queryFn: () => apiRequest<PlatformDashboardData>('/platform/dashboard'),
    refetchInterval: 30000,
  });
}

export function useTenants() {
  return useQuery<TenantSummary[]>({
    queryKey: ['tenants'],
    queryFn: () => apiRequest<TenantSummary[]>('/platform/tenants'),
  });
}

export function useTenant(tenantId: string) {
  return useQuery<TenantSummary>({
    queryKey: ['tenant', tenantId],
    queryFn: () => apiRequest<TenantSummary>(`/tenants/${tenantId}`),
    enabled: Boolean(tenantId),
  });
}

export function useCreateTenant() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: any) =>
      apiRequest('/platform/tenants', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tenants'] });
      queryClient.invalidateQueries({ queryKey: ['platform-dashboard'] });
    },
  });
}

export function useToggleTenantStatus() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ tenantId, status }: { tenantId: string; status: 'active' | 'suspended' }) =>
      apiRequest(`/platform/tenants/${tenantId}/status`, {
        method: 'PATCH',
        body: JSON.stringify({ status }),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tenants'] });
      queryClient.invalidateQueries({ queryKey: ['platform-dashboard'] });
    },
  });
}

// 2. User Management Hooks
export function useUsers(tenantId?: string) {
  return useQuery<any[]>({
    queryKey: ['users', tenantId],
    queryFn: () => {
      const url = tenantId ? `/users?tenant_id=${tenantId}` : '/users';
      return apiRequest<any[]>(url);
    },
  });
}

export function usePlatformUsers() {
  return useQuery<any[]>({
    queryKey: ['platform-users'],
    queryFn: () => apiRequest<any[]>('/platform/users'),
  });
}

export function useCreateUser() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: any) =>
      apiRequest('/users', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
      queryClient.invalidateQueries({ queryKey: ['platform-users'] });
      queryClient.invalidateQueries({ queryKey: ['platform-dashboard'] });
    },
  });
}

// 3. Cases & Investigations Hooks
export function useCases() {
  return useQuery<any[]>({
    queryKey: ['cases'],
    queryFn: () => apiRequest<any[]>('/cases'),
  });
}

export function useInvestigations(status?: string) {
  return useQuery<any[]>({
    queryKey: ['investigations', status],
    queryFn: () => {
      const url = status ? `/investigations?status=${status}` : '/investigations';
      return apiRequest<any[]>(url);
    },
  });
}

// 4. Evidence, Findings, Reports
export function useEvidence(investigationId?: string) {
  return useQuery<any[]>({
    queryKey: ['evidence', investigationId],
    queryFn: () => {
      const url = investigationId ? `/evidence?investigation_id=${investigationId}` : '/evidence';
      return apiRequest<any[]>(url);
    },
  });
}

export function useFindings(investigationId?: string) {
  return useQuery<any[]>({
    queryKey: ['findings', investigationId],
    queryFn: () => {
      const url = investigationId ? `/findings?investigation_id=${investigationId}` : '/findings';
      return apiRequest<any[]>(url);
    },
  });
}

export function useReports(investigationId?: string) {
  return useQuery<any[]>({
    queryKey: ['reports', investigationId],
    queryFn: () => {
      const url = investigationId ? `/reports?investigation_id=${investigationId}` : '/reports';
      return apiRequest<any[]>(url);
    },
  });
}

// 5. Tools & OSINT / Threat Hooks
export function useTools(category?: string, moduleId?: string) {
  return useQuery<ToolItem[]>({
    queryKey: ['tools', category, moduleId],
    queryFn: () => {
      const params = new URLSearchParams();
      if (category) params.append('category', category);
      if (moduleId) params.append('module_id', moduleId);
      const q = params.toString();
      return apiRequest<ToolItem[]>(`/tools${q ? `?${q}` : ''}`);
    },
  });
}

export function useOsintTools() {
  return useTools(undefined, 'osint');
}

export function useThreatTools() {
  return useTools(undefined, 'threat_intelligence');
}

export function useOsintSearch() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (searchPayload: any) =>
      apiRequest('/search/execute', {
        method: 'POST',
        body: JSON.stringify(searchPayload),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['searches'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard-summary'] });
    },
  });
}

export function useOsintResults(searchId: string) {
  return useQuery<any>({
    queryKey: ['osint-results', searchId],
    queryFn: () => apiRequest(`/search/${searchId}`),
    enabled: Boolean(searchId),
  });
}

export function useThreatScans() {
  return useQuery<any[]>({
    queryKey: ['threat-scans'],
    queryFn: () => apiRequest<any[]>('/threat-intelligence/scans'),
    retry: false,
  });
}

// 6. Organization Dashboard
export function useDashboard() {
  return useQuery<DashboardSummary>({
    queryKey: ['dashboard-summary'],
    queryFn: () => apiRequest<DashboardSummary>('/dashboard/summary'),
    refetchInterval: 15000,
  });
}

// 7. Audit Logs
export function useAuditLogs(limit: number = 50) {
  return useQuery<any[]>({
    queryKey: ['audit-logs', limit],
    queryFn: () => apiRequest<any[]>(`/audit?limit=${limit}`),
  });
}

export function usePlatformAuditLogs(limit: number = 100) {
  return useQuery<any[]>({
    queryKey: ['platform-audit-logs', limit],
    queryFn: () => apiRequest<any[]>(`/platform/audit-logs?limit=${limit}`),
  });
}
