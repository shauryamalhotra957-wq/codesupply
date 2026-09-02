import React, { useState, useMemo } from 'react';
import { 
  Search, 
  Filter, 
  Layers, 
  Boxes, 
  FileCode2, 
  AlertTriangle, 
  CheckCircle2, 
  ChevronRight, 
  Download,
  Copy,
  Check
} from 'lucide-react';

export default function ComponentsTableView({ 
  components, 
  findings, 
  onSelectComponent 
}) {
  const [search, setSearch] = useState('');
  const [ecoFilter, setEcoFilter] = useState('all');
  const [typeFilter, setTypeFilter] = useState('all');
  const [pinnedFilter, setPinnedFilter] = useState('all');
  const [copiedPurl, setCopiedPurl] = useState(null);

  const findingsMap = useMemo(() => {
    const map = {};
    for (const f of findings) {
      const key = f.component_name?.toLowerCase();
      map[key] = (map[key] || 0) + 1;
    }
    return map;
  }, [findings]);

  const filteredComponents = useMemo(() => {
    return components.filter(c => {
      const searchMatch = !search || 
        c.name.toLowerCase().includes(search.toLowerCase()) ||
        (c.version && c.version.toLowerCase().includes(search.toLowerCase())) ||
        (c.source_file && c.source_file.toLowerCase().includes(search.toLowerCase()));

      const ecoMatch = ecoFilter === 'all' || c.ecosystem === ecoFilter;
      
      let typeMatch = true;
      if (typeFilter === 'direct') typeMatch = c.direct === true;
      if (typeFilter === 'transitive') typeMatch = c.direct === false;

      let pinMatch = true;
      const isPinned = c.version && !['unpinned', 'unspecified', ''].includes(c.version);
      if (pinnedFilter === 'pinned') pinMatch = isPinned;
      if (pinnedFilter === 'unpinned') pinMatch = !isPinned;

      return searchMatch && ecoMatch && typeMatch && pinMatch;
    });
  }, [components, search, ecoFilter, typeFilter, pinnedFilter]);

  const handleCopy = (e, purl) => {
    e.stopPropagation();
    navigator.clipboard.writeText(purl);
    setCopiedPurl(purl);
    setTimeout(() => setCopiedPurl(null), 1500);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">Component Inventory</h1>
          <p className="text-xs text-slate-400">
            Showing {filteredComponents.length} of {components.length} normalized components & sub-dependencies
          </p>
        </div>
      </div>

      {/* Filter and Search Toolbar */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-col md:flex-row items-stretch md:items-center justify-between gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by package name, version, or manifest..."
            className="w-full bg-slate-800 border border-slate-700 rounded-lg pl-9 pr-4 py-2 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>

        <div className="flex flex-wrap items-center gap-2">
          {/* Ecosystem Filter */}
          <select
            value={ecoFilter}
            onChange={(e) => setEcoFilter(e.target.value)}
            className="bg-slate-800 border border-slate-700 text-slate-200 text-xs rounded-lg px-3 py-2 focus:outline-none"
          >
            <option value="all">All Ecosystems</option>
            <option value="pypi">PyPI (Python)</option>
            <option value="npm">NPM (Node.js)</option>
          </select>

          {/* Type Filter */}
          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            className="bg-slate-800 border border-slate-700 text-slate-200 text-xs rounded-lg px-3 py-2 focus:outline-none"
          >
            <option value="all">All Types</option>
            <option value="direct">Direct Only</option>
            <option value="transitive">Transitive Only</option>
          </select>

          {/* Pinning Filter */}
          <select
            value={pinnedFilter}
            onChange={(e) => setPinnedFilter(e.target.value)}
            className="bg-slate-800 border border-slate-700 text-slate-200 text-xs rounded-lg px-3 py-2 focus:outline-none"
          >
            <option value="all">All Versions</option>
            <option value="pinned">Pinned Versions</option>
            <option value="unpinned">Unpinned (Risky)</option>
          </select>
        </div>
      </div>

      {/* Components Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="bg-slate-950/80 border-b border-slate-800 text-slate-400 uppercase tracking-wider font-semibold">
                <th className="py-3.5 px-4">Component</th>
                <th className="py-3.5 px-4">Version</th>
                <th className="py-3.5 px-4">Ecosystem</th>
                <th className="py-3.5 px-4">Relation</th>
                <th className="py-3.5 px-4">Source Manifest</th>
                <th className="py-3.5 px-4">Package URL (PURL)</th>
                <th className="py-3.5 px-4 text-center">Status</th>
                <th className="py-3.5 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {filteredComponents.length === 0 ? (
                <tr>
                  <td colSpan={8} className="text-center py-10 text-slate-500">
                    No components match your search and filter criteria.
                  </td>
                </tr>
              ) : (
                filteredComponents.map((comp) => {
                  const hasRisks = (findingsMap[comp.name.toLowerCase()] || 0) > 0;
                  const isPinned = comp.version && !['unpinned', 'unspecified', ''].includes(comp.version);

                  return (
                    <tr
                      key={comp.purl}
                      onClick={() => onSelectComponent(comp)}
                      className="hover:bg-slate-800/50 cursor-pointer transition group"
                    >
                      {/* Name */}
                      <td className="py-3 px-4">
                        <div className="flex items-center space-x-2.5">
                          <div className={`w-7 h-7 rounded-lg flex items-center justify-center shrink-0 ${
                            comp.ecosystem === 'npm' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-blue-500/10 text-blue-400'
                          }`}>
                            {comp.ecosystem === 'npm' ? <Boxes className="w-4 h-4" /> : <FileCode2 className="w-4 h-4" />}
                          </div>
                          <span className="font-bold text-white group-hover:text-indigo-300 transition">
                            {comp.name}
                          </span>
                        </div>
                      </td>

                      {/* Version */}
                      <td className="py-3 px-4">
                        <span className={`font-mono px-2 py-0.5 rounded text-[11px] font-semibold ${
                          isPinned 
                            ? 'bg-slate-800 text-slate-200' 
                            : 'bg-red-500/20 text-red-400 border border-red-500/30'
                        }`}>
                          {comp.version || 'unpinned'}
                        </span>
                      </td>

                      {/* Ecosystem */}
                      <td className="py-3 px-4">
                        <span className={`text-[10px] font-bold px-2 py-0.5 rounded uppercase ${
                          comp.ecosystem === 'npm' ? 'bg-emerald-950/60 text-emerald-400' : 'bg-blue-950/60 text-blue-400'
                        }`}>
                          {comp.ecosystem}
                        </span>
                      </td>

                      {/* Direct / Transitive */}
                      <td className="py-3 px-4">
                        <span className={`text-[10px] font-semibold px-2 py-0.5 rounded ${
                          comp.direct ? 'bg-indigo-500/20 text-indigo-300' : 'bg-slate-800 text-slate-400'
                        }`}>
                          {comp.direct ? 'Direct' : 'Transitive'}
                        </span>
                      </td>

                      {/* Source file */}
                      <td className="py-3 px-4 font-mono text-[11px] text-slate-400 truncate max-w-[150px]">
                        {comp.source_file}
                      </td>

                      {/* PURL */}
                      <td className="py-3 px-4">
                        <div className="flex items-center space-x-1.5 font-mono text-[11px] text-slate-400">
                          <span className="truncate max-w-[200px]">{comp.purl}</span>
                          <button
                            onClick={(e) => handleCopy(e, comp.purl)}
                            className="text-slate-500 hover:text-indigo-300 p-1 transition"
                            title="Copy PURL"
                          >
                            {copiedPurl === comp.purl ? (
                              <Check className="w-3.5 h-3.5 text-emerald-400" />
                            ) : (
                              <Copy className="w-3.5 h-3.5" />
                            )}
                          </button>
                        </div>
                      </td>

                      {/* Status */}
                      <td className="py-3 px-4 text-center">
                        {hasRisks ? (
                          <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded bg-amber-500/20 text-amber-400 text-[10px] font-bold">
                            <AlertTriangle className="w-3 h-3" />
                            <span>Risk Flag</span>
                          </span>
                        ) : (
                          <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 text-[10px]">
                            <CheckCircle2 className="w-3 h-3" />
                            <span>Valid</span>
                          </span>
                        )}
                      </td>

                      {/* Action */}
                      <td className="py-3 px-4 text-right">
                        <ChevronRight className="w-4 h-4 text-slate-500 group-hover:text-indigo-400 inline-block transition-transform group-hover:translate-x-1" />
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
