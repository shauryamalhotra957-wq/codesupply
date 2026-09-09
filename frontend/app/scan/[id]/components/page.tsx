"use client";

import { useState } from 'react';
import { useComponents } from '@/hooks/use-components';
import { ComponentListResponse, Component } from '@/types';
import { 
  Table, 
  TableBody, 
  TableCell, 
  TableHead, 
  TableHeader, 
  TableRow 
} from '@/components/ui/table';
import { Input } from '@/components/ui/input';
import { Select } from '@/components/ui/select';
import { RiskBadge } from '@/components/shared/risk-badge';
import { EcosystemBadge } from '@/components/shared/ecosystem-badge';
import { ConfidenceBadge } from '@/components/shared/confidence-badge';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { ComponentDetail } from '@/components/components/component-detail';
import { Search } from 'lucide-react';

export default function ComponentsPage({ params }: { params: { id: string } }) {
  const [searchTerm, setSearchTerm] = useState("");
  const [riskFilter, setRiskFilter] = useState("");
  const [ecosystemFilter, setEcosystemFilter] = useState("");
  const [page, setPage] = useState(1);
  const [selectedComponent, setSelectedComponent] = useState<Component | null>(null);

  const { components, total, isLoading, totalPages } = useComponents(params.id, {
    q: searchTerm,
    risk_level: riskFilter !== 'all' ? riskFilter : undefined,
    ecosystem: ecosystemFilter !== 'all' ? ecosystemFilter : undefined,
    page,
    per_page: 50
  });

  return (
    <div className="p-6 h-full flex flex-col">
      <div className="mb-6 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Components</h2>
          <p className="text-muted-foreground">
            {total} components discovered in this project.
          </p>
        </div>
      </div>

      <div className="flex flex-col sm:flex-row gap-4 mb-4">
        <div className="relative flex-1">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search packages..."
            className="pl-9"
            value={searchTerm}
            onChange={(e) => { setSearchTerm(e.target.value); setPage(1); }}
          />
        </div>
        <div className="flex gap-2">
          <Select 
            value={riskFilter} 
            onChange={(e) => { setRiskFilter(e.target.value); setPage(1); }}
            className="w-[140px]"
          >
            <option value="all">All Risks</option>
            <option value="critical">Critical Risk</option>
            <option value="high">High Risk</option>
            <option value="medium">Medium Risk</option>
            <option value="low">Low Risk</option>
            <option value="none">No Risk</option>
          </Select>
          <Select 
            value={ecosystemFilter} 
            onChange={(e) => { setEcosystemFilter(e.target.value); setPage(1); }}
            className="w-[140px]"
          >
            <option value="all">All Ecosystems</option>
            <option value="npm">npm</option>
            <option value="pypi">PyPI</option>
            <option value="maven">Maven</option>
          </Select>
        </div>
      </div>

      <div className="rounded-md border flex-1 overflow-hidden flex flex-col bg-card">
        <div className="flex-1 overflow-auto">
          <Table>
            <TableHeader className="sticky top-0 bg-card z-10 shadow-sm">
              <TableRow>
                <TableHead>Component</TableHead>
                <TableHead>Version</TableHead>
                <TableHead>Ecosystem</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Risk</TableHead>
                <TableHead>Confidence</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading ? (
                Array.from({ length: 10 }).map((_, i) => (
                  <TableRow key={i}>
                    <TableCell><Skeleton className="h-4 w-48" /></TableCell>
                    <TableCell><Skeleton className="h-4 w-16" /></TableCell>
                    <TableCell><Skeleton className="h-6 w-16 rounded-full" /></TableCell>
                    <TableCell><Skeleton className="h-4 w-20" /></TableCell>
                    <TableCell><Skeleton className="h-6 w-24 rounded-full" /></TableCell>
                    <TableCell><Skeleton className="h-6 w-24 rounded-full" /></TableCell>
                  </TableRow>
                ))
              ) : components.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} className="h-24 text-center text-muted-foreground">
                    No components found matching your filters.
                  </TableCell>
                </TableRow>
              ) : (
                components.map((component) => (
                  <TableRow 
                    key={component.id} 
                    className="cursor-pointer hover:bg-muted/50"
                    onClick={() => setSelectedComponent(component)}
                  >
                    <TableCell className="font-mono text-sm font-medium">
                      {component.name}
                    </TableCell>
                    <TableCell className="font-mono text-sm text-muted-foreground">
                      {component.version || 'unknown'}
                    </TableCell>
                    <TableCell>
                      <EcosystemBadge ecosystem={component.ecosystem} />
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline" className="capitalize">
                        {component.dependency_type}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <RiskBadge level={component.risk_level} score={component.risk_score} />
                    </TableCell>
                    <TableCell>
                      <ConfidenceBadge confidence={component.version_confidence} />
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </div>
      </div>

      <ComponentDetail 
        scanId={params.id}
        componentId={selectedComponent?.id || null} 
        open={!!selectedComponent} 
        onOpenChange={(open) => !open && setSelectedComponent(null)} 
      />
    </div>
  );
}
