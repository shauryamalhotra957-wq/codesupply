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
  const [showAllAdded, setShowAllAdded] = useState(false);
  const [showAllChanged, setShowAllChanged] = useState(false);
  const [showAllRemoved, setShowAllRemoved] = useState(false);
  const [availableScans, setAvailableScans] = useState<any[]>([]);
  const [selectedBase, setSelectedBase] = useState<string>("");
  const [selectedCompare, setSelectedCompare] = useState<string>("");

  useEffect(() => {
    if (!baseId || !compareId) {
      setLoading(true);
      api.listScans()
        .then((res) => {
          const items = res.items || [];
          setAvailableScans(items);
          if (items.length >= 2) {
            setSelectedBase(items[1].id);
            setSelectedCompare(items[0].id);
          } else if (items.length === 1) {
            setSelectedBase(items[0].id);
            setSelectedCompare(items[0].id);
          }
        })
        .catch((e) => setError(e.message))
        .finally(() => setLoading(false));
      return;
    }

    api.getScanDiff(baseId, compareId)
      .then(setDiff)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  }, [baseId, compareId]);

  const handleStartComparison = () => {
    if (selectedBase && selectedCompare) {
      router.push(`/scans/compare?base=${selectedBase}&compare=${selectedCompare}`);
    }
  };

  const components = diff?.components || { added: [], version_changed: [], removed: [] };
  const vulnerabilities = diff?.vulnerabilities || { added: [], resolved: [] };
  const displayedAdded = showAllAdded ? components.added : components.added.slice(0, 10);
  const displayedChanged = showAllChanged ? components.version_changed : components.version_changed.slice(0, 10);
  const displayedRemoved = showAllRemoved ? components.removed : components.removed.slice(0, 10);

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={() => router.push("/scans")}>
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

      {loading ? (
        <div className="p-12 text-center text-muted-foreground">Loading comparison...</div>
      ) : error && (baseId || compareId) ? (
        <div className="p-12 text-center text-destructive">{error}</div>
      ) : !baseId || !compareId ? (
        <Card className="border-border/50">
          <CardHeader>
            <CardTitle className="text-base">Choose Scans to Compare</CardTitle>
            <CardDescription>
              Select a baseline scan (e.g. prior release) and a target scan (e.g. latest release).
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {availableScans.length < 2 ? (
              <div className="py-6 text-center text-muted-foreground text-sm space-y-2">
                <p>At least two scans are required to compute a version drift diff.</p>
                <Button onClick={() => router.push("/")} variant="outline" size="sm">
                  Run New Scan
                </Button>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div className="space-y-1.5">
                    <label className="text-xs font-semibold text-muted-foreground uppercase">Baseline Scan (Older)</label>
                    <select
                      value={selectedBase}
                      onChange={(e) => setSelectedBase(e.target.value)}
                      className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                    >
                      {availableScans.map((s) => (
                        <option key={s.id} value={s.id}>
                          {s.project_name || s.filename} ({s.id.slice(0, 8)}) - {new Date(s.created_at).toLocaleDateString()}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div className="space-y-1.5">
                    <label className="text-xs font-semibold text-muted-foreground uppercase">Target Scan (Newer)</label>
                    <select
                      value={selectedCompare}
                      onChange={(e) => setSelectedCompare(e.target.value)}
                      className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                    >
                      {availableScans.map((s) => (
                        <option key={s.id} value={s.id}>
                          {s.project_name || s.filename} ({s.id.slice(0, 8)}) - {new Date(s.created_at).toLocaleDateString()}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                <div className="flex justify-end pt-2">
                  <Button
                    onClick={handleStartComparison}
                    disabled={!selectedBase || !selectedCompare || selectedBase === selectedCompare}
                    className="gap-2 bg-purple-600 hover:bg-purple-700 text-white"
                  >
                    <GitCompare className="h-4 w-4" /> Compare Scans
                  </Button>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      ) : !diff ? null : (
        <>
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
                  {displayedAdded.map((c: any, i: number) => (
                    <div key={i} className="text-sm p-2 bg-green-500/10 rounded border border-green-500/20">
                      <span className="font-mono">{c.ecosystem}:{c.name}</span> <Badge variant="outline" className="ml-2">{c.version}</Badge>
                    </div>
                  ))}
                  {components.added.length > 10 && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setShowAllAdded(!showAllAdded)}
                      className="text-xs text-muted-foreground hover:text-foreground mt-1 h-7 px-2"
                    >
                      {showAllAdded ? "Show less" : `+ ${components.added.length - 10} more (Show all)`}
                    </Button>
                  )}
                </div>
              </div>
            )}
            
            {components.version_changed.length > 0 && (
              <div>
                <h3 className="text-sm font-semibold text-blue-600 mb-2 flex items-center">
                  <ArrowRight className="h-4 w-4 mr-1" /> Version Changed ({components.version_changed.length})
                </h3>
                <div className="space-y-1">
                  {displayedChanged.map((c: any, i: number) => (
                    <div key={i} className="text-sm p-2 bg-blue-500/10 rounded border border-blue-500/20 flex items-center gap-2">
                      <span className="font-mono">{c.ecosystem}:{c.name}</span>
                      <Badge variant="outline">{c.old_version}</Badge>
                      <ArrowRight className="h-3 w-3" />
                      <Badge variant="default">{c.new_version}</Badge>
                    </div>
                  ))}
                  {components.version_changed.length > 10 && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setShowAllChanged(!showAllChanged)}
                      className="text-xs text-muted-foreground hover:text-foreground mt-1 h-7 px-2"
                    >
                      {showAllChanged ? "Show less" : `+ ${components.version_changed.length - 10} more (Show all)`}
                    </Button>
                  )}
                </div>
              </div>
            )}

            {components.removed.length > 0 && (
              <div>
                <h3 className="text-sm font-semibold text-red-600 mb-2 flex items-center">
                  <Minus className="h-4 w-4 mr-1" /> Removed ({components.removed.length})
                </h3>
                <div className="space-y-1">
                  {displayedRemoved.map((c: any, i: number) => (
                    <div key={i} className="text-sm p-2 bg-red-500/10 rounded border border-red-500/20">
                      <span className="font-mono">{c.ecosystem}:{c.name}</span> <Badge variant="outline" className="ml-2 text-muted-foreground line-through">{c.version}</Badge>
                    </div>
                  ))}
                  {components.removed.length > 10 && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setShowAllRemoved(!showAllRemoved)}
                      className="text-xs text-muted-foreground hover:text-foreground mt-1 h-7 px-2"
                    >
                      {showAllRemoved ? "Show less" : `+ ${components.removed.length - 10} more (Show all)`}
                    </Button>
                  )}
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
    </>
  )}
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
