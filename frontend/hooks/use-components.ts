import { useState, useEffect } from 'react';
import { ComponentListResponse } from '@/types';
import { api } from '@/lib/api';

export function useComponents(scanId: string, params: Record<string, any>) {
  const [data, setData] = useState<ComponentListResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const fetchComponents = async () => {
      if (!scanId) return;
      try {
        setIsLoading(true);
        const fetched = await api.getComponents(scanId, params);
        setData(fetched);
        setError(null);
      } catch (err: any) {
        setError(err instanceof Error ? err : new Error(err?.message || 'Failed to fetch components'));
      } finally {
        setIsLoading(false);
      }
    };
    
    // Add a slight debounce to avoid too many requests when typing
    const timeoutId = setTimeout(fetchComponents, 300);
    return () => clearTimeout(timeoutId);
  }, [scanId, JSON.stringify(params)]);

  return { 
    components: data?.items || [], 
    total: data?.total || 0,
    totalPages: data?.total_pages || 0,
    isLoading, 
    error 
  };
}
