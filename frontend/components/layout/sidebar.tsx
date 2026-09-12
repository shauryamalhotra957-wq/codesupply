"use client";

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { 
  LayoutDashboard, 
  Package, 
  ShieldAlert, 
  Network, 
  FileJson,
  FileText,
  History,
  Settings,
  ChevronLeft,
  Menu
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { useState } from 'react';
import { Sheet, SheetContent } from '@/components/ui/sheet';

interface SidebarProps {
  scanId?: string | null;
}

export function Sidebar({ scanId }: SidebarProps) {
  const pathname = usePathname();
  const [isOpen, setIsOpen] = useState(false);

  const routes = [
    {
      label: 'Overview',
      icon: LayoutDashboard,
      href: scanId ? `/scan/${scanId}` : '/',
      active: pathname === `/scan/${scanId}` || pathname === '/',
      disabled: !scanId && pathname !== '/',
      shortcut: '⌘1'
    },
    {
      label: 'Components',
      icon: Package,
      href: scanId ? `/scan/${scanId}/components` : '#',
      active: pathname === `/scan/${scanId}/components`,
      disabled: !scanId,
      shortcut: '⌘2'
    },
    {
      label: 'Vulnerabilities',
      icon: ShieldAlert,
      href: scanId ? `/scan/${scanId}/vulnerabilities` : '#',
      active: pathname === `/scan/${scanId}/vulnerabilities`,
      disabled: !scanId,
      shortcut: '⌘3'
    },
    {
      label: 'Dependency Graph',
      icon: Network,
      href: scanId ? `/scan/${scanId}/graph` : '#',
      active: pathname === `/scan/${scanId}/graph`,
      disabled: !scanId,
      shortcut: '⌘4'
    },
    {
      label: 'SBOM',
      icon: FileJson,
      href: scanId ? `/scan/${scanId}/sbom` : '#',
      active: pathname === `/scan/${scanId}/sbom`,
      disabled: !scanId,
      shortcut: '⌘5'
    },
    {
      label: 'Executive Report',
      icon: FileText,
      href: scanId ? `/scan/${scanId}/report` : '#',
      active: pathname === `/scan/${scanId}/report`,
      disabled: !scanId,
      shortcut: '⌘6'
    },
    {
      label: 'Scan History',
      icon: History,
      href: '/scans',
      active: pathname === '/scans',
      disabled: false,
      shortcut: '⌘7'
    },
    {
      label: 'Settings',
      icon: Settings,
      href: '/settings',
      active: pathname === '/settings',
      disabled: false,
      shortcut: '⌘8'
    }
  ];

  const SidebarContent = () => (
    <div className="flex h-full flex-col bg-card/50 backdrop-blur-2xl border-r border-border/40 selection:bg-purple-500/20">
      <div className="flex h-16 items-center border-b border-border/40 px-5">
        <Link href="/" className="flex items-center gap-3 font-bold group">
          <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-purple-600 to-indigo-500 flex items-center justify-center text-white shadow-[0_0_15px_rgba(139,92,246,0.3)] group-hover:scale-105 transition-transform">
            <ShieldAlert className="h-4 w-4" />
          </div>
          <span className="text-base tracking-tight font-black bg-gradient-to-r from-foreground to-foreground/70 bg-clip-text text-transparent">
            CodeSupply
          </span>
        </Link>
      </div>
      
      <div className="flex-1 overflow-auto py-5">
        <nav className="grid gap-1 px-3">
          {routes.map((route) => (
            <Link
              key={route.href}
              href={route.disabled ? '#' : route.href}
              className={cn(
                "flex items-center justify-between rounded-xl px-3.5 py-2.5 text-sm font-medium transition-all duration-200 group",
                route.active 
                  ? "bg-gradient-to-r from-purple-600/15 to-indigo-600/15 text-foreground border border-purple-500/30 shadow-[0_0_15px_rgba(139,92,246,0.1)] font-semibold" 
                  : "text-muted-foreground hover:bg-card/70 hover:text-foreground",
                route.disabled && "opacity-40 cursor-not-allowed pointer-events-none"
              )}
            >
              <div className="flex items-center gap-3">
                <route.icon className={cn("h-4 w-4", route.active ? "text-purple-400" : "text-muted-foreground group-hover:text-foreground")} />
                {route.label}
              </div>
              <span className={cn(
                "text-[10px] font-mono tracking-wider opacity-0 group-hover:opacity-100 transition-opacity px-1.5 py-0.5 rounded border border-border/40 bg-background/50",
                route.active ? "opacity-100 text-purple-400 border-purple-500/20" : "text-muted-foreground"
              )}>
                {route.shortcut}
              </span>
            </Link>
          ))}
        </nav>
      </div>

      <div className="mt-auto p-4 space-y-3 border-t border-border/40">
        {scanId && (
          <Link href="/">
            <Button variant="outline" className="w-full justify-start gap-2 rounded-xl border-border/60 bg-card/40 backdrop-blur-md text-xs font-medium hover:bg-card/70" size="sm">
              <ChevronLeft className="h-3.5 w-3.5" />
              New Scan
            </Button>
          </Link>
        )}
        <div className="flex items-center justify-between px-2 pt-1 text-[11px] text-muted-foreground">
          <div className="flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
            <span className="font-medium">Flow v1.2.0</span>
          </div>
          <span className="font-mono text-[10px] text-muted-foreground/60">SIH Edition</span>
        </div>
      </div>
    </div>
  );

  return (
    <>
      <div className="hidden lg:flex h-screen w-64 flex-col fixed inset-y-0 z-50">
        <SidebarContent />
      </div>
      
      <div className="lg:hidden fixed top-0 left-0 z-50 flex h-14 items-center px-4">
        <Button variant="ghost" size="icon" onClick={() => setIsOpen(true)}>
          <Menu className="h-5 w-5" />
        </Button>
      </div>

      <Sheet open={isOpen} onOpenChange={setIsOpen}>
        <SheetContent className="w-64 p-0">
          <SidebarContent />
        </SheetContent>
      </Sheet>
    </>
  );
}
