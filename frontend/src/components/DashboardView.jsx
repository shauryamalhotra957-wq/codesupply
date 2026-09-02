import React from 'react';
import { 
  Boxes, 
  Layers, 
  ShieldAlert, 
  CheckCircle2, 
  FileCode2, 
  AlertTriangle, 
  ArrowRight,
  TrendingUp,
  FileCheck2,
  Lock,
  GitBranch
} from 'lucide-react';
import { 
  ResponsiveContainer, 
  PieChart, 
  Pie, 
  Cell, 
  Tooltip, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid 
} from 'recharts';

export default function DashboardView({ 
  project, 
  components, 
  findings, 
  onNavigateTab, 
  onSelectComponent 
}) {
  if (!project) return null;

  const total = project.total_components || 0;
  const direct = project.direct_count || 0;
  const transitive = project.transitive_count || 0;
  const pinned = project.pinned_count || 0;
  const unpinned = project.unpinned_count || 0;
  const pinnedPct = total > 0 ? Math.round((pinned / total) * 100) : 100;

  // Ecosystem chart data
  const pypiCount = components.filter(c => c.ecosystem === 'pypi').length;
  const npmCount = components.filter(c => c.ecosystem === 'npm').length;

  const ecoData = [
    { name: 'PyPI (Python)', value: pypiCount, color: '#3b82f6' },
    { name: 'NPM (Node.js)', value: npmCount, color: '#10b981' },
  ].filter(d => d.value > 0);

  // Direct vs Transitive chart data
  const depTypeData = [
    { name: 'Direct', count: direct, fill: '#6366f1' },
    { name: 'Transitive', count: transitive, fill: '#a855f7' },
    { name: 'Pinned', count: pinned, fill: '#10b981' },
    { name: 'Unpinned', count: unpinned, fill: '#ef4444' },
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Project Header Banner */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2 mb-1">
            <h1 className="text-2xl font-bold text-white">{project.name}</h1>
            <span className="text-xs px-2.5 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 font-semibold border border-indigo-500/30">
              CycloneDX v1.5 Ready
            </span>
          </div>
          <p className="text-xs text-slate-400">
            Scanned on {new Date(project.created_at).toLocaleString()} • Ecosystems: {project.ecosystems.join(', ').toUpperCase() || 'None'}
          </p>
        </div>

        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => onNavigateTab('graph')}
            className="flex items-center space-x-1.5 bg-indigo-600 hover:bg-indigo-500 text-white px-3.5 py-2 rounded-lg text-xs font-semibold shadow-md shadow-indigo-600/30 transition"
          >
            <GitBranch className="w-4 h-4" />
            <span>Explore Dependency Graph</span>
          </button>
          <button
            onClick={() => onNavigateTab('export')}
            className="flex items-center space-x-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 px-3.5 py-2 rounded-lg text-xs font-semibold border border-slate-700 transition"
          >
            <FileCheck2 className="w-4 h-4 text-emerald-400" />
            <span>Download SBOM</span>
          </button>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Components */}
        <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 relative overflow-hidden">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-medium text-slate-400">Total Components</span>
            <div className="w-8 h-8 rounded-lg bg-indigo-500/10 text-indigo-400 flex items-center justify-center">
              <Boxes className="w-4 h-4" />
            </div>
          </div>
          <div className="text-3xl font-extrabold text-white mb-1">{total}</div>
          <div className="text-[11px] text-slate-400 flex items-center space-x-2">
            <span>Direct: <strong className="text-indigo-300">{direct}</strong></span>
            <span>•</span>
            <span>Transitive: <strong className="text-purple-300">{transitive}</strong></span>
          </div>
        </div>

        {/* Direct Dependencies */}
        <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 relative overflow-hidden">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-medium text-slate-400">Direct Dependencies</span>
            <div className="w-8 h-8 rounded-lg bg-blue-500/10 text-blue-400 flex items-center justify-center">
              <Layers className="w-4 h-4" />
            </div>
          </div>
          <div className="text-3xl font-extrabold text-white mb-1">{direct}</div>
          <div className="text-[11px] text-slate-400">
            {total > 0 ? Math.round((direct / total) * 100) : 0}% of overall bill of materials
          </div>
        </div>

        {/* Pinning Coverage */}
        <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 relative overflow-hidden">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-medium text-slate-400">Version Pinning Rate</span>
            <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${
              pinnedPct >= 80 ? 'bg-emerald-500/10 text-emerald-400' : 'bg-amber-500/10 text-amber-400'
            }`}>
              <CheckCircle2 className="w-4 h-4" />
            </div>
          </div>
          <div className="text-3xl font-extrabold text-white mb-1">{pinnedPct}%</div>
          <div className="text-[11px] text-slate-400">
            <strong className={pinnedPct >= 80 ? 'text-emerald-400' : 'text-amber-400'}>{pinned}</strong> pinned / <strong className="text-red-400">{unpinned}</strong> unpinned
          </div>
        </div>

        {/* Risk Findings */}
        <div 
          onClick={() => onNavigateTab('findings')}
          className="bg-slate-900/90 hover:bg-slate-850 border border-slate-800 hover:border-red-500/40 rounded-xl p-5 cursor-pointer transition relative overflow-hidden group"
        >
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-medium text-slate-400">Risk Findings</span>
            <div className="w-8 h-8 rounded-lg bg-red-500/10 text-red-400 flex items-center justify-center">
              <ShieldAlert className="w-4 h-4" />
            </div>
          </div>
          <div className="text-3xl font-extrabold text-white mb-1 flex items-center space-x-2">
            <span>{project.findings_count}</span>
            <ArrowRight className="w-4 h-4 text-slate-500 group-hover:text-red-400 group-hover:translate-x-1 transition-all" />
          </div>
          <div className="text-[11px] text-slate-400 flex items-center space-x-2">
            <span className="text-red-400 font-bold">{project.high_findings} High</span>
            <span>•</span>
            <span className="text-amber-400 font-bold">{project.medium_findings} Med</span>
            <span>•</span>
            <span className="text-blue-400 font-bold">{project.low_findings} Low</span>
          </div>
        </div>
      </div>

      {/* Visual Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Ecosystem Distribution Donut */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
          <h3 className="text-sm font-bold text-white mb-1">Ecosystem Package Distribution</h3>
          <p className="text-xs text-slate-400 mb-4">Breakdown of detected packages by package registry</p>

          <div className="h-56 w-full flex items-center justify-center">
            {ecoData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={ecoData}
                    cx="50%"
                    cy="50%"
                    innerRadius={55}
                    outerRadius={80}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {ecoData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                    itemStyle={{ color: '#e2e8f0' }}
                  />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="text-xs text-slate-500">No components detected</div>
            )}
          </div>

          <div className="flex justify-center space-x-6 pt-2 border-t border-slate-800 text-xs">
            {ecoData.map((d, i) => (
              <div key={i} className="flex items-center space-x-2">
                <div className="w-3 h-3 rounded-full" style={{ backgroundColor: d.color }} />
                <span className="text-slate-300">{d.name}: <strong>{d.value}</strong></span>
              </div>
            ))}
          </div>
        </div>

        {/* Architecture Breakdown Bar Chart */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
          <h3 className="text-sm font-bold text-white mb-1">Dependency Architecture & Hygiene</h3>
          <p className="text-xs text-slate-400 mb-4">Direct vs transitive and pinning health metrics</p>

          <div className="h-56 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={depTypeData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="name" stroke="#64748b" fontSize={11} tickLine={false} />
                <YAxis stroke="#64748b" fontSize={11} tickLine={false} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                  itemStyle={{ color: '#e2e8f0' }}
                />
                <Bar dataKey="count" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Manifests and Top Findings Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Detected Manifest Files */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-white flex items-center space-x-2">
              <FileCode2 className="w-4 h-4 text-indigo-400" />
              <span>Detected Dependency Manifests ({project.manifest_files.length})</span>
            </h3>
          </div>

          <div className="space-y-2">
            {project.manifest_files.map((mf, i) => (
              <div key={i} className="flex items-center justify-between bg-slate-800/60 border border-slate-700/50 rounded-lg px-3 py-2 text-xs">
                <div className="flex items-center space-x-2 truncate">
                  <span className="font-mono text-indigo-300 font-semibold">{mf.file_name}</span>
                  <span className="text-slate-500 font-mono text-[11px]">({mf.relative_path})</span>
                </div>
                <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                  mf.ecosystem === 'pypi' ? 'bg-blue-500/20 text-blue-400' : 'bg-emerald-500/20 text-emerald-400'
                }`}>
                  {mf.ecosystem.toUpperCase()}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Top Risk Highlights */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-white flex items-center space-x-2">
              <ShieldAlert className="w-4 h-4 text-red-400" />
              <span>Top Risk Highlights ({findings.length})</span>
            </h3>
            {findings.length > 0 && (
              <button 
                onClick={() => onNavigateTab('findings')}
                className="text-xs text-indigo-400 hover:text-indigo-300 font-semibold"
              >
                View all →
              </button>
            )}
          </div>

          {findings.length === 0 ? (
            <div className="p-6 text-center text-xs text-slate-500">
              No anomalies or security risks detected. Excellent manifest hygiene!
            </div>
          ) : (
            <div className="space-y-2.5">
              {findings.slice(0, 3).map((f, i) => (
                <div key={i} className="bg-slate-800/60 border border-slate-700/50 rounded-lg p-3 space-y-1.5">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-white">{f.title}</span>
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                      f.severity === 'HIGH' || f.severity === 'CRITICAL' 
                        ? 'bg-red-500/20 text-red-400 border border-red-500/30' 
                        : 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                    }`}>
                      {f.severity}
                    </span>
                  </div>
                  <p className="text-xs text-slate-400 line-clamp-2">{f.explanation}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
