"use client";

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { 
  LayoutDashboard, 
  Package, 
  ShieldAlert, 
  Network, 
  FileJson,
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
      label: 'Scan History',
      icon: History,
      href: '/scans',
      active: pathname === '/scans',
      disabled: false,
      shortcut: '⌘6'
    }
  ];

  const SidebarContent = () => (
    <div className="flex h-full flex-col bg-card border-r">
      <div className="flex h-14 items-center border-b px-4 bg-gradient-to-r from-background to-muted/50">
        <Link href="/" className="flex items-center gap-2 font-bold">
          <ShieldAlert className="h-5 w-5 text-primary" />
          <span className="text-lg tracking-tight text-gradient">CodeSupply</span>
        </Link>
      </div>
      
      <div className="flex-1 overflow-auto py-4">
        <nav className="grid gap-1 px-2">
          {routes.map((route) => (
            <Link
              key={route.href}
              href={route.disabled ? '#' : route.href}
              className={cn(
                "flex items-center justify-between rounded-md px-3 py-2 text-sm font-medium transition-colors group",
                route.active 
                  ? "bg-primary text-primary-foreground" 
                  : "text-muted-foreground hover:bg-muted hover:text-foreground",
                route.disabled && "opacity-50 cursor-not-allowed pointer-events-none"
              )}
            >
              <div className="flex items-center gap-3">
                <route.icon className="h-4 w-4" />
                {route.label}
              </div>
              <span className={cn(
                "text-xs tracking-widest opacity-0 group-hover:opacity-100 transition-opacity",
                route.active ? "opacity-100 text-primary-foreground/70" : "text-muted-foreground"
              )}>
                {route.shortcut}
              </span>
            </Link>
          ))}
        </nav>
      </div>

      <div className="mt-auto p-4 space-y-4">
        {scanId && (
          <Link href="/">
            <Button variant="outline" className="w-full justify-start gap-2" size="sm">
              <ChevronLeft className="h-4 w-4" />
              New Scan
            </Button>
          </Link>
        )}
        <div className="text-center text-xs text-muted-foreground/70 font-medium">
          v1.0
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
