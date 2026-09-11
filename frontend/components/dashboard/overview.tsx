"use client";

import { useScan } from '@/hooks/use-scan';
import { MetricCard } from '@/components/shared/metric-card';
import { Skeleton } from '@/components/ui/skeleton';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  Package, 
  ShieldAlert, 
  AlertTriangle, 
  HelpCircle,
  CheckCircle2,
  AlertCircle,
  Activity,
  Terminal,
  Wrench,
  Copy,
  Check
} from 'lucide-react';
import { RemediationAction } from '@/types';
import { 
  PieChart, 
  Pie, 
  Cell, 
  ResponsiveContainer, 
  Tooltip as RechartsTooltip,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Legend
} from 'recharts';
import { api } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { useState, useEffect } from 'react';

const RISK_COLORS = {
  critical: '#b91c1c', // red-700
  high: '#ef4444',     // red-500
  medium: '#f59e0b',   // amber-500
  low: '#3b82f6',      // blue-500
  unknown: '#9ca3af',  // gray-400
  none: '#16a34a'      // green-600
};

const ECOSYSTEM_COLORS = {
  npm: '#cb3837',
  pypi: '#3776ab',
  maven: '#c71a22',
  go: '#00add8',
  cargo: '#dea584'
};

const VULN_COLORS = {
  CRITICAL: '#b91c1c',
  HIGH: '#ef4444',
  MODERATE: '#f59e0b',
  LOW: '#3b82f6',
  UNKNOWN: '#9ca3af'
};

