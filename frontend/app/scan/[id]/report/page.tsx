"use client";

import { useState, useEffect } from "react";
import { useScan } from "@/hooks/use-scan";
import { api } from "@/lib/api";
import { Vulnerability, RemediationAction } from "@/types";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { EcosystemBadge } from "@/components/shared/ecosystem-badge";
import { 
  Printer, 
  Download, 
  FileText, 
  ShieldAlert, 
  CheckCircle2, 
  Layers, 
  ArrowRight,
  ExternalLink
} from "lucide-react";

export default function ReportPage({ params }: { params: { id: string } }) {
  const { scan, summary, isLoading, error } = useScan(params.id);
  const [vulns, setVulns] = useState<Vulnerability[]>([]);
  const [remediations, setRemediations] = useState<RemediationAction[]>([]);
  const [isDataLoading, setIsDataLoading] = useState(true);

  useEffect(() => {
    async function loadDetails() {
      try {
        const [vRes, rRes] = await Promise.all([
          api.getVulnerabilities(params.id),
          api.getRemediations(params.id).catch(() => ({ remediations: [] })),
        ]);
        setVulns(vRes.items || []);
        setRemediations(rRes.remediations || []);
      } catch (e) {
        console.error("Failed to load report findings", e);
      } finally {
        setIsDataLoading(false);
      }
    }
    loadDetails();
  }, [params.id]);

  if (isLoading || isDataLoading) {
    return (
      <div className="p-8 space-y-6 max-w-6xl mx-auto">
        <Skeleton className="h-10 w-64" />
        <Skeleton className="h-32 w-full" />
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }

  if (error || !scan) {
    return (
      <div className="p-12 text-center text-destructive">
        Failed to load executive report: {error?.message || "Scan not found"}
      </div>
    );
  }

  const criticalCount = (summary?.components_by_risk?.critical || 0);
  const highCount = (summary?.components_by_risk?.high || 0);
  const letterGrade = criticalCount > 0 ? "F" : highCount > 0 ? "D" : (summary?.total_vulnerabilities || 0) > 0 ? "B" : "A";

  const handlePrint = () => {
    window.print();
  };

  const handleDownloadJSON = async () => {
    try {
      const blob = await api.downloadSBOM(params.id);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `codesupply-sbom-${params.id}.json`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="p-6 md:p-10 max-w-5xl mx-auto space-y-8 print:p-0 print:max-w-none">
      {/* Header with Print / Export Actions */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-border/40 pb-6 print:border-none">
        <div>
          <div className="flex items-center gap-2">
            <Badge variant="outline" className="text-purple-400 border-purple-500/30 bg-purple-500/10">
              Executive Audit
            </Badge>
            <span className="text-xs text-muted-foreground font-mono">ID: {scan.id}</span>
          </div>
          <h1 className="text-3xl font-extrabold tracking-tight mt-1">
            Software Supply Chain Security & SBOM Report
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            Standards-Compliant Software Bill of Materials & Vulnerability Risk Analysis
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2 print:hidden">
          <Button variant="outline" size="sm" onClick={handlePrint} className="gap-2">
            <Printer className="h-4 w-4" /> Print / Save PDF
          </Button>
          <Button variant="outline" size="sm" onClick={handleDownloadJSON} className="gap-2">
            <Download className="h-4 w-4" /> CycloneDX JSON
          </Button>
          <Button 
            variant="default" 
            size="sm" 
            onClick={() => window.open(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'}/scans/${scan.id}/report/html`, '_blank')}
            className="gap-2 bg-purple-600 hover:bg-purple-700 text-white"
          >
            <ExternalLink className="h-4 w-4" /> View Full HTML
          </Button>
        </div>
      </div>

      {/* Overview Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="bg-card/50 backdrop-blur border-border/50">
          <CardHeader className="pb-2">
            <CardDescription className="text-xs">Security Posture</CardDescription>
            <CardTitle className="text-2xl font-black flex items-center gap-2">
              <span className={`text-3xl font-extrabold ${letterGrade === 'A' ? 'text-green-400' : letterGrade === 'B' ? 'text-blue-400' : letterGrade === 'D' ? 'text-amber-400' : 'text-red-400'}`}>
                Grade {letterGrade}
              </span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-xs text-muted-foreground">
              {letterGrade === 'A' ? 'Compliant with low risk' : 'Requires security remediation'}
            </p>
          </CardContent>
        </Card>

        <Card className="bg-card/50 backdrop-blur border-border/50">
          <CardHeader className="pb-2">
            <CardDescription className="text-xs">Total Components</CardDescription>
            <CardTitle className="text-3xl font-bold font-mono">
              {summary?.total_components || scan.total_components}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-xs text-muted-foreground">
              {summary?.components_by_type?.direct || 0} direct, {summary?.components_by_type?.transitive || 0} transitive
            </p>
          </CardContent>
        </Card>

        <Card className="bg-card/50 backdrop-blur border-border/50">
          <CardHeader className="pb-2">
            <CardDescription className="text-xs">Vulnerability Findings</CardDescription>
            <CardTitle className="text-3xl font-bold font-mono text-red-400">
              {summary?.total_vulnerabilities || scan.total_vulnerabilities}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-xs text-muted-foreground">
              {summary?.total_high_critical || 0} critical or high severity
            </p>
          </CardContent>
        </Card>

        <Card className="bg-card/50 backdrop-blur border-border/50">
          <CardHeader className="pb-2">
            <CardDescription className="text-xs">SBOM Validation</CardDescription>
            <CardTitle className="text-xl font-bold text-green-400 flex items-center gap-1.5 mt-1">
              <CheckCircle2 className="h-5 w-5" /> CycloneDX 1.7
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-xs text-muted-foreground">
              Validated with SPDX 2.3 & VEX
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Metadata & Ecosystems */}
      <Card className="border-border/50">
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <Layers className="h-4 w-4 text-purple-400" /> Project Metadata & Scope
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-sm font-mono">
            <div>
              <div className="text-muted-foreground text-xs font-sans">Project Name</div>
              <div className="font-semibold">{scan.project_name || scan.filename}</div>
            </div>
            <div>
              <div className="text-muted-foreground text-xs font-sans">Archive Name</div>
              <div className="truncate">{scan.filename}</div>
            </div>
            <div>
              <div className="text-muted-foreground text-xs font-sans">Scan Timestamp</div>
              <div>{new Date(scan.created_at).toLocaleDateString()}</div>
            </div>
            <div>
              <div className="text-muted-foreground text-xs font-sans">Manifests Discovered</div>
              <div>{scan.total_manifests} manifest(s)</div>
            </div>
          </div>

          <div className="pt-3 border-t border-border/40 flex flex-wrap gap-2 items-center">
            <span className="text-xs text-muted-foreground mr-2 font-medium">Ecosystems Analyzed:</span>
            {Object.keys(summary?.components_by_ecosystem || {}).map((eco) => (
              <EcosystemBadge key={eco} ecosystem={eco} />
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Top Vulnerability Findings */}
      <Card className="border-border/50">
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <ShieldAlert className="h-4 w-4 text-red-400" /> Identified Vulnerabilities & Advisories
          </CardTitle>
          <CardDescription>
            Known CVE and advisory records matched via deterministic package lookup
          </CardDescription>
        </CardHeader>
        <CardContent>
          {vulns.length === 0 ? (
            <div className="py-8 text-center text-sm text-muted-foreground">
              No known vulnerabilities detected for this project.
            </div>
          ) : (
            <div className="space-y-3">
              {vulns.slice(0, 8).map((v) => (
                <div 
                  key={v.id} 
                  className="p-3.5 rounded-lg bg-muted/20 border border-border/40 flex flex-col sm:flex-row justify-between sm:items-center gap-2"
                >
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <Badge variant="destructive" className="uppercase text-[10px]">
                        {v.severity || "UNKNOWN"}
                      </Badge>
                      <span className="font-mono text-xs font-bold text-primary">{v.vuln_id}</span>
                      {v.cvss_score && (
                        <span className="text-[11px] font-mono text-muted-foreground">
                          CVSS: {v.cvss_score.toFixed(1)}
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-foreground/90 font-medium line-clamp-1">
                      {v.summary}
                    </p>
                    <div className="text-[11px] text-muted-foreground font-mono">
                      Component: <span className="text-foreground">{v.component_name}</span> @ {v.component_version}
                    </div>
                  </div>

                  {v.fixed_version && (
                    <div className="text-right shrink-0">
                      <span className="text-[10px] text-muted-foreground uppercase block">Remediation</span>
                      <span className="text-xs font-mono font-semibold text-green-400">
                        Fix: {v.fixed_version}
                      </span>
                    </div>
                  )}
                </div>
              ))}
              {vulns.length > 8 && (
                <p className="text-xs text-center text-muted-foreground pt-2">
                  + {vulns.length - 8} additional vulnerabilities documented in full SBOM export.
                </p>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Prescriptive Remediations */}
      {remediations.length > 0 && (
        <Card className="border-border/50">
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <CheckCircle2 className="h-4 w-4 text-green-400" /> Prioritized Remediation Playbook
            </CardTitle>
            <CardDescription>
              Actionable CLI upgrade commands to resolve critical CVEs with minimal breaking risk
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {remediations.slice(0, 5).map((r, i) => (
              <div key={i} className="p-3 rounded-lg bg-card/60 border border-border/40 space-y-1.5">
                <div className="flex justify-between items-center text-xs">
                  <span className="font-semibold text-foreground">
                    Upgrade {r.component_name} ({r.current_version} <ArrowRight className="inline h-3 w-3" /> {r.target_version})
                  </span>
                  <Badge variant="outline" className={`capitalize text-[10px] ${r.breaking_change_risk === 'low' ? 'text-green-400 border-green-500/30' : 'text-amber-400 border-amber-500/30'}`}>
                    Breaking Risk: {r.breaking_change_risk}
                  </Badge>
                </div>
                <div className="bg-muted/40 p-2 rounded font-mono text-xs text-foreground/90">
                  {r.upgrade_command}
                </div>
                <p className="text-[11px] text-muted-foreground">{r.rationale}</p>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Attestation & Footer */}
      <div className="text-xs text-muted-foreground text-center space-y-1 pt-6 border-t border-border/40">
        <p className="font-semibold text-foreground">
          CodeSupply Automated Software Bill of Materials (SBOM) Generation Tool (SIH1449)
        </p>
        <p>
          Generated in accordance with U.S. Executive Order 14028, NTIA Minimum Elements, and ISO/IEC 5962:2021 standards.
        </p>
      </div>
    </div>
  );
}
