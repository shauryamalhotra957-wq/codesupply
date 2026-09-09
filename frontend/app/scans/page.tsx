"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { Scan } from "@/types";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { StatusBadge } from "@/components/shared/status-badge";
import { Skeleton } from "@/components/ui/skeleton";
import { ErrorState } from "@/components/shared/error-state";
import { Package, ShieldAlert, ArrowUpRight, Plus, RefreshCw, Layers, GitCompare } from "lucide-react";


export default function ScansPage() {
  const router = useRouter();
  const [scans, setScans] = useState<Scan[]>([]);
  const [total, setTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [selectedScans, setSelectedScans] = useState<string[]>([]);
  
  const toggleScanSelection = (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    setSelectedScans(prev => 
      prev.includes(id) ? prev.filter(s => s !== id) : [...prev, id].slice(-2)
    );
  };


  const fetchScans = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await api.listScans({ limit: 50 });
      setScans(data.items);
      setTotal(data.total);
    } catch (err: any) {
      setError(err.message || "Failed to load scan history");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchScans();
  }, []);

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Scan History</h1>
          <p className="text-sm text-muted-foreground">
            All software supply-chain scans and their verification results.
          </p>
        </div>
        <div className="flex items-center gap-2">
          
          {selectedScans.length === 2 && (
            <Button size="sm" variant="secondary" asChild className="mr-2 border-primary/20 bg-primary/10 hover:bg-primary/20 text-primary">
              <Link href={`/scans/compare?base=${selectedScans[1]}&compare=${selectedScans[0]}`}>
                <GitCompare className="h-4 w-4 mr-1.5" />
                Compare Scans
              </Link>
            </Button>
          )}

          <Button variant="outline" size="sm" onClick={fetchScans} disabled={isLoading}>
            <RefreshCw className={`h-4 w-4 mr-1.5 ${isLoading ? "animate-spin" : ""}`} />
            Refresh
          </Button>
          <Button size="sm" asChild>
            <Link href="/">
              <Plus className="h-4 w-4 mr-1.5" />
              New Scan
            </Link>
          </Button>
        </div>
      </div>

      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base font-medium flex items-center gap-2">
            <Layers className="h-4 w-4 text-primary" />
            Total Scans ({total})
          </CardTitle>
          <CardDescription>
            Click on any scan to inspect components, vulnerability findings, dependency graph, and SBOM.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-3">
              {[...Array(5)].map((_, i) => (
                <Skeleton key={i} className="h-12 w-full rounded-md" />
              ))}
            </div>
          ) : error ? (
            <ErrorState title="Could not load scans" description={error} onRetry={fetchScans} />
          ) : scans.length === 0 ? (
            <div className="text-center py-12 space-y-4">
              <Package className="h-12 w-12 text-muted-foreground mx-auto opacity-50" />
              <div className="space-y-1">
                <h3 className="font-semibold text-lg">No scans yet</h3>
                <p className="text-sm text-muted-foreground max-w-sm mx-auto">
                  Upload an archive or run the demo project scan to generate your first supply-chain report.
                </p>
              </div>
              <Button asChild>
                <Link href="/">Upload Archive</Link>
              </Button>
            </div>
          ) : (
            <div className="rounded-md border overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-[40px]"></TableHead>
                    <TableHead>Project / Archive</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead className="text-right">Components</TableHead>
                    <TableHead className="text-right">Vulnerabilities</TableHead>
                    <TableHead className="text-right">Manifests</TableHead>
                    <TableHead>Created</TableHead>
                    <TableHead className="text-right">Action</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {scans.map((scan) => (
                    <TableRow
                      key={scan.id}
                      className="cursor-pointer hover:bg-muted/50"
                      onClick={() => router.push(`/scan/${scan.id}`)}
                    >
                      
                      <TableCell onClick={(e) => e.stopPropagation()}>
                        <input type="checkbox" className="h-4 w-4 rounded border-gray-300" checked={selectedScans.includes(scan.id)} onChange={(e) => toggleScanSelection(e as any, scan.id)} disabled={!selectedScans.includes(scan.id) && selectedScans.length >= 2} />
                      </TableCell>

                      <TableCell className="font-medium">
                        <div className="flex items-center gap-2">
                          <Package className="h-4 w-4 text-muted-foreground flex-shrink-0" />
                          <div>
                            <span className="font-semibold text-foreground">
                              {scan.project_name || scan.filename}
                            </span>
                            <span className="block text-xs text-muted-foreground">
                              ID: {scan.id.substring(0, 12)}...
                            </span>
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <StatusBadge status={scan.status} />
                      </TableCell>
                      <TableCell className="text-right font-mono">
                        {scan.total_components}
                      </TableCell>
                      <TableCell className="text-right font-mono">
                        {scan.total_vulnerabilities > 0 ? (
                          <span className="text-destructive font-semibold inline-flex items-center gap-1 justify-end">
                            <ShieldAlert className="h-3.5 w-3.5" />
                            {scan.total_vulnerabilities}
                          </span>
                        ) : (
                          <span className="text-muted-foreground">0</span>
                        )}
                      </TableCell>
                      <TableCell className="text-right font-mono text-muted-foreground">
                        {scan.total_manifests}
                      </TableCell>
                      <TableCell className="text-xs text-muted-foreground">
                        {new Date(scan.created_at).toLocaleString()}
                      </TableCell>
                      <TableCell className="text-right">
                        <Button variant="ghost" size="sm" asChild>
                          <Link href={`/scan/${scan.id}`}>
                            View
                            <ArrowUpRight className="h-4 w-4 ml-1" />
                          </Link>
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
