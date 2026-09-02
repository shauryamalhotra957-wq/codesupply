import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { 
  ReactFlow, 
  Background, 
  Controls, 
  MiniMap, 
  useNodesState, 
  useEdgesState 
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import CustomDependencyNode from './CustomDependencyNode';
import { 
  Search, 
  Filter, 
  Layers, 
  ZoomIn, 
  AlertTriangle, 
  Boxes, 
  FileCode2, 
  Sparkles,
  RefreshCw
} from 'lucide-react';

const nodeTypes = {
  customDependencyNode: CustomDependencyNode,
};

export default function DependencyGraphView({ 
  graphData, 
  components, 
  onSelectComponent 
}) {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [ecosystemFilter, setEcosystemFilter] = useState('all'); // all, pypi, npm
  const [typeFilter, setTypeFilter] = useState('all'); // all, direct, transitive, risky

  // Initialize or update graph data
  useEffect(() => {
    if (graphData?.react_flow) {
      setNodes(graphData.react_flow.nodes || []);
      setEdges(graphData.react_flow.edges || []);
    }
  }, [graphData, setNodes, setEdges]);

  // Handle node selection
  const handleNodeClick = useCallback((event, node) => {
    if (node.id === 'root:application') return;
    const matchedComp = components.find(
      c => c.purl === node.id || c.name.toLowerCase() === node.data.name?.toLowerCase()
    );
    if (matchedComp) {
      onSelectComponent(matchedComp);
    }
  }, [components, onSelectComponent]);

  // Filtered nodes and edges based on user search and filters
  const filteredNodes = useMemo(() => {
    if (!graphData?.react_flow?.nodes) return [];

    return graphData.react_flow.nodes.map(node => {
      if (node.id === 'root:application') return node;

      const nameMatch = !searchQuery || 
        node.data.name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        node.data.label?.toLowerCase().includes(searchQuery.toLowerCase());

      const ecoMatch = ecosystemFilter === 'all' || node.data.ecosystem === ecosystemFilter;

      let typeMatch = true;
      if (typeFilter === 'direct') typeMatch = node.data.direct === true;
      if (typeFilter === 'transitive') typeMatch = node.data.direct === false;
      if (typeFilter === 'risky') typeMatch = node.data.has_findings === true;

      const isVisible = nameMatch && ecoMatch && typeMatch;

      return {
        ...node,
        style: {
          ...node.style,
          opacity: isVisible ? 1 : 0.15,
          transition: 'opacity 0.2s ease',
        },
      };
    });
  }, [graphData, searchQuery, ecosystemFilter, typeFilter]);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-4">
      {/* Top Filter Bar */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-col md:flex-row items-stretch md:items-center justify-between gap-4">
        {/* Search */}
        <div className="relative flex-1 max-w-md">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search dependency by name or version..."
            className="w-full bg-slate-800 border border-slate-700 rounded-lg pl-9 pr-4 py-2 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>

        {/* Filter Controls */}
        <div className="flex flex-wrap items-center gap-2">
          {/* Ecosystem Filter */}
          <div className="flex items-center bg-slate-800 rounded-lg p-1 border border-slate-700 text-xs">
            <button
              onClick={() => setEcosystemFilter('all')}
              className={`px-2.5 py-1 rounded font-medium transition ${
                ecosystemFilter === 'all' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-white'
              }`}
            >
              All
            </button>
            <button
              onClick={() => setEcosystemFilter('pypi')}
              className={`px-2.5 py-1 rounded font-medium transition ${
                ecosystemFilter === 'pypi' ? 'bg-blue-600 text-white' : 'text-slate-400 hover:text-white'
              }`}
            >
              PyPI
            </button>
            <button
              onClick={() => setEcosystemFilter('npm')}
              className={`px-2.5 py-1 rounded font-medium transition ${
                ecosystemFilter === 'npm' ? 'bg-emerald-600 text-white' : 'text-slate-400 hover:text-white'
              }`}
            >
              NPM
            </button>
          </div>

          {/* Type Filter */}
          <div className="flex items-center bg-slate-800 rounded-lg p-1 border border-slate-700 text-xs">
            <button
              onClick={() => setTypeFilter('all')}
              className={`px-2.5 py-1 rounded font-medium transition ${
                typeFilter === 'all' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-white'
              }`}
            >
              All Types
            </button>
            <button
              onClick={() => setTypeFilter('direct')}
              className={`px-2.5 py-1 rounded font-medium transition ${
                typeFilter === 'direct' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-white'
              }`}
            >
              Direct
            </button>
            <button
              onClick={() => setTypeFilter('transitive')}
              className={`px-2.5 py-1 rounded font-medium transition ${
                typeFilter === 'transitive' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-white'
              }`}
            >
              Transitive
            </button>
            <button
              onClick={() => setTypeFilter('risky')}
              className={`px-2.5 py-1 rounded font-medium flex items-center space-x-1 transition ${
                typeFilter === 'risky' ? 'bg-amber-600 text-white' : 'text-amber-400 hover:text-white'
              }`}
            >
              <AlertTriangle className="w-3 h-3" />
              <span>Risks Only</span>
            </button>
          </div>
        </div>
      </div>

      {/* Canvas Area */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl h-[650px] relative overflow-hidden shadow-2xl">
        <ReactFlow
          nodes={filteredNodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onNodeClick={handleNodeClick}
          nodeTypes={nodeTypes}
          fitView
          fitViewOptions={{ padding: 0.2 }}
          minZoom={0.2}
          maxZoom={2.0}
        >
          <Background color="#334155" gap={20} size={1} />
          <Controls position="top-right" />
          <MiniMap 
            position="bottom-right"
            nodeColor={(node) => {
              if (node.id === 'root:application') return '#6366f1';
              if (node.data?.has_findings) return '#f59e0b';
              if (node.data?.ecosystem === 'npm') return '#10b981';
              return '#3b82f6';
            }}
            maskColor="rgba(15, 23, 42, 0.7)"
            style={{ backgroundColor: '#0f172a', border: '1px solid #334155', borderRadius: '8px' }}
          />
        </ReactFlow>

        {/* Floating Instruction Overlay */}
        <div className="absolute bottom-4 left-4 bg-slate-950/80 backdrop-blur-md border border-slate-800 rounded-xl px-3 py-2 text-[11px] text-slate-400 flex items-center space-x-3 pointer-events-none">
          <div className="flex items-center space-x-1.5">
            <div className="w-2.5 h-2.5 rounded-full bg-blue-500" />
            <span>PyPI</span>
          </div>
          <div className="flex items-center space-x-1.5">
            <div className="w-2.5 h-2.5 rounded-full bg-emerald-500" />
            <span>NPM</span>
          </div>
          <div className="flex items-center space-x-1.5">
            <div className="w-2.5 h-2.5 rounded-full bg-amber-500" />
            <span>Anomaly / Risk</span>
          </div>
          <span className="text-slate-600">|</span>
          <span>Click any node to view details</span>
        </div>
      </div>
    </div>
  );
}
