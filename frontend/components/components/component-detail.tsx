import { useState, useEffect } from 'react';
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetDescription } from '@/components/ui/sheet';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Component, ComponentExplanation } from '@/types';
import { api } from '@/lib/api';
import { Skeleton } from '@/components/ui/skeleton';
import { RiskBadge } from '@/components/shared/risk-badge';
import { EcosystemBadge } from '@/components/shared/ecosystem-badge';
import { ConfidenceBadge } from '@/components/shared/confidence-badge';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Copy, ExternalLink, ShieldAlert, Sparkles, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface ComponentDetailProps {
  scanId: string;
  componentId: string | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function ComponentDetail({ scanId, componentId, open, onOpenChange }: ComponentDetailProps) {
  const [component, setComponent] = useState<Component | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [explanation, setExplanation] = useState<ComponentExplanation | null>(null);
  const [isExplaining, setIsExplaining] = useState(false);

  useEffect(() => {
    if (open && componentId) {
      setIsLoading(true);
      setExplanation(null);
      api.getComponent(scanId, componentId)
        .then(setComponent)
        .catch(console.error)
        .finally(() => setIsLoading(false));
    } else {
      setComponent(null);
      setExplanation(null);
    }
  }, [scanId, componentId, open]);

  const handleExplain = async () => {
    if (!component) return;
    setIsExplaining(true);
    try {
      const res = await api.explainComponent(scanId, component.id);
      setExplanation(res);
    } catch (err) {
      console.error(err);
    } finally {
      setIsExplaining(false);
    }
  };

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent onClose={() => onOpenChange(false)} className="sm:max-w-xl w-full flex flex-col p-0">
        {isLoading || !component ? (
          <div className="p-6 space-y-4">
            <Skeleton className="h-8 w-3/4" />
            <Skeleton className="h-4 w-1/2" />
            <div className="flex gap-2 pt-4">
              <Skeleton className="h-6 w-20 rounded-full" />
              <Skeleton className="h-6 w-20 rounded-full" />
              <Skeleton className="h-6 w-24 rounded-full" />
            </div>
            <Skeleton className="h-64 w-full mt-8" />
          </div>
        ) : (
          <>
            <div className="p-6 pb-4 border-b">
              <div className="flex items-start justify-between">
                <div>
                  <h2 className="text-xl font-bold font-mono break-all">{component.name}</h2>
                  <div className="text-muted-foreground font-mono mt-1">
                    {component.version || 'Version unknown'}
                  </div>
                </div>
              </div>
              <div className="flex flex-wrap gap-2 mt-4">
                <EcosystemBadge ecosystem={component.ecosystem} />
                <Badge variant="outline" className="capitalize">
                  {component.dependency_type}
                </Badge>
                <RiskBadge level={component.risk_level} score={component.risk_score} />
                <ConfidenceBadge confidence={component.version_confidence} />
              </div>
            </div>

            <Tabs defaultValue="overview" className="flex-1 flex flex-col min-h-0">
              <div className="px-6 pt-2 border-b">
                <TabsList className="bg-transparent h-12 p-0 space-x-6 border-b-0 w-full justify-start">
                  <TabsTrigger value="overview" className="rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-transparent data-[state=active]:shadow-none px-0 py-3">
                    Overview
                  </TabsTrigger>
                  <TabsTrigger value="vulnerabilities" className="rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-transparent data-[state=active]:shadow-none px-0 py-3">
                    Vulnerabilities
                    {component.vulnerabilities?.length > 0 && (
                      <Badge variant="destructive" className="ml-2 h-5 px-1.5 min-w-5 flex items-center justify-center rounded-full text-[10px]">
                        {component.vulnerabilities.length}
                      </Badge>
                    )}
                  </TabsTrigger>
                  <TabsTrigger value="evidence" className="rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-transparent data-[state=active]:shadow-none px-0 py-3">
                    Evidence
                  </TabsTrigger>
                </TabsList>
              </div>

              <ScrollArea className="flex-1">
                <div className="p-6">
                  <TabsContent value="overview" className="m-0 space-y-6">
                    <section className="space-y-3">
                      <h3 className="text-sm font-medium text-muted-foreground uppercase tracking-wider">Identifiers</h3>
                      <div className="bg-muted/50 rounded-md p-3 flex justify-between items-center group">
                        <span className="font-mono text-sm truncate pr-4 text-foreground/80">{component.purl || 'N/A'}</span>
                        {component.purl && (
                          <Button variant="ghost" size="icon" className="h-8 w-8 opacity-0 group-hover:opacity-100 transition-opacity" onClick={() => navigator.clipboard.writeText(component.purl!)}>
                            <Copy className="h-4 w-4" />
                          </Button>
                        )}
                      </div>
                    </section>
                    
                    <section className="space-y-3">
                      <h3 className="text-sm font-medium text-muted-foreground uppercase tracking-wider">Source Information</h3>
                      <div className="grid grid-cols-3 gap-y-2 text-sm">
                        <div className="text-muted-foreground">Source File</div>
                        <div className="col-span-2 font-mono break-all">{component.source_file}</div>
                        <div className="text-muted-foreground">Location</div>
                        <div className="col-span-2 font-mono">{component.source_location || 'N/A'}</div>
                        <div className="text-muted-foreground">Declaration</div>
                        <div className="col-span-2 font-mono whitespace-pre-wrap bg-muted/30 p-2 rounded-md mt-1">{component.original_declaration || 'N/A'}</div>
                      </div>
                    </section>

                    {component.risk_reasons && component.risk_reasons.length > 0 && (
                      <section className="space-y-3">
                        <h3 className="text-sm font-medium text-muted-foreground uppercase tracking-wider">Risk Factors</h3>
                        <ul className="space-y-2">
                          {component.risk_reasons.map((r, i) => (
                            <li key={i} className="flex gap-2 text-sm items-start p-3 bg-muted/30 rounded-md border border-border/50">
                              <ShieldAlert className="h-4 w-4 mt-0.5 text-muted-foreground shrink-0" />
                              <div>
                                <div className="font-medium">{r.reason_type.replace(/_/g, ' ')}</div>
                                <div className="text-muted-foreground text-xs mt-1">{r.description}</div>
                              </div>
                            </li>
                          ))}
                        </ul>
                      </section>
                    )}

                    <section className="space-y-3 pt-2">
                      <div className="flex items-center justify-between">
                        <h3 className="text-sm font-medium text-muted-foreground uppercase tracking-wider">AI Security Intelligence</h3>
                        {!explanation && (
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={handleExplain}
                            disabled={isExplaining}
                            className="h-8 gap-1.5 text-xs bg-purple-500/10 hover:bg-purple-500/20 text-purple-400 border-purple-500/30"
                          >
                            {isExplaining ? (
                              <>
                                <Loader2 className="h-3.5 w-3.5 animate-spin" /> Analyzing...
                              </>
                            ) : (
                              <>
                                <Sparkles className="h-3.5 w-3.5" /> Explain this component
                              </>
                            )}
                          </Button>
                        )}
                      </div>

                      {explanation && (
                        <div className="rounded-xl border border-purple-500/30 bg-purple-950/20 p-4 space-y-3 text-sm">
                          <div className="flex items-center justify-between">
                            <Badge className="bg-purple-500/20 text-purple-300 border-purple-500/30 text-[10px] font-medium flex items-center gap-1">
                              <Sparkles className="h-3 w-3" /> {explanation.label}
                            </Badge>
                            <Button
                              size="sm"
                              variant="ghost"
                              onClick={handleExplain}
                              disabled={isExplaining}
                              className="h-6 px-2 text-[11px] text-muted-foreground hover:text-foreground"
                            >
                              Refresh
                            </Button>
                          </div>

                          <div>
                            <h4 className="font-semibold text-xs uppercase tracking-wider text-muted-foreground">Summary</h4>
                            <p className="mt-1 text-sm text-foreground leading-relaxed">{explanation.summary}</p>
                          </div>

                          <div>
                            <h4 className="font-semibold text-xs uppercase tracking-wider text-muted-foreground">Why It Matters</h4>
                            <p className="mt-1 text-sm text-muted-foreground leading-relaxed">{explanation.why_it_matters}</p>
                          </div>

                          <div>
                            <h4 className="font-semibold text-xs uppercase tracking-wider text-muted-foreground">Recommended Action</h4>
                            <p className="mt-1 text-sm text-foreground/90 font-mono bg-muted/40 p-2.5 rounded-lg border border-border/40 text-xs">
                              {explanation.what_to_do}
                            </p>
                          </div>

                          <p className="text-[11px] text-muted-foreground/70 italic pt-1 border-t border-border/30">
                            * {explanation.disclaimer}
                          </p>
                        </div>
                      )}
                    </section>
                  </TabsContent>

                  <TabsContent value="vulnerabilities" className="m-0">
                    {(!component.vulnerabilities || component.vulnerabilities.length === 0) ? (
                      <div className="text-center py-12 text-muted-foreground">
                        <ShieldAlert className="h-8 w-8 mx-auto mb-3 opacity-20" />
                        <p>No known vulnerabilities found</p>
                      </div>
                    ) : (
                      <div className="space-y-4">
                        {component.vulnerabilities.map(v => (
                          <div key={v.id} className="border rounded-lg p-4 space-y-3 shadow-sm relative overflow-hidden">
                            <div className="absolute top-0 left-0 w-1 h-full bg-destructive"></div>
                            <div className="flex justify-between items-start">
                              <Badge variant="destructive">{v.severity || 'UNKNOWN'}</Badge>
                              <a href={`https://nvd.nist.gov/vuln/detail/${v.vuln_id}`} target="_blank" rel="noreferrer" className="flex items-center text-xs text-primary hover:underline">
                                {v.vuln_id} <ExternalLink className="ml-1 h-3 w-3" />
                              </a>
                            </div>
                            <p className="text-sm text-foreground/90 font-medium">{v.summary}</p>
                            <div className="text-xs text-muted-foreground flex gap-4">
                              {v.fixed_version && <span>Fixed in: <span className="font-mono text-foreground">{v.fixed_version}</span></span>}
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </TabsContent>

                  <TabsContent value="evidence" className="m-0 space-y-4">
                    {(!component.evidence || component.evidence.length === 0) ? (
                      <div className="text-center py-12 text-muted-foreground">
                        <p>No evidence records available</p>
                      </div>
                    ) : (
                      component.evidence.map(e => (
                        <div key={e.id} className="border rounded-md p-3 text-sm space-y-2 bg-muted/10">
                          <div className="flex justify-between items-center">
                            <Badge variant="outline" className="text-[10px] uppercase tracking-wider">{e.evidence_type}</Badge>
                            <span className="text-xs text-muted-foreground">{e.confidence} confidence</span>
                          </div>
                          <div className="grid grid-cols-[80px_1fr] gap-1 text-xs">
                            <div className="text-muted-foreground">Method</div>
                            <div>{e.method}</div>
                            <div className="text-muted-foreground">Value</div>
                            <div className="font-mono break-all">{e.value}</div>
                            <div className="text-muted-foreground mt-2">Source</div>
                            <div className="mt-2 font-mono break-all">{e.source_file}{e.source_location ? `:${e.source_location}` : ''}</div>
                          </div>
                        </div>
                      ))
                    )}
                  </TabsContent>
                </div>
              </ScrollArea>
            </Tabs>
          </>
        )}
      </SheetContent>
    </Sheet>
  );
}
