import React, { useState, useMemo } from 'react';
import { 
  ShieldAlert, 
  AlertTriangle, 
  AlertOctagon, 
  Info, 
  Search, 
  CheckCircle2, 
  ExternalLink, 
  Wrench, 
  FileSearch, 
  ArrowRight,
  Copy,
  Check,
  Zap
} from 'lucide-react';

export default function FindingsView({ 
  findings, 
  components, 
  onSelectComponent 
}) {
  const [search, setSearch] = useState('');
  const [severityFilter, setSeverityFilter] = useState('all');
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [copiedIndex, setCopiedIndex] = useState(null);

  const counts = useMemo(() => {
    return {
      total: findings.length,
      high: findings.filter(f => f.severity === 'HIGH' || f.severity === 'CRITICAL').length,
      medium: findings.filter(f => f.severity === 'MEDIUM').length,
      low: findings.filter(f => f.severity === 'LOW' || f.severity === 'INFO').length,
    };
  }, [findings]);

  const categories = useMemo(() => {
    return Array.from(new Set(findings.map(f => f.category))).filter(Boolean);
  }, [findings]);

  const filteredFindings = useMemo(() => {
    return findings.filter(f => {
      const searchMatch = !search || 
        f.component_name?.toLowerCase().includes(search.toLowerCase()) ||
        f.title?.toLowerCase().includes(search.toLowerCase()) ||
        f.explanation?.toLowerCase().includes(search.toLowerCase()) ||
        f.category?.toLowerCase().includes(search.toLowerCase());

      const sevMatch = severityFilter === 'all' || 
        (severityFilter === 'high' && (f.severity === 'HIGH' || f.severity === 'CRITICAL')) ||
        (severityFilter === 'medium' && f.severity === 'MEDIUM') ||
        (severityFilter === 'low' && (f.severity === 'LOW' || f.severity === 'INFO'));

      const catMatch = categoryFilter === 'all' || f.category === categoryFilter;

      return searchMatch && sevMatch && catMatch;
    });
  }, [findings, search, severityFilter, categoryFilter]);

  const handleCopyFix = (text, idx) => {
    navigator.clipboard.writeText(text);
    setCopiedIndex(idx);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Header & Metrics */}
      <div className="space-y-4">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center space-x-2.5">
            <ShieldAlert className="w-6 h-6 text-red-400" />
            <span>Supply-Chain Anomalies & CVE Findings</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Deterministic risk detection, version pinning hygiene, CISA KEV exploitation markers, and recommended fixes.
          </p>
        </div>

        {/* Severity Metric Cards */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <button 
            onClick={() => setSeverityFilter('all')}
            className={`p-4 rounded-xl border text-left transition ${
              severityFilter === 'all' ? 'bg-slate-800 border-indigo-500' : 'bg-slate-900 border-slate-800 hover:border-slate-700'
            }`}
          >
            <span className="text-xs text-slate-400 font-semibold uppercase">Total Anomalies</span>
            <div className="text-2xl font-bold text-white mt-1">{counts.total}</div>
          </button>

          <button 
            onClick={() => setSeverityFilter('high')}
            className={`p-4 rounded-xl border text-left transition ${
              severityFilter === 'high' ? 'bg-red-950/40 border-red-500' : 'bg-slate-900 border-slate-800 hover:border-red-900/40'
            }`}
          >
            <span className="text-xs text-red-400 font-semibold uppercase">Critical / High</span>
            <div className="text-2xl font-bold text-red-400 mt-1">{counts.high}</div>
          </button>

          <button 
            onClick={() => setSeverityFilter('medium')}
            className={`p-4 rounded-xl border text-left transition ${
              severityFilter === 'medium' ? 'bg-amber-950/40 border-amber-500' : 'bg-slate-900 border-slate-800 hover:border-amber-900/40'
            }`}
          >
            <span className="text-xs text-amber-400 font-semibold uppercase">Medium Risk</span>
            <div className="text-2xl font-bold text-amber-400 mt-1">{counts.medium}</div>
          </button>

          <button 
            onClick={() => setSeverityFilter('low')}
            className={`p-4 rounded-xl border text-left transition ${
              severityFilter === 'low' ? 'bg-blue-950/40 border-blue-500' : 'bg-slate-900 border-slate-800 hover:border-blue-900/40'
            }`}
          >
            <span className="text-xs text-blue-400 font-semibold uppercase">Low / Hygiene</span>
            <div className="text-2xl font-bold text-blue-400 mt-1">{counts.low}</div>
          </button>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="relative w-full md:w-96">
          <Search className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search anomalies by keyword or package name..."
            className="w-full bg-slate-800 border border-slate-700 rounded-lg pl-9 pr-4 py-2 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>

        <div className="flex flex-wrap items-center gap-2">
          {/* Category Filter */}
          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="bg-slate-800 border border-slate-700 text-slate-200 text-xs rounded-lg px-3 py-2 focus:outline-none"
          >
            <option value="all">All Categories</option>
            {categories.map((c, i) => (
              <option key={i} value={c}>{c}</option>
            ))}
          </select>

          {/* Reset Filters */}
          {(severityFilter !== 'all' || categoryFilter !== 'all' || search) && (
            <button
              onClick={() => { setSeverityFilter('all'); setCategoryFilter('all'); setSearch(''); }}
              className="text-xs text-indigo-400 hover:text-indigo-300 font-medium px-2 py-1"
            >
              Reset Filters
            </button>
          )}
        </div>
      </div>

      {/* Findings List */}
      <div className="space-y-4">
        {filteredFindings.length === 0 ? (
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-12 text-center space-y-3">
            <CheckCircle2 className="w-10 h-10 text-emerald-400 mx-auto" />
            <h3 className="text-base font-bold text-white">No Matching Findings</h3>
            <p className="text-xs text-slate-400 max-w-md mx-auto">
              No anomalies match your active filters. If you want to test risk detection, try running the
              "Anomalous / Broken Project" sample from the Upload page!
            </p>
          </div>
        ) : (
          filteredFindings.map((finding, idx) => {
            const isHigh = finding.severity === 'HIGH' || finding.severity === 'CRITICAL';
            const isMed = finding.severity === 'MEDIUM';
            const isCve = finding.category === 'Vulnerability' || finding.title?.includes('CVE-');
            const isKev = finding.title?.includes('CISA KEV');

            const compObj = components.find(
              c => c.name.toLowerCase() === finding.component_name?.toLowerCase()
            );

            return (
              <div 
                key={idx}
                className={`bg-slate-900 border rounded-2xl p-6 space-y-4 shadow-xl transition-all ${
                  isHigh ? 'border-red-900/60 hover:border-red-500/60' : isMed ? 'border-amber-900/60 hover:border-amber-500/60' : 'border-slate-800 hover:border-slate-700'
                }`}
              >
                {/* Header */}
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-3">
                  <div className="flex items-center space-x-2.5 flex-wrap gap-y-1">
                    <span className={`px-2.5 py-0.5 rounded text-[10px] font-extrabold uppercase ${
                      isHigh ? 'bg-red-500/20 text-red-400 border border-red-500/30' : isMed ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30' : 'bg-blue-500/20 text-blue-400 border border-blue-500/30'
                    }`}>
                      {finding.severity}
                    </span>
                    <span className="text-xs text-slate-400 font-semibold">• {finding.category}</span>
                    {isKev && (
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30 flex items-center space-x-1">
                        <Zap className="w-3 h-3 text-amber-400" />
                        <span>CISA KEV EXPLOITED</span>
                      </span>
                    )}
                    <h3 className="text-sm font-bold text-white">{finding.title}</h3>
                  </div>

                  {compObj && (
                    <button
                      onClick={() => onSelectComponent(compObj)}
                      className="flex items-center space-x-1 text-xs text-indigo-400 hover:text-indigo-300 font-semibold"
                    >
                      <span>Inspect {compObj.name}</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </button>
                  )}
                </div>

                {/* Evidence Snippet */}
                {finding.evidence && (
                  <div className="space-y-1">
                    <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider flex items-center space-x-1.5">
                      <FileSearch className="w-3.5 h-3.5 text-indigo-400" />
                      <span>Manifest & CVE Evidence</span>
                    </span>
                    <div className="font-mono text-xs text-slate-300 bg-slate-950 p-3 rounded-lg border border-slate-800 break-all select-all">
                      {finding.evidence}
                    </div>
                  </div>
                )}

                {/* Contextual Explanation */}
                {finding.explanation && (
                  <div className="space-y-1">
                    <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                      Supply-Chain Risk Analysis
                    </span>
                    <p className="text-xs text-slate-300 leading-relaxed">
                      {finding.explanation}
                    </p>
                  </div>
                )}

                {/* Actionable Remediation & 1-Click Copy */}
                {finding.recommendation && (
                  <div className="bg-emerald-950/20 border border-emerald-900/40 rounded-xl p-3.5 flex items-center justify-between gap-4">
                    <div className="space-y-0.5">
                      <span className="text-[11px] font-bold text-emerald-400 uppercase tracking-wider flex items-center space-x-1.5">
                        <Wrench className="w-3.5 h-3.5" />
                        <span>Recommended Remediation</span>
                      </span>
                      <p className="text-xs text-emerald-300 font-medium leading-relaxed font-mono">
                        {finding.recommendation}
                      </p>
                    </div>
                    <button
                      onClick={() => handleCopyFix(finding.recommendation, idx)}
                      className="py-1.5 px-3 bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-300 border border-emerald-500/30 rounded-lg text-xs font-semibold flex items-center space-x-1.5 transition shrink-0"
                    >
                      {copiedIndex === idx ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                      <span>{copiedIndex === idx ? 'Copied' : 'Copy Fix'}</span>
                    </button>
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
