import { useQuery } from '@tanstack/react-query';
import { apiRequest } from './client';

export interface MLServiceStatusResponse {
  status: 'not_configured' | 'available' | 'unavailable';
  is_configured: boolean;
  service_url: string | null;
  message: string;
  contract_version: string;
  supported_capabilities: string[];
}

export function useMLServiceStatus() {
  return useQuery<MLServiceStatusResponse, Error>({
    queryKey: ['mlServiceStatus'],
    queryFn: () => apiRequest<MLServiceStatusResponse>('/ml/status'),
    retry: 1,
  });
}
