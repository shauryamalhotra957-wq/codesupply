"use client";

import { useState, useEffect, useMemo } from 'react';
import { api } from '@/lib/api';
import { Vulnerability } from '@/types';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { EmptyState } from '@/components/shared/empty-state';
import { ShieldCheck, Search } from 'lucide-react';
import { VulnerabilityDetail } from '@/components/vulnerabilities/vulnerability-detail';
import { Input } from '@/components/ui/input';
import { Select } from '@/components/ui/select';

export default function VulnerabilitiesPage({ params }: { params: { id: string } }) {
  const [vulnerabilities, setVulnerabilities] = useState<Vulnerability[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedVuln, setSelectedVuln] = useState<Vulnerability | null>(null);
  
  const [searchTerm, setSearchTerm] = useState("");
  const [severityFilter, setSeverityFilter] = useState("all");

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

  const filteredVulnerabilities = useMemo(() => {
    return vulnerabilities.filter(v => {
      const matchesSearch = v.vuln_id.toLowerCase().includes(searchTerm.toLowerCase()) || 
                            (v.component_name || "").toLowerCase().includes(searchTerm.toLowerCase());
      const matchesSeverity = severityFilter === 'all' || v.severity.toLowerCase() === severityFilter.toLowerCase();
      return matchesSearch && matchesSeverity;
    });
  }, [vulnerabilities, searchTerm, severityFilter]);

  return (
    <div className="p-6 h-full flex flex-col">
      <div className="mb-6 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Vulnerabilities</h2>
          <p className="text-muted-foreground">
            {vulnerabilities.length} known vulnerabilities found in this project.
          </p>
        </div>
      </div>

      <div className="flex flex-col sm:flex-row gap-4 mb-4">
        <div className="relative flex-1">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search by ID or component..."
            className="pl-9"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
        <div className="flex gap-2">
          <Select 
            value={severityFilter} 
            onChange={(e) => setSeverityFilter(e.target.value)}
            className="w-[140px]"
          >
            <option value="all">All Severities</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </Select>
        </div>
      </div>

      <div className="rounded-md border flex-1 overflow-hidden flex flex-col bg-card">
        <div className="flex-1 overflow-auto">
          {isLoading ? (
            <div className="p-6 space-y-4">
              {[...Array(5)].map((_, i) => <Skeleton key={i} className="h-16 w-full" />)}
            </div>
          ) : filteredVulnerabilities.length === 0 ? (
            <div className="h-full flex items-center justify-center">
              <EmptyState 
                icon={ShieldCheck}
                title="No vulnerabilities found"
                description={vulnerabilities.length > 0 ? "No vulnerabilities match your filters." : "No known vulnerabilities found in the queried advisory source for this scan."}
              />
            </div>
          ) : (
            <Table>
              <TableHeader className="sticky top-0 bg-card z-10 shadow-sm">
                <TableRow>
                  <TableHead>ID</TableHead>
                  <TableHead>Severity</TableHead>
                  <TableHead>CVSS</TableHead>
                  <TableHead>Component</TableHead>
                  <TableHead>Summary</TableHead>
                  <TableHead>Fixed In</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredVulnerabilities.map(vuln => (
                  <TableRow key={vuln.id} className="cursor-pointer hover:bg-muted/50" onClick={() => setSelectedVuln(vuln)}>
                    <TableCell className="font-mono text-xs text-primary font-semibold">
                      {vuln.vuln_id}
                    </TableCell>
                    <TableCell>
                      <Badge variant={getSeverityColor(vuln.severity) as any}>
                        {vuln.severity}
                      </Badge>
                    </TableCell>
                    <TableCell className="font-mono text-xs">
                      {vuln.cvss_score ? (
                        <span className={`font-bold px-1.5 py-0.5 rounded ${
                          vuln.cvss_score >= 9.0 ? 'bg-red-500/10 text-red-500' :
                          vuln.cvss_score >= 7.0 ? 'bg-orange-500/10 text-orange-500' :
                          vuln.cvss_score >= 4.0 ? 'bg-amber-500/10 text-amber-500' :
                          'bg-blue-500/10 text-blue-500'
                        }`}>
                          {vuln.cvss_score.toFixed(1)}
                        </span>
                      ) : (
                        <span className="text-muted-foreground text-xs font-mono">-</span>
                      )}
                    </TableCell>
                    <TableCell>
                      <div className="font-mono text-sm">{vuln.component_name}</div>
                      <div className="text-xs text-muted-foreground font-mono">{vuln.component_version}</div>
                    </TableCell>
                    <TableCell className="max-w-md truncate text-xs" title={vuln.summary}>
                      {vuln.summary}
                    </TableCell>
                    <TableCell className="font-mono text-xs">
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
