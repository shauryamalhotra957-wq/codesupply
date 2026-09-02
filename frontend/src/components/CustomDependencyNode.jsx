import React, { memo } from 'react';
import { Handle, Position } from '@xyflow/react';
import { 
  Package, 
  AlertTriangle, 
  Layers, 
  Boxes, 
  Cpu, 
  FileCode2 
} from 'lucide-react';

function CustomDependencyNode({ data, selected }) {
  const isRoot = data.level === 0;
  const isDirect = data.direct;
  const hasFindings = data.has_findings;
  const ecosystem = data.ecosystem || 'pypi';

  if (isRoot) {
    return (
      <div className={`px-4 py-3 rounded-xl shadow-xl border transition-all cursor-pointer bg-gradient-to-br from-indigo-900 via-indigo-950 to-slate-900 ${
        selected ? 'ring-2 ring-indigo-400 border-indigo-400' : 'border-indigo-500/50'
      }`}>
        <Handle type="source" position={Position.Right} className="w-2.5 h-2.5 bg-indigo-400 border-2 border-slate-900" />
        <div className="flex items-center space-x-2.5">
          <div className="w-8 h-8 rounded-lg bg-indigo-600 text-white flex items-center justify-center font-bold">
            <Cpu className="w-4 h-4" />
          </div>
          <div>
            <div className="text-[10px] uppercase font-bold tracking-wider text-indigo-300">Root Application</div>
            <div className="text-sm font-extrabold text-white">{data.label}</div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`px-3.5 py-2.5 rounded-xl shadow-lg border transition-all cursor-pointer min-w-[200px] ${
      selected 
        ? 'ring-2 ring-indigo-400 border-indigo-400 bg-slate-800' 
        : hasFindings 
        ? 'border-amber-500/60 bg-slate-900 hover:border-amber-400' 
        : isDirect 
        ? 'border-slate-700 bg-slate-900 hover:border-indigo-500' 
        : 'border-slate-800 bg-slate-900/80 hover:border-slate-600 opacity-90'
    }`}>
      {/* Target handle on left */}
      <Handle type="target" position={Position.Left} className="w-2 h-2 bg-indigo-400 border-2 border-slate-900" />

      {/* Source handle on right */}
      <Handle type="source" position={Position.Right} className="w-2 h-2 bg-indigo-400 border-2 border-slate-900" />

      <div className="flex items-start justify-between gap-2">
        <div className="flex items-center space-x-2 truncate">
          <div className={`w-6 h-6 rounded-md flex items-center justify-center shrink-0 text-xs ${
            ecosystem === 'npm' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-blue-500/10 text-blue-400'
          }`}>
            {ecosystem === 'npm' ? <Boxes className="w-3.5 h-3.5" /> : <FileCode2 className="w-3.5 h-3.5" />}
          </div>
          <div className="truncate">
            <div className="text-xs font-bold text-white truncate max-w-[130px]">{data.name}</div>
            <div className="text-[10px] font-mono text-slate-400">{data.version || 'unpinned'}</div>
          </div>
        </div>

        {hasFindings && (
          <div className="shrink-0 flex items-center space-x-1 px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-400 text-[10px] font-bold border border-amber-500/30">
            <AlertTriangle className="w-3 h-3" />
            <span>{data.findings_count}</span>
          </div>
        )}
      </div>

      <div className="mt-2 pt-2 border-t border-slate-800 flex items-center justify-between text-[10px] text-slate-400">
        <span className={`px-1.5 py-0.2 rounded font-semibold ${
          isDirect ? 'bg-indigo-500/20 text-indigo-300' : 'bg-slate-800 text-slate-400'
        }`}>
          {isDirect ? 'Direct' : 'Transitive'}
        </span>
        <span className="font-mono text-[9px] text-slate-500 uppercase">{ecosystem}</span>
      </div>
    </div>
  );
}

export default memo(CustomDependencyNode);
