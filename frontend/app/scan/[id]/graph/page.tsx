"use client";

import { useState, useEffect, useMemo } from 'react';
import { api } from '@/lib/api';
import { GraphData } from '@/types';
import dagre from '@dagrejs/dagre';
import { ReactFlow, Controls, Background, MiniMap, useNodesState, useEdgesState, MarkerType, ReactFlowProvider, useReactFlow } from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { Skeleton } from '@/components/ui/skeleton';
import { EmptyState } from '@/components/shared/empty-state';
import { Network, Search, Maximize } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';

const getLayoutedElements = (nodes: any[], edges: any[], direction = 'TB') => {
  const dagreGraph = new dagre.graphlib.Graph();
  dagreGraph.setDefaultEdgeLabel(() => ({}));
  
  const nodeWidth = 180;
  const nodeHeight = 50;

  dagreGraph.setGraph({ rankdir: direction });

  nodes.forEach((node) => {
    dagreGraph.setNode(node.id, { width: nodeWidth, height: nodeHeight });
  });

  edges.forEach((edge) => {
    dagreGraph.setEdge(edge.source, edge.target);
  });

  dagre.layout(dagreGraph);

  nodes.forEach((node) => {
    const nodeWithPosition = dagreGraph.node(node.id);
    node.targetPosition = direction === 'TB' ? 'top' : 'left';
    node.sourcePosition = direction === 'TB' ? 'bottom' : 'right';
    node.position = {
      x: nodeWithPosition.x - nodeWidth / 2,
      y: nodeWithPosition.y - nodeHeight / 2,
    };
    return node;
  });

  return { nodes, edges };
};

function FlowContent({ 
  data, 
  nodes, 
  edges, 
  onNodesChange, 
  onEdgesChange 
}: any) {
  const { fitView } = useReactFlow();
  
  return (
    <>
      <div className="absolute top-4 left-4 z-10 bg-background/80 backdrop-blur-sm p-2 rounded-md border text-sm shadow-sm pointer-events-none">
        {data.total_nodes} nodes • {data.total_edges} edges
        {data.truncated && " (Truncated)"}
      </div>
      <div className="absolute top-4 right-4 z-10 flex gap-2 items-center">
        <Button variant="secondary" size="sm" onClick={() => fitView()}>
          <Maximize className="w-4 h-4 mr-2" />
          Fit to View
        </Button>
      </div>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        fitView
        minZoom={0.1}
      >
        <Background />
        <Controls />
        <MiniMap />
      </ReactFlow>
    </>
  );
}

export default function GraphPage({ params }: { params: { id: string } }) {
  const [data, setData] = useState<GraphData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [nodes, setNodes, onNodesChange] = useNodesState<any>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<any>([]);
  
  const [showDirectOnly, setShowDirectOnly] = useState(false);
  const [showRiskyOnly, setShowRiskyOnly] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");

  useEffect(() => {
    setIsLoading(true);
    api.getGraph(params.id)
      .then(res => {
        setData(res);
      })
      .catch(console.error)
      .finally(() => setIsLoading(false));
  }, [params.id]);

  useEffect(() => {
    if (!data) return;

    let filteredNodes = data.nodes;
    let filteredEdges = data.edges;

    if (showDirectOnly) {
      filteredNodes = filteredNodes.filter(n => n.dependency_type === 'direct');
      const nodeIds = new Set(filteredNodes.map(n => n.id));
      filteredEdges = filteredEdges.filter(e => nodeIds.has(e.source) && nodeIds.has(e.target));
    }

    if (showRiskyOnly) {
      filteredNodes = filteredNodes.filter(n => n.risk_level !== 'none' && n.risk_level !== 'low');
      const nodeIds = new Set(filteredNodes.map(n => n.id));
      filteredEdges = filteredEdges.filter(e => nodeIds.has(e.source) && nodeIds.has(e.target));
    }

    const newNodes = filteredNodes.map((n) => {
      const isHighlighted = searchQuery && n.name.toLowerCase().includes(searchQuery.toLowerCase());
      const opacity = searchQuery && !isHighlighted ? 0.2 : 1;
      
      return {
        id: n.id,
        position: { x: 0, y: 0 },
        data: { label: `${n.name}\n${n.version || '?'}${n.ecosystem ? ` (${n.ecosystem})` : ''}` },
        style: {
          opacity,
          border: n.risk_level === 'critical' 
            ? '1.5px solid rgba(239, 68, 68, 0.8)' 
            : n.risk_level === 'high' 
            ? '1.5px solid rgba(249, 115, 22, 0.8)' 
            : n.risk_level === 'medium'
            ? '1.5px solid rgba(245, 158, 11, 0.8)'
            : '1px solid rgba(255, 255, 255, 0.15)',
          borderRadius: '10px',
          padding: '10px 14px',
          background: 'rgba(15, 17, 26, 0.9)',
          color: '#f8fafc',
          fontSize: '12px',
          fontFamily: 'monospace',
          boxShadow: n.risk_level === 'critical' 
            ? '0 0 15px rgba(239, 68, 68, 0.25)' 
            : '0 4px 12px rgba(0, 0, 0, 0.4)',
          width: 180,
          cursor: 'pointer'
        }
      };
    });

    const newEdges = filteredEdges.map(e => ({
      id: e.id,
      source: e.source,
      target: e.target,
      markerEnd: { type: MarkerType.ArrowClosed },
      style: { stroke: 'rgba(148, 163, 184, 0.35)', strokeWidth: 1.5 }
    }));

    const { nodes: layoutedNodes, edges: layoutedEdges } = getLayoutedElements(newNodes, newEdges);
    setNodes(layoutedNodes);
    setEdges(layoutedEdges);

  }, [data, showDirectOnly, showRiskyOnly, searchQuery, setNodes, setEdges]);

  if (isLoading) {
    return <div className="p-6 h-full"><Skeleton className="h-full w-full rounded-xl" /></div>;
  }

  if (!data || data.nodes.length === 0) {
    return (
      <div className="h-full flex items-center justify-center p-6">
        <EmptyState 
          icon={Network}
          title="Dependency graph unavailable"
          description="The available project metadata does not contain enough relationship information."
        />
      </div>
    );
  }

  return (
    <div className="h-full w-full flex flex-col">
      <div className="border-b p-4 flex flex-col sm:flex-row gap-4 justify-between items-center bg-card">
        <div className="relative w-full max-w-sm">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Find in graph..."
            className="pl-9"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
        <div className="flex gap-6 items-center">
          <div className="flex items-center space-x-2">
            <input 
              type="checkbox" 
              id="direct-only" 
              checked={showDirectOnly} 
              onChange={(e) => setShowDirectOnly(e.target.checked)} 
              className="h-4 w-4 rounded border-gray-300"
            />
            <Label htmlFor="direct-only">Direct Only</Label>
          </div>
          <div className="flex items-center space-x-2">
            <input 
              type="checkbox" 
              id="risky-only" 
              checked={showRiskyOnly} 
              onChange={(e) => setShowRiskyOnly(e.target.checked)} 
              className="h-4 w-4 rounded border-gray-300"
            />
            <Label htmlFor="risky-only">Risky Only</Label>
          </div>
        </div>
      </div>
      <div className="flex-1 bg-muted/10 relative">
        <ReactFlowProvider>
          <FlowContent 
            data={data} 
            nodes={nodes} 
            edges={edges} 
            onNodesChange={onNodesChange} 
            onEdgesChange={onEdgesChange} 
          />
        </ReactFlowProvider>
      </div>
    </div>
  );
}
