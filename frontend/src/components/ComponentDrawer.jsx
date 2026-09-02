import React, { useState } from 'react';
import { 
  X, 
  Copy, 
  Check, 
  ExternalLink, 
  ShieldAlert, 
  FileCode2, 
  Boxes, 
  Layers, 
  GitFork, 
  CheckCircle2,
  FileCheck 
} from 'lucide-react';

export default function ComponentDrawer({ 
  component, 
  findings, 
  onClose, 
  onSelectComponent, 
  allComponents 
}) {
  const [copied, setCopied] = useState(false);

  if (!component) return null;

  const handleCopyPurl = () => {
    navigator.clipboard.writeText(component.purl);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const compFindings = findings.filter(
    f => f.component_name?.toLowerCase() === component.name?.toLowerCase()
  );

  return (
    <div className="fixed inset-y-0 right-0 max-w-lg w-full bg-slate-900 border-l border-slate-800 shadow-2xl z-50 overflow-y-auto flex flex-col">
      {/* Drawer Header */}
      <div className="p-6 border-b border-slate-800 flex items-start justify-between bg-slate-950/50 sticky top-0 backdrop-blur-md z-10">
        <div className="flex items-center space-x-3">
          <div className={`w-10 h-10 rounded-xl flex items-center justify-center font-bold ${
            component.ecosystem === 'npm' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-blue-500/10 text-blue-400 border border-blue-500/20'
          }`}>
            {component.ecosystem === 'npm' ? <Boxes className="w-5 h-5" /> : <FileCode2 className="w-5 h-5" />}
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h2 className="text-lg font-bold text-white">{component.name}</h2>
              <span className={`text-[10px] font-bold px-2 py-0.5 rounded uppercase ${
                component.direct ? 'bg-indigo-500/20 text-indigo-300' : 'bg-slate-800 text-slate-400'
              }`}>
                {component.direct ? 'Direct' : 'Transitive'}
              </span>
            </div>
            <p className="text-xs font-mono text-slate-400">{component.version || 'Unpinned Version'}</p>
          </div>
        </div>

        <button 
          onClick={onClose}
          className="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800 transition"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Drawer Body Content */}
      <div className="p-6 space-y-6 flex-1">
        {/* PURL Box with Copy Button */}
        <div className="bg-slate-950 border border-slate-800 rounded-xl p-4 space-y-2">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span className="font-semibold">Package URL (PURL)</span>
            <button
              onClick={handleCopyPurl}
              className="flex items-center space-x-1 text-indigo-400 hover:text-indigo-300 transition"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
              <span className="text-[11px]">{copied ? 'Copied!' : 'Copy'}</span>
            </button>
          </div>
          <div className="font-mono text-xs text-slate-200 break-all select-all bg-slate-900 p-2.5 rounded-lg border border-slate-800">
            {component.purl}
          </div>
        </div>

        {/* Metadata Details Grid */}
        <div className="grid grid-cols-2 gap-3 text-xs">
          <div className="bg-slate-800/50 p-3 rounded-lg border border-slate-800">
            <span className="text-slate-400 block mb-1">Ecosystem</span>
            <span className="font-semibold text-white uppercase">{component.ecosystem}</span>
          </div>

          <div className="bg-slate-800/50 p-3 rounded-lg border border-slate-800">
            <span className="text-slate-400 block mb-1">Raw Specifier</span>
            <span className="font-mono font-semibold text-white">{component.raw_specifier || component.version || 'None'}</span>
          </div>

          <div className="bg-slate-800/50 p-3 rounded-lg border border-slate-800">
            <span className="text-slate-400 block mb-1">License</span>
            <span className="font-semibold text-white">{component.license || 'Not declared in manifest'}</span>
          </div>

          <div className="bg-slate-800/50 p-3 rounded-lg border border-slate-800">
            <span className="text-slate-400 block mb-1">Scope</span>
            <span className="font-semibold text-white capitalize">{component.scope || 'required'}</span>
          </div>
        </div>

        {/* Manifest Provenance */}
        <div className="space-y-2">
          <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider">Source Provenance</h3>
          <div className="bg-slate-800/40 border border-slate-800 rounded-xl p-3.5 space-y-1.5">
            <div className="text-xs text-slate-400">Declared in manifest:</div>
            <div className="font-mono text-xs text-indigo-300 bg-slate-900/80 px-2.5 py-1.5 rounded border border-slate-800">
              {component.source_file}
            </div>
            {component.source_files && component.source_files.length > 1 && (
              <div className="text-[11px] text-slate-500 pt-1">
                Also referenced in: {component.source_files.filter(f => f !== component.source_file).join(', ')}
              </div>
            )}
          </div>
        </div>

        {/* Integrity Hash if present */}
        {component.integrity && (
          <div className="space-y-2">
            <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider">Integrity Hash</h3>
            <div className="font-mono text-[11px] text-slate-400 bg-slate-950 p-3 rounded-lg border border-slate-800 break-all select-all">
              {component.integrity}
            </div>
          </div>
        )}

        {/* Risk / Anomaly Findings on this Component */}
        <div className="space-y-3">
          <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center space-x-1.5">
            <ShieldAlert className="w-4 h-4 text-red-400" />
            <span>Active Risk Findings ({compFindings.length})</span>
          </h3>

          {compFindings.length === 0 ? (
            <div className="bg-emerald-950/30 border border-emerald-900/50 rounded-xl p-3.5 text-xs text-emerald-300 flex items-center space-x-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
              <span>No known anomalies or pinning risks flagged for this component.</span>
            </div>
          ) : (
            <div className="space-y-3">
              {compFindings.map((f, i) => (
                <div key={i} className="bg-red-950/20 border border-red-900/40 rounded-xl p-4 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-red-200">{f.title}</span>
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-red-500/20 text-red-300">
                      {f.severity}
                    </span>
                  </div>
                  <p className="text-xs text-slate-300">{f.explanation}</p>
                  {f.recommendation && (
                    <div className="pt-2 border-t border-red-900/30 text-xs text-emerald-400 font-medium">
                      <strong>Remediation:</strong> {f.recommendation}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Child Dependencies Tree */}
        {component.dependencies && component.dependencies.length > 0 && (
          <div className="space-y-2">
            <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center space-x-1.5">
              <GitFork className="w-4 h-4 text-indigo-400" />
              <span>Child Sub-Dependencies ({component.dependencies.length})</span>
            </h3>
            <div className="flex flex-wrap gap-1.5">
              {component.dependencies.map((subName, i) => {
                const childObj = allComponents?.find(c => c.name.toLowerCase() === subName.toLowerCase());
                return (
                  <button
                    key={i}
                    onClick={() => childObj && onSelectComponent(childObj)}
                    className="bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white px-2.5 py-1 rounded text-xs font-mono transition border border-slate-700"
                  >
                    {subName} {childObj?.version ? `@${childObj.version}` : ''}
                  </button>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
