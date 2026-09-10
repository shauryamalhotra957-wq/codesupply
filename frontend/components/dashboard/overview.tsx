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
  Activity
} from 'lucide-react';
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

  const calculateRiskGrade = () => {
    if (summary.total_high_critical > 0) return { grade: 'F', color: 'text-red-600', text: 'Critical Risk' };
    if (summary.total_vulnerabilities > summary.total_high_critical) return { grade: 'D', color: 'text-amber-500', text: 'Moderate Risk' };
    if (summary.total_unknown_versions > 0) return { grade: 'B', color: 'text-blue-500', text: 'Low Risk' };
    return { grade: 'A', color: 'text-green-500', text: 'Excellent' };
  };

  const riskGrade = calculateRiskGrade();

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold tracking-tight">Overview</h2>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => window.location.reload()}>Rescan</Button>
          <Button onClick={downloadSbom}>Export SBOM</Button>
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
            <span>CycloneDX 1.6 SBOM {summary.sbom_valid ? 'validated' : 'generated'}</span>
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
    </div>
  );
}
