import React, { useState, useEffect } from 'react';
import { 
  GitCompare, 
  X, 
  ArrowRight, 
  PlusCircle, 
  MinusCircle, 
  RefreshCw, 
  ShieldAlert, 
  ShieldCheck, 
  AlertTriangle,
  Layers
} from 'lucide-react';
import { compareProjects, listProjects } from '../api';

export default function SbomDiffModal({ currentProject, isOpen, onClose }) {
  const [projects, setProjects] = useState([]);
  const [baseId, setBaseId] = useState(currentProject?.id || '');
  const [targetId, setTargetId] = useState('');
  const [diffData, setDiffData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (isOpen) {
      listProjects()
        .then((data) => {
          setProjects(data);
          if (currentProject?.id) {
            setBaseId(currentProject.id);
            const other = data.find((p) => p.id !== currentProject.id);
            if (other) setTargetId(other.id);
          } else if (data.length >= 2) {
            setBaseId(data[0].id);
            setTargetId(data[1].id);
          }
        })
        .catch((err) => setError(err.message));
    }
  }, [isOpen, currentProject?.id]);

  const handleRunCompare = async () => {
    if (!baseId || !targetId) return;
    setIsLoading(true);
    setError(null);
    try {
      const result = await compareProjects(baseId, targetId);
      setDiffData(result);
    } catch (err) {
      setError(err.message || 'Failed to compare projects');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (baseId && targetId && baseId !== targetId) {
      handleRunCompare();
    }
  }, [baseId, targetId]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-5xl max-h-[90vh] flex flex-col shadow-2xl overflow-hidden">
        {/* Modal Header */}
        <div className="p-6 border-b border-slate-800 flex items-center justify-between bg-slate-950/50">
          <div className="flex items-center space-x-3">
            <div className="p-2.5 rounded-xl bg-indigo-600/10 border border-indigo-500/20 text-indigo-400">
              <GitCompare className="w-6 h-6" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-white">SBOM Comparison & Dependency Drift Differ</h2>
              <p className="text-xs text-slate-400">Compare versions, dependency migrations, and newly introduced or resolved CVEs.</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Project Selectors */}
        <div className="p-6 border-b border-slate-800 bg-slate-900/50 grid grid-cols-1 md:grid-cols-2 gap-4 items-center">
          <div>
            <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
              Base Project (Baseline)
            </label>
            <select
              value={baseId}
              onChange={(e) => setBaseId(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
            >
              {projects.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name} ({p.total_components} components)
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
              Target Project (Comparison)
            </label>
            <select
              value={targetId}
              onChange={(e) => setTargetId(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
            >
              {projects.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name} ({p.total_components} components)
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Diff Content View */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {error && (
            <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-xl text-xs text-red-400">
              {error}
            </div>
          )}

          {isLoading ? (
            <div className="py-20 text-center text-slate-500 text-sm flex flex-col items-center space-y-3">
              <RefreshCw className="w-8 h-8 animate-spin text-indigo-400" />
              <span>Analyzing dependency drift and matching CVEs...</span>
            </div>
          ) : diffData ? (
            <>
              {/* Metric Delta Badges */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                <div className="bg-slate-950/60 border border-slate-800 rounded-xl p-4">
                  <span className="text-xs text-slate-500 uppercase font-semibold">Added Components</span>
                  <div className="text-2xl font-bold text-emerald-400 mt-1 flex items-center space-x-1.5">
                    <PlusCircle className="w-5 h-5 text-emerald-500" />
                    <span>+{diffData.added_count}</span>
                  </div>
                </div>

                <div className="bg-slate-950/60 border border-slate-800 rounded-xl p-4">
                  <span className="text-xs text-slate-500 uppercase font-semibold">Removed Components</span>
                  <div className="text-2xl font-bold text-rose-400 mt-1 flex items-center space-x-1.5">
                    <MinusCircle className="w-5 h-5 text-rose-500" />
                    <span>-{diffData.removed_count}</span>
                  </div>
                </div>

                <div className="bg-slate-950/60 border border-slate-800 rounded-xl p-4">
                  <span className="text-xs text-slate-500 uppercase font-semibold">Version Migrations</span>
                  <div className="text-2xl font-bold text-blue-400 mt-1 flex items-center space-x-1.5">
                    <RefreshCw className="w-5 h-5 text-blue-500" />
                    <span>{diffData.version_changes_count}</span>
                  </div>
                </div>

                <div className="bg-slate-950/60 border border-slate-800 rounded-xl p-4">
                  <span className="text-xs text-slate-500 uppercase font-semibold">Net CVE Delta</span>
                  <div className={`text-2xl font-bold mt-1 flex items-center space-x-1.5 ${diffData.net_vulnerability_delta > 0 ? 'text-amber-400' : 'text-emerald-400'}`}>
                    {diffData.net_vulnerability_delta > 0 ? (
                      <ShieldAlert className="w-5 h-5 text-amber-500" />
                    ) : (
                      <ShieldCheck className="w-5 h-5 text-emerald-500" />
                    )}
                    <span>{diffData.net_vulnerability_delta > 0 ? `+${diffData.net_vulnerability_delta}` : diffData.net_vulnerability_delta}</span>
                  </div>
                </div>
              </div>

              {/* Version Changes List */}
              {diffData.version_changes.length > 0 && (
                <div className="bg-slate-950/60 border border-slate-800 rounded-xl p-5 space-y-3">
                  <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center space-x-2">
                    <RefreshCw className="w-4 h-4 text-blue-400" />
                    <span>Version Upgrades & Downgrades</span>
                  </h3>
                  <div className="divide-y divide-slate-800/60">
                    {diffData.version_changes.map((vc, idx) => (
                      <div key={idx} className="py-2.5 flex items-center justify-between text-xs">
                        <div className="flex items-center space-x-2">
                          <span className="font-semibold text-white">{vc.name}</span>
                          <span className="px-1.5 py-0.5 rounded text-[10px] uppercase font-bold bg-slate-800 text-slate-400">
                            {vc.ecosystem}
                          </span>
                        </div>
                        <div className="flex items-center space-x-3">
                          <span className="text-slate-400 font-mono">{vc.old_version || 'unpinned'}</span>
                          <ArrowRight className="w-3.5 h-3.5 text-slate-600" />
                          <span className="text-white font-mono font-bold">{vc.new_version}</span>
                          <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                            vc.change_type === 'UPGRADE' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                          }`}>
                            {vc.change_type}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Added Components */}
              {diffData.added_components.length > 0 && (
                <div className="bg-slate-950/60 border border-slate-800 rounded-xl p-5 space-y-3">
                  <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center space-x-2">
                    <PlusCircle className="w-4 h-4 text-emerald-400" />
                    <span>Newly Added Dependencies ({diffData.added_components.length})</span>
                  </h3>
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2.5">
                    {diffData.added_components.map((comp, idx) => (
                      <div key={idx} className="p-2.5 bg-slate-900/80 border border-emerald-500/20 rounded-lg flex items-center justify-between text-xs">
                        <span className="font-medium text-emerald-300 truncate mr-2">{comp.name}</span>
                        <span className="text-slate-400 font-mono text-[11px]">{comp.version || '*'}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Resolved / New Vulnerabilities */}
              {diffData.new_vulnerabilities.length > 0 && (
                <div className="bg-rose-950/20 border border-rose-500/30 rounded-xl p-5 space-y-3">
                  <h3 className="text-xs font-bold text-rose-400 uppercase tracking-wider flex items-center space-x-2">
                    <ShieldAlert className="w-4 h-4 text-rose-400" />
                    <span>New Vulnerabilities Introduced ({diffData.new_vulnerabilities.length})</span>
                  </h3>
                  <div className="space-y-2">
                    {diffData.new_vulnerabilities.map((v, idx) => (
                      <div key={idx} className="p-3 bg-slate-900/90 border border-rose-500/30 rounded-lg flex items-center justify-between text-xs">
                        <div>
                          <div className="flex items-center space-x-2">
                            <span className="font-bold text-white">{v.cve_id}</span>
                            <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-rose-500/20 text-rose-300 border border-rose-500/30">
                              CVSS {v.cvss_v3_score} · {v.severity}
                            </span>
                            {v.cisa_kev && (
                              <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30">
                                CISA KEV
                              </span>
                            )}
                          </div>
                          <p className="text-slate-400 text-xs mt-1">{v.summary}</p>
                        </div>
                        {v.remediation_version && (
                          <div className="text-right">
                            <span className="text-[10px] text-slate-500 block">Recommended Fix</span>
                            <span className="text-xs font-mono font-bold text-emerald-400">{v.remediation_version}</span>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="py-20 text-center text-slate-500 text-sm">
              Select two projects above to calculate the dependency drift.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
