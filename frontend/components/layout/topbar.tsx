"use client";

import { useScan } from '@/hooks/use-scan';
import { Skeleton } from '@/components/ui/skeleton';
import { StatusBadge } from '@/components/shared/status-badge';
import { Package } from 'lucide-react';

interface TopbarProps {
  scanId?: string | null;
}

export function Topbar({ scanId }: TopbarProps) {
  const { scan, isLoading } = useScan(scanId || null);

  if (!scanId) {
    return (
      <header className="flex h-14 items-center gap-4 border-b bg-background px-4 lg:px-6 pl-14 lg:pl-6 justify-end">
        <div className="text-sm font-medium text-muted-foreground">CodeSupply Scanner</div>
      </header>
    );
  }

  return (
    <header className="flex h-14 items-center gap-4 border-b bg-background px-4 lg:px-6 pl-14 lg:pl-6 justify-between lg:justify-end">
      <div className="flex items-center gap-4 flex-1 lg:flex-initial lg:mr-auto">
        {isLoading ? (
          <div className="flex items-center gap-2">
            <Skeleton className="h-5 w-5 rounded-md" />
            <Skeleton className="h-5 w-48" />
          </div>
        ) : scan ? (
          <div className="flex items-center gap-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-md bg-primary/10">
              <Package className="h-4 w-4 text-primary" />
            </div>
            <div className="flex flex-col">
              <span className="text-sm font-semibold leading-none">
                {scan.project_name || scan.filename}
              </span>
              <span className="text-xs text-muted-foreground mt-1">
                {scan.id.substring(0, 8)} • {(scan.file_size / 1024 / 1024).toFixed(2)} MB
              </span>
            </div>
            <div className="hidden sm:block ml-4">
              <StatusBadge status={scan.status} />
            </div>
          </div>
        ) : null}
      </div>
      
      <div className="flex items-center gap-2">
        {/* Placeholders for search or theme toggle */}
      </div>
    </header>
  );
}
