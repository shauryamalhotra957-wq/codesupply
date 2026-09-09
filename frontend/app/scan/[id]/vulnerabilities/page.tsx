"use client";

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { Vulnerability } from '@/types';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { EmptyState } from '@/components/shared/empty-state';
import { ShieldCheck, ExternalLink } from 'lucide-react';
import { VulnerabilityDetail } from '@/components/vulnerabilities/vulnerability-detail';

export default function VulnerabilitiesPage({ params }: { params: { id: string } }) {
  const [vulnerabilities, setVulnerabilities] = useState<Vulnerability[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedVuln, setSelectedVuln] = useState<Vulnerability | null>(null);

  useEffect(() => {
    setIsLoading(true);
    api.getVulnerabilities(params.id)
      .then(res => setVulnerabilities(res.items))
      .catch(console.error)
      .finally(() => setIsLoading(false));
  }, [params.id]);

  const getSeverityColor = (severity: string) => {
    switch(severity.toLowerCase()) {
      case 'critical': return 'destructive';
      case 'high': return 'destructive';
      case 'medium': return 'default'; // mapping to amber in proper implementation
      case 'low': return 'secondary';
      default: return 'outline';
    }
  };

  return (
    <div className="p-6 h-full flex flex-col">
      <div className="mb-6">
        <h2 className="text-2xl font-bold tracking-tight">Vulnerabilities</h2>
        <p className="text-muted-foreground">
          {vulnerabilities.length} known vulnerabilities found in this project.
        </p>
      </div>

      <div className="rounded-md border flex-1 overflow-hidden flex flex-col bg-card">
        <div className="flex-1 overflow-auto">
          {isLoading ? (
            <div className="p-6 space-y-4">
              {[...Array(5)].map((_, i) => <Skeleton key={i} className="h-16 w-full" />)}
            </div>
          ) : vulnerabilities.length === 0 ? (
            <div className="h-full flex items-center justify-center">
              <EmptyState 
                icon={ShieldCheck}
                title="No vulnerabilities found"
                description="No known vulnerabilities found in the queried advisory source for this scan."
              />
            </div>
          ) : (
            <Table>
              <TableHeader className="sticky top-0 bg-card z-10 shadow-sm">
                <TableRow>
                  <TableHead>ID</TableHead>
                  <TableHead>Severity</TableHead>
                  <TableHead>Component</TableHead>
                  <TableHead>Summary</TableHead>
                  <TableHead>Fixed In</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {vulnerabilities.map(vuln => (
                  <TableRow key={vuln.id} className="cursor-pointer hover:bg-muted/50" onClick={() => setSelectedVuln(vuln)}>
                    <TableCell className="font-mono text-xs text-primary">
                      {vuln.vuln_id}
                    </TableCell>
                    <TableCell>
                      <Badge variant={getSeverityColor(vuln.severity) as any}>
                        {vuln.severity}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <div className="font-mono text-sm">{vuln.component_name}</div>
                      <div className="text-xs text-muted-foreground font-mono">{vuln.component_version}</div>
                    </TableCell>
                    <TableCell className="max-w-md truncate" title={vuln.summary}>
                      {vuln.summary}
                    </TableCell>
                    <TableCell className="font-mono text-sm">
                      {vuln.fixed_version || '-'}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </div>
      </div>

      <VulnerabilityDetail 
        vulnerability={selectedVuln} 
        open={!!selectedVuln} 
        onOpenChange={(open) => !open && setSelectedVuln(null)} 
      />
    </div>
  );
}
