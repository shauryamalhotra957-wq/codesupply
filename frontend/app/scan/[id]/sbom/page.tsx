"use client";

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { SBOMData } from '@/types';
import { Skeleton } from '@/components/ui/skeleton';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Download, Copy, CheckCircle2, FileCode, Check, FileSpreadsheet, ShieldAlert } from 'lucide-react';
import { ScrollArea } from '@/components/ui/scroll-area';

export default function SBOMPage({ params }: { params: { id: string } }) {
  const [format, setFormat] = useState<'cyclonedx' | 'spdx' | 'vex'>('cyclonedx');
  const [cycloneSbom, setCycloneSbom] = useState<SBOMData | null>(null);
  const [spdxData, setSpdxData] = useState<any | null>(null);
  const [vexData, setVexData] = useState<any | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    setIsLoading(true);
    Promise.all([
      api.getSBOM(params.id).catch(() => null),
      api.getSPDX(params.id).catch(() => null),
      api.getVEX(params.id).catch(() => null),
    ])
      .then(([cdx, spdx, vex]) => {
        setCycloneSbom(cdx);
        setSpdxData(spdx);
        setVexData(vex);
      })
      .finally(() => setIsLoading(false));
  }, [params.id]);

  const handleDownload = async () => {
    try {
      if (format === 'cyclonedx') {
        const blob = await api.downloadSBOM(params.id);
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `sbom-cyclonedx-${params.id.substring(0, 8)}.cdx.json`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
      } else if (format === 'spdx') {
        const blob = await api.downloadSPDX(params.id);
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `sbom-spdx-${params.id.substring(0, 8)}.spdx.json`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
      } else {
        const blob = await api.downloadVEX(params.id);
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `vex-cyclonedx-${params.id.substring(0, 8)}.cdx.json`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleCopy = () => {
    let dataToCopy: any = null;
    if (format === 'cyclonedx') dataToCopy = cycloneSbom?.content;
    else if (format === 'spdx') dataToCopy = spdxData;
    else dataToCopy = vexData;

    if (dataToCopy) {
      navigator.clipboard.writeText(JSON.stringify(dataToCopy, null, 2));
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleExportCSV = () => {
    window.open(api.exportCSVUrl(params.id), '_blank');
  };

  if (isLoading) {
    return (
      <div className="p-6 space-y-6 h-full flex flex-col">
        <Skeleton className="h-32 w-full rounded-2xl" />
        <Skeleton className="flex-1 w-full rounded-2xl" />
      </div>
    );
  }

  let activeContent: any = null;
  let componentCount = 0;
  let relationshipCount = 0;
  let formatTitle = '';
  let badgeLabel = '';
  let badgeColor = '';
  let versionLabel = '';

  if (format === 'cyclonedx') {
    activeContent = cycloneSbom?.content;
    componentCount = cycloneSbom?.component_count || 0;
    relationshipCount = cycloneSbom?.relationship_count || 0;
    formatTitle = 'CycloneDX 1.7 JSON';
    badgeLabel = 'OWASP CycloneDX';
    badgeColor = 'bg-purple-600 text-white';
    versionLabel = `v${cycloneSbom?.spec_version || '1.7'}`;
  } else if (format === 'spdx') {
    activeContent = spdxData;
    componentCount = spdxData?.packages?.length || 0;
    relationshipCount = spdxData?.relationships?.length || 0;
    formatTitle = 'SPDX 2.3 JSON';
    badgeLabel = 'Linux Foundation SPDX';
    badgeColor = 'bg-blue-600 text-white';
    versionLabel = 'v2.3 (ISO/IEC 5962:2021)';
  } else {
    activeContent = vexData;
    componentCount = vexData?.vulnerabilities?.length || 0;
    relationshipCount = 0;
    formatTitle = 'CycloneDX 1.7 VEX';
    badgeLabel = 'CISA / CycloneDX VEX';
    badgeColor = 'bg-amber-600 text-white';
    versionLabel = 'v1.7 Exploitability eXchange';
  }

  return (
    <div className="p-6 h-full flex flex-col gap-6">
      {/* Format Toggle & Action Bar */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Software Bill of Materials & VEX</h2>
          <p className="text-xs text-muted-foreground mt-0.5">
            Cryptographically structured software supply chain manifests and machine-readable exploitability statements.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <div className="flex items-center gap-1.5 p-1 rounded-xl bg-card border border-border/50">
            <Button
              size="sm"
              variant={format === 'cyclonedx' ? 'default' : 'ghost'}
              onClick={() => setFormat('cyclonedx')}
              className="rounded-lg text-xs"
            >
              CycloneDX 1.7
            </Button>
            <Button
              size="sm"
              variant={format === 'spdx' ? 'default' : 'ghost'}
              onClick={() => setFormat('spdx')}
              className="rounded-lg text-xs"
            >
              SPDX 2.3 (ISO)
            </Button>
            <Button
              size="sm"
              variant={format === 'vex' ? 'default' : 'ghost'}
              onClick={() => setFormat('vex')}
              className="rounded-lg text-xs gap-1.5"
            >
              <ShieldAlert className="h-3.5 w-3.5 text-amber-400" />
              VEX Statements
            </Button>
          </div>

          <Button
            variant="outline"
            size="sm"
            onClick={handleExportCSV}
            className="rounded-xl text-xs gap-1.5 border-border/50 hover:bg-white/5"
          >
            <FileSpreadsheet className="h-3.5 w-3.5 text-emerald-400" />
            Export CSV
          </Button>
        </div>
      </div>

      <Card className="wispr-glass rounded-2xl border-border/40">
        <CardContent className="p-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="space-y-2">
            <div className="flex items-center gap-3">
              <Badge className={badgeColor}>
                {badgeLabel}
              </Badge>
              <span className="font-mono text-sm text-muted-foreground">
                {versionLabel}
              </span>
            </div>
            <div className="flex items-center gap-2 mt-2">
              <CheckCircle2 className="h-4 w-4 text-emerald-400" />
              <span className="font-medium text-sm">
                {format === 'vex' 
                  ? 'Authenticated Exploitability & Remediation Ledger' 
                  : 'Valid & Cryptographically Formatted Manifest'}
              </span>
            </div>
            <p className="text-xs text-muted-foreground font-mono">
              {format === 'vex'
                ? `${componentCount} active vulnerability statements analyzed`
                : `${componentCount} components / packages | ${relationshipCount} dependency relationships`}
            </p>
          </div>
          
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={handleCopy} className="gap-2 rounded-xl text-xs">
              {copied ? <Check className="h-3.5 w-3.5 text-emerald-400" /> : <Copy className="h-3.5 w-3.5" />}
              {copied ? "Copied" : "Copy JSON"}
            </Button>
            <Button size="sm" onClick={handleDownload} className="gap-2 rounded-xl text-xs bg-primary">
              <Download className="h-3.5 w-3.5" />
              Download {format === 'cyclonedx' ? 'CycloneDX' : format === 'spdx' ? 'SPDX' : 'VEX'}
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card className="flex-1 flex flex-col min-h-[420px] rounded-2xl border-border/40 overflow-hidden">
        <div className="flex justify-between items-center px-4 py-3 border-b border-border/40 bg-card/60">
          <div className="flex items-center gap-2 text-xs font-semibold">
            <FileCode className="h-4 w-4 text-purple-400" />
            <span>Raw Document Preview ({formatTitle})</span>
          </div>
          <span className="text-[11px] font-mono text-muted-foreground">
            {format === 'vex' ? 'CycloneDX 1.7 / CISA VEX Standard' : 'JSON Schema Compliant'}
          </span>
        </div>
        <ScrollArea className="flex-1 bg-[#090b10] text-[#e2e8f0] p-4 font-mono text-xs leading-relaxed">
          <pre>
            {activeContent ? JSON.stringify(activeContent, null, 2) : "Loading document..."}
          </pre>
        </ScrollArea>
      </Card>
    </div>
  );
}
