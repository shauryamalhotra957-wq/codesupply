"use client";

import { useScanPolling } from '@/hooks/use-scan-polling';
import { ScanProgress } from '@/components/scan/scan-progress';
import { DashboardOverview } from '@/components/dashboard/overview';
import { ErrorState } from '@/components/shared/error-state';
import { Skeleton } from '@/components/ui/skeleton';
import { api } from '@/lib/api';

export default function ScanPage({ params }: { params: { id: string } }) {
  const { scan, error } = useScanPolling(params.id);

  if (error && !scan) {
    return (
      <div className="h-full flex items-center justify-center p-6">
        <ErrorState 
          title="Failed to load scan"
          description={error.message || "An unexpected error occurred."}
          onRetry={() => window.location.reload()}
        />
      </div>
    );
  }

  if (!scan) {
    return (
      <div className="p-6 space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => (
            <Skeleton key={i} className="h-32 w-full rounded-xl" />
          ))}
        </div>
        <Skeleton className="h-96 w-full rounded-xl" />
      </div>
    );
  }

  if (scan.status === 'failed') {
    return (
      <div className="h-full flex items-center justify-center p-6">
        <ErrorState 
          title="Scan Failed"
          description={scan.error_message || "CodeSupply couldn't complete dependency analysis."}
          onRetry={async () => {
            try {
              await api.retryScan(scan.id);
              window.location.reload();
            } catch (err) {
              console.error("Retry failed", err);
            }
          }}
        />
      </div>
    );
  }

  if (scan.status !== 'complete') {
    return (
      <div className="max-w-3xl mx-auto p-6 pt-12">
        <ScanProgress scan={scan} />
      </div>
    );
  }

  return (
    <div className="p-6">
      <DashboardOverview scanId={scan.id} />
    </div>
  );
}
