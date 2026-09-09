"use client";

import { useEffect, useState, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ArrowLeft, Plus, Minus, ArrowRight, ShieldAlert, Package, GitCompare } from "lucide-react";
import { Badge } from "@/components/ui/badge";

function ComparePageContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const baseId = searchParams.get("base");
  const compareId = searchParams.get("compare");

  const [diff, setDiff] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!baseId || !compareId) {
      setError("Missing scan IDs for comparison.");
      setLoading(false);
      return;
    }

    api.getScanDiff(baseId, compareId)
      .then(setDiff)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  }, [baseId, compareId]);

  if (loading) return <div className="p-12 text-center">Loading comparison...</div>;
  if (error) return <div className="p-12 text-center text-destructive">{error}</div>;
  if (!diff) return null;

  const { components, vulnerabilities } = diff;

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={() => router.back()}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <GitCompare className="h-6 w-6" /> Scan Comparison
          </h1>
          <p className="text-muted-foreground text-sm">
            Diffing changes between two scan baselines.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <Package className="h-5 w-5 text-primary" /> Dependency Drift
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {components.added.length > 0 && (
              <div>
                <h3 className="text-sm font-semibold text-green-600 mb-2 flex items-center">
                  <Plus className="h-4 w-4 mr-1" /> Added ({components.added.length})
                </h3>
                <div className="space-y-1">
                  {components.added.slice(0, 10).map((c: any, i: number) => (
                    <div key={i} className="text-sm p-2 bg-green-500/10 rounded border border-green-500/20">
                      <span className="font-mono">{c.ecosystem}:{c.name}</span> <Badge variant="outline" className="ml-2">{c.version}</Badge>
                    </div>
                  ))}
                  {components.added.length > 10 && <div className="text-xs text-muted-foreground">+ {components.added.length - 10} more</div>}
                </div>
              </div>
            )}
            
            {components.version_changed.length > 0 && (
              <div>
                <h3 className="text-sm font-semibold text-blue-600 mb-2 flex items-center">
                  <ArrowRight className="h-4 w-4 mr-1" /> Version Changed ({components.version_changed.length})
                </h3>
                <div className="space-y-1">
                  {components.version_changed.slice(0, 10).map((c: any, i: number) => (
                    <div key={i} className="text-sm p-2 bg-blue-500/10 rounded border border-blue-500/20 flex items-center gap-2">
                      <span className="font-mono">{c.ecosystem}:{c.name}</span>
                      <Badge variant="outline">{c.old_version}</Badge>
                      <ArrowRight className="h-3 w-3" />
                      <Badge variant="default">{c.new_version}</Badge>
                    </div>
                  ))}
                  {components.version_changed.length > 10 && <div className="text-xs text-muted-foreground">+ {components.version_changed.length - 10} more</div>}
                </div>
              </div>
            )}

            {components.removed.length > 0 && (
              <div>
                <h3 className="text-sm font-semibold text-red-600 mb-2 flex items-center">
                  <Minus className="h-4 w-4 mr-1" /> Removed ({components.removed.length})
                </h3>
                <div className="space-y-1">
                  {components.removed.slice(0, 10).map((c: any, i: number) => (
                    <div key={i} className="text-sm p-2 bg-red-500/10 rounded border border-red-500/20">
                      <span className="font-mono">{c.ecosystem}:{c.name}</span> <Badge variant="outline" className="ml-2 text-muted-foreground line-through">{c.version}</Badge>
                    </div>
                  ))}
                  {components.removed.length > 10 && <div className="text-xs text-muted-foreground">+ {components.removed.length - 10} more</div>}
                </div>
              </div>
            )}

            {components.added.length === 0 && components.version_changed.length === 0 && components.removed.length === 0 && (
              <div className="text-center py-6 text-muted-foreground text-sm">No dependency changes.</div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <ShieldAlert className="h-5 w-5 text-destructive" /> Vulnerability Changes
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {vulnerabilities.added.length > 0 && (
              <div>
                <h3 className="text-sm font-semibold text-red-600 mb-2 flex items-center">
                  <Plus className="h-4 w-4 mr-1" /> New Vulnerabilities ({vulnerabilities.added.length})
                </h3>
                <div className="space-y-2">
                  {vulnerabilities.added.map((v: any, i: number) => (
                    <div key={i} className="text-sm p-3 bg-red-500/10 rounded border border-red-500/20">
                      <div className="flex items-center gap-2 font-semibold mb-1">
                        <span className="text-destructive">{v.vuln_id}</span>
                        <Badge variant="destructive" className="uppercase text-[10px] h-4">{v.severity}</Badge>
                      </div>
                      <p className="text-xs text-muted-foreground line-clamp-2">{v.summary}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {vulnerabilities.resolved.length > 0 && (
              <div>
                <h3 className="text-sm font-semibold text-green-600 mb-2 flex items-center">
                  <Minus className="h-4 w-4 mr-1" /> Resolved Vulnerabilities ({vulnerabilities.resolved.length})
                </h3>
                <div className="space-y-2">
                  {vulnerabilities.resolved.map((v: any, i: number) => (
                    <div key={i} className="text-sm p-3 bg-green-500/10 rounded border border-green-500/20">
                      <div className="flex items-center gap-2 font-semibold mb-1">
                        <span className="text-green-700 line-through">{v.vuln_id}</span>
                        <Badge variant="outline" className="uppercase text-[10px] h-4">{v.severity}</Badge>
                      </div>
                      <p className="text-xs text-muted-foreground line-clamp-2">{v.summary}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {vulnerabilities.added.length === 0 && vulnerabilities.resolved.length === 0 && (
              <div className="text-center py-6 text-muted-foreground text-sm">No vulnerability changes.</div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}


export default function ComparePage() {
  return (
    <Suspense fallback={<div className="p-12 text-center text-muted-foreground">Loading comparison...</div>}>
      <ComparePageContent />
    </Suspense>
  );
}