export function DashboardOverview({ scanId }: { scanId: string }) {
  const { scan, summary, isLoading } = useScan(scanId);
  const [remediations, setRemediations] = useState<RemediationAction[]>([]);
  const [copiedCmd, setCopiedCmd] = useState<string | null>(null);

  useEffect(() => {
    if (scanId) {
      api
        .getRemediations(scanId)
        .then((res) => setRemediations(res.remediations || []))
        .catch(() => {});
    }
  }, [scanId]);

  const copyCommand = (cmd: string) => {
    navigator.clipboard.writeText(cmd);
    setCopiedCmd(cmd);
    setTimeout(() => setCopiedCmd(null), 2000);
  };

  if (isLoading || !summary) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
          {[...Array(5)].map((_, i) => <Skeleton key={i} className="h-32 rounded-xl" />)}
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <Skeleton className="h-80 rounded-xl" />
          <Skeleton className="h-80 rounded-xl" />
          <Skeleton className="h-80 rounded-xl" />
        </div>
      </div>
    );
  }

  const riskData = Object.entries(summary.components_by_risk)
    .filter(([_, count]) => count > 0)
    .map(([name, value]) => ({ name, value }));

  const ecosystemData = Object.entries(summary.components_by_ecosystem)
    .map(([name, value]) => ({ name, value }));
    
  const vulnData = Object.entries(summary.vulnerabilities_by_severity)
    .filter(([_, count]) => count > 0)
    .map(([name, value]) => ({ name: name.toUpperCase(), count: value }));

  const downloadSbom = async () => {
    try {
      const blob = await api.downloadSBOM(scanId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `sbom-${scanId.substring(0,8)}.json`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error("Failed to download SBOM", err);
    }
  };

  const downloadSpdx = async () => {
    try {
      const blob = await api.downloadSPDX(scanId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `sbom-${scanId.substring(0,8)}.spdx.json`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error("Failed to download SPDX SBOM", err);
    }
  };

  const openReport = () => {
    const apiBase = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";
    window.open(`${apiBase}/scans/${scanId}/report/html`, '_blank');
  };

  const calculateRiskGrade = () => {
    if (summary.total_high_critical > 0) return { grade: 'F', color: 'text-red-600', text: 'Critical Risk' };
    if (summary.total_vulnerabilities > summary.total_high_critical) return { grade: 'D', color: 'text-amber-500', text: 'Moderate Risk' };
    if (summary.total_unknown_versions > 0) return { grade: 'B', color: 'text-blue-500', text: 'Low Risk' };
    return { grade: 'A', color: 'text-green-500', text: 'Excellent' };
  };

  const riskGrade = calculateRiskGrade();

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <h2 className="text-2xl font-bold tracking-tight">Overview</h2>
        <div className="flex flex-wrap gap-2">
          <Button variant="outline" size="sm" onClick={() => window.location.reload()}>Rescan</Button>
          <Button variant="outline" size="sm" onClick={downloadSbom}>CycloneDX 1.7</Button>
          <Button variant="outline" size="sm" onClick={downloadSpdx}>SPDX 2.3</Button>
          <Button size="sm" className="bg-primary" onClick={openReport}>Executive Report</Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
        <Card className="flex flex-col items-center justify-center p-4">
          <div className="text-sm font-medium text-muted-foreground mb-1">Risk Score</div>
          <div className={`text-5xl font-black ${riskGrade.color}`}>{riskGrade.grade}</div>
          <div className="text-xs text-muted-foreground mt-1">{riskGrade.text}</div>
        </Card>
        <MetricCard
          title="Total Components"
          value={summary.total_components}
          icon={Package}
          subtitle={`${summary.manifests_discovered} manifests parsed`}
        />
        <MetricCard
          title="Vulnerabilities"
          value={summary.total_vulnerabilities}
          icon={AlertTriangle}
          subtitle="Known CVEs/GHSAs"
          iconClassName={summary.total_vulnerabilities > 0 ? "text-destructive" : ""}
        />
        <MetricCard
          title="High/Critical Risk"
          value={summary.total_high_critical}
          icon={ShieldAlert}
          subtitle="Requires immediate attention"
          iconClassName={summary.total_high_critical > 0 ? "text-destructive" : ""}
        />
        <MetricCard
          title="Unknown Versions"
          value={summary.total_unknown_versions}
          icon={HelpCircle}
          subtitle="Unresolved resolution"
        />
      </div>

      <Card className="bg-muted/30 border-dashed">
        <CardContent className="p-4 flex flex-wrap gap-x-8 gap-y-2 text-sm">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="h-4 w-4 text-green-500" />
            <span>{summary.total_components} components analyzed</span>
          </div>
          <div className="flex items-center gap-2">
            {summary.sbom_valid ? (
              <CheckCircle2 className="h-4 w-4 text-green-500" />
            ) : (
              <AlertCircle className="h-4 w-4 text-amber-500" />
            )}
            <span>CycloneDX 1.7 SBOM {summary.sbom_valid ? 'validated' : 'generated'}</span>
          </div>
          <div className="flex items-center gap-2">
            <CheckCircle2 className="h-4 w-4 text-green-500" />
            <span>{summary.intelligence_checked}/{summary.intelligence_total} vulnerability checks completed</span>
          </div>
          {summary.total_unknown_versions > 0 && (
            <div className="flex items-center gap-2">
              <AlertTriangle className="h-4 w-4 text-amber-500" />
              <span>{summary.total_unknown_versions} dependencies have unresolved version information</span>
            </div>
          )}
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-lg font-medium">Risk Distribution</CardTitle>
          </CardHeader>
          <CardContent className="h-72 flex flex-col">
            {riskData.length > 0 ? (
              <>
                <div className="flex-1">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={riskData}
                        cx="50%"
                        cy="50%"
                        innerRadius={50}
                        outerRadius={75}
                        paddingAngle={2}
                        dataKey="value"
                      >
                        {riskData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={RISK_COLORS[entry.name as keyof typeof RISK_COLORS] || RISK_COLORS.unknown} />
                        ))}
                      </Pie>
                      <RechartsTooltip 
                        formatter={(value: number) => [`${value} components`, 'Count']}
                        labelFormatter={(label: string) => label.charAt(0).toUpperCase() + label.slice(1) + ' Risk'}
                      />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
                <div className="flex flex-wrap justify-center gap-2 mt-2">
                  {riskData.map(entry => (
                    <div key={entry.name} className="flex items-center gap-1 text-xs">
                      <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: RISK_COLORS[entry.name as keyof typeof RISK_COLORS] || RISK_COLORS.unknown }} />
                      <span className="capitalize">{entry.name}: {entry.value}</span>
                    </div>
                  ))}
                </div>
              </>
            ) : (
              <div className="h-full flex items-center justify-center text-muted-foreground">No risk data</div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg font-medium">Ecosystems</CardTitle>
          </CardHeader>
          <CardContent className="h-72 flex flex-col">
            {ecosystemData.length > 0 ? (
              <>
                <div className="flex-1">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={ecosystemData}
                        cx="50%"
                        cy="50%"
                        innerRadius={50}
                        outerRadius={75}
                        paddingAngle={2}
                        dataKey="value"
                      >
                        {ecosystemData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={ECOSYSTEM_COLORS[entry.name as keyof typeof ECOSYSTEM_COLORS] || '#8884d8'} />
                        ))}
                      </Pie>
                      <RechartsTooltip formatter={(value: number) => [`${value} components`, 'Count']} />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
                <div className="flex flex-wrap justify-center gap-2 mt-2">
                  {ecosystemData.map(entry => (
                    <div key={entry.name} className="flex items-center gap-1 text-xs">
                      <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: ECOSYSTEM_COLORS[entry.name as keyof typeof ECOSYSTEM_COLORS] || '#8884d8' }} />
                      <span className="capitalize">{entry.name}: {entry.value}</span>
                    </div>
                  ))}
                </div>
              </>
            ) : (
              <div className="h-full flex items-center justify-center text-muted-foreground">No ecosystem data</div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg font-medium">Vulnerabilities</CardTitle>
          </CardHeader>
          <CardContent className="h-72">
            {vulnData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={vulnData} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} />
                  <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fontSize: 10 }} />
                  <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 10 }} />
                  <RechartsTooltip cursor={{ fill: 'transparent' }} contentStyle={{ borderRadius: '8px' }} />
                  <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                    {vulnData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={VULN_COLORS[entry.name as keyof typeof VULN_COLORS] || VULN_COLORS.UNKNOWN} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-muted-foreground">No vulnerabilities found</div>
            )}
          </CardContent>
        </Card>
      </div>

      {remediations.length > 0 && (
        <Card className="wispr-glass rounded-2xl border-border/40 overflow-hidden">
          <CardHeader className="flex flex-row items-center justify-between pb-3 border-b border-border/30">
            <div className="flex items-center gap-2.5">
              <div className="h-8 w-8 rounded-lg bg-purple-500/10 border border-purple-500/20 flex items-center justify-center">
                <Wrench className="h-4 w-4 text-purple-400" />
              </div>
              <div>
                <CardTitle className="text-base font-semibold">Prescriptive Remediation Playbook</CardTitle>
                <p className="text-xs text-muted-foreground">Prioritized upgrade actions with 1-click executable terminal commands</p>
              </div>
            </div>
            <Badge variant="outline" className="text-xs border-purple-500/30 text-purple-400 bg-purple-500/5">
              {remediations.length} Actionable Upgrades
            </Badge>
          </CardHeader>
          <CardContent className="p-4 space-y-3">
            {remediations.slice(0, 3).map((action) => (
              <div
                key={action.component_id}
                className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-3.5 rounded-xl bg-card/60 border border-border/40 hover:border-border/80 transition-all"
              >
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-sm">{action.component_name}</span>
                    <Badge variant="outline" className="text-[10px] font-mono capitalize">
                      {action.ecosystem}
                    </Badge>
                    <span className="text-xs text-muted-foreground font-mono">
                      {action.current_version} &rarr; <span className="text-emerald-400 font-semibold">{action.target_version}</span>
                    </span>
                    <Badge
                      className={
                        action.severity === 'critical'
                          ? 'bg-red-600 text-white text-[10px]'
                          : action.severity === 'high'
                          ? 'bg-orange-600 text-white text-[10px]'
                          : 'bg-amber-600 text-white text-[10px]'
                      }
                    >
                      {action.severity.toUpperCase()}
                    </Badge>
                    {action.breaking_change_risk === 'low' ? (
                      <Badge variant="outline" className="text-[10px] text-emerald-400 border-emerald-500/30">
                        Safe Patch
                      </Badge>
                    ) : (
                      <Badge variant="outline" className="text-[10px] text-amber-400 border-amber-500/30">
                        Major Bump
                      </Badge>
                    )}
                  </div>
                  <p className="text-xs text-muted-foreground">{action.rationale}</p>
                </div>

                <div className="flex items-center gap-2 shrink-0">
                  <code className="px-3 py-1.5 rounded-lg bg-black/60 border border-white/10 font-mono text-xs text-purple-300 max-w-xs sm:max-w-md truncate">
                    {action.upgrade_command}
                  </code>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => copyCommand(action.upgrade_command)}
                    className="h-8 px-2.5 rounded-lg text-xs gap-1.5"
                  >
                    {copiedCmd === action.upgrade_command ? (
                      <>
                        <Check className="h-3.5 w-3.5 text-emerald-400" />
                        <span className="text-emerald-400">Copied</span>
                      </>
                    ) : (
                      <>
                        <Copy className="h-3.5 w-3.5" />
                        <span>Copy</span>
                      </>
                    )}
                  </Button>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
