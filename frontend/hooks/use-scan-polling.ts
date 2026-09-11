import { useState, useEffect } from 'react';
import { Scan } from '@/types';
import { api } from '@/lib/api';

export function useScanPolling(scanId: string | null) {
  const [scan, setScan] = useState<Scan | null>(null);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    if (!scanId) return;

    let timeoutId: NodeJS.Timeout;
    let ws: WebSocket | null = null;
    let isActive = true;

    const fetchInitial = async () => {
      try {
        const fetchedScan = await api.getScan(scanId);
        if (isActive) {
          setScan(fetchedScan);
          setError(null);
          if (fetchedScan.status !== 'complete' && fetchedScan.status !== 'failed') {
            setupWebSocket();
          }
        }
      } catch (err: any) {
        if (isActive) {
          setError(err instanceof Error ? err : new Error(err?.message || 'Failed to poll scan'));
          timeoutId = setTimeout(fetchInitial, 5000);
        }
      }
    };

    const setupWebSocket = () => {
      const base = (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000')
        .replace(/\/api\/?$/, '')
        .replace(/^http/, 'ws');
      ws = new WebSocket(`${base}/api/scans/${scanId}/ws`);

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          setScan(data);
        } catch (e) {
          console.error("Invalid WS message", e);
        }
      };

      ws.onclose = () => {
        if (isActive && scan?.status !== 'complete' && scan?.status !== 'failed') {
          timeoutId = setTimeout(poll, 2000);
        }
      };
    };

    const poll = async () => {
      try {
        const fetchedScan = await api.getScan(scanId);
        if (isActive) {
          setScan(fetchedScan);
          if (fetchedScan.status !== 'complete' && fetchedScan.status !== 'failed') {
            timeoutId = setTimeout(poll, 2000);
          }
        }
      } catch (err) {
        if (isActive) {
           timeoutId = setTimeout(poll, 5000);
        }
      }
    };

    fetchInitial();

    return () => {
      isActive = false;
      if (timeoutId) clearTimeout(timeoutId);
      if (ws) ws.close();
    };
  }, [scanId]);

  return { scan, error };
}
