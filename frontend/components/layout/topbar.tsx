"use client";

import { useScan } from '@/hooks/use-scan';
import { Skeleton } from '@/components/ui/skeleton';
import { StatusBadge } from '@/components/shared/status-badge';
import { Package, Sun, Moon, Github } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useState, useEffect } from 'react';
import Link from 'next/link';

interface TopbarProps {
  scanId?: string | null;
}

export function Topbar({ scanId }: TopbarProps) {
  const { scan, isLoading } = useScan(scanId || null);
  const [isDark, setIsDark] = useState(false);

  useEffect(() => {
    setIsDark(document.documentElement.classList.contains('dark'));
  }, []);

  const toggleTheme = () => {
    const root = document.documentElement;
    if (root.classList.contains('dark')) {
      root.classList.remove('dark');
      localStorage.setItem('theme', 'light');
      setIsDark(false);
    } else {
      root.classList.add('dark');
      localStorage.setItem('theme', 'dark');
      setIsDark(true);
    }
  };

  const Actions = () => (
    <div className="flex items-center gap-2">
      <Link href="https://github.com/shauryamalhotra957-wq/codesupply" target="_blank" rel="noreferrer">
        <Button variant="ghost" size="icon" className="rounded-full h-9 w-9 text-muted-foreground hover:text-foreground hover:bg-card/70">
          <Github className="h-4 w-4" />
        </Button>
      </Link>
      <Button variant="ghost" size="icon" onClick={toggleTheme} className="rounded-full h-9 w-9 text-muted-foreground hover:text-foreground hover:bg-card/70">
        {isDark ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
      </Button>
    </div>
  );

  if (!scanId) {
    return (
      <header className="flex h-16 items-center gap-4 border-b border-border/40 bg-card/40 backdrop-blur-2xl px-5 lg:px-8 pl-14 lg:pl-8 justify-between lg:justify-end sticky top-0 z-40">
        <div className="flex-1 text-xs font-semibold uppercase tracking-wider text-muted-foreground lg:text-right mr-4 lg:mr-0 flex items-center lg:justify-end gap-2">
          <span className="w-2 h-2 rounded-full bg-purple-500 animate-pulse" />
          <span>CodeSupply Intelligence Engine</span>
        </div>
        <Actions />
      </header>
    );
  }

  return (
    <header className="flex h-16 items-center gap-4 border-b border-border/40 bg-card/40 backdrop-blur-2xl px-5 lg:px-8 pl-14 lg:pl-8 justify-between lg:justify-end sticky top-0 z-40">
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
      
      <Actions />
    </header>
  );
}
