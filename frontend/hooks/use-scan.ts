import { useState, useEffect, useCallback } from 'react';
import { Scan, ScanSummary } from '@/types';
import { api } from '@/lib/api';

export function useScan(scanId: string | null) {
  const [scan, setScan] = useState<Scan | null>(null);
  const [summary, setSummary] = useState<ScanSummary | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchScan = useCallback(async () => {
    if (!scanId) return;
    try {
      setIsLoading(true);
      const fetchedScan = await api.getScan(scanId);
      setScan(fetchedScan);
      
      if (fetchedScan.status === 'complete') {
        const fetchedSummary = await api.getScanSummary(scanId);
        setSummary(fetchedSummary);
      }
      setError(null);
    } catch (err: any) {
      setError(err instanceof Error ? err : new Error(err?.message || 'Failed to fetch scan'));
    } finally {
      setIsLoading(false);
    }
  }, [scanId]);

  useEffect(() => {
    fetchScan();
  }, [fetchScan]);

  return { scan, summary, isLoading, error, refetch: fetchScan };
}
