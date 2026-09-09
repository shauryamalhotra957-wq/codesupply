"use client";

import { useState, useEffect, useMemo } from 'react';
import { api } from '@/lib/api';
import { GraphData } from '@/types';
import { ReactFlow, Controls, Background, MiniMap, useNodesState, useEdgesState, MarkerType } from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { Skeleton } from '@/components/ui/skeleton';
import { EmptyState } from '@/components/shared/empty-state';
import { Network } from 'lucide-react';

export default function GraphPage({ params }: { params: { id: string } }) {
  const [data, setData] = useState<GraphData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [nodes, setNodes, onNodesChange] = useNodesState<any>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<any>([]);

  useEffect(() => {
    setIsLoading(true);
    api.getGraph(params.id)
      .then(res => {
        setData(res);
        // Extremely simple layout (random scatter or grid) since dagre is not installed
        const newNodes = res.nodes.map((n, i) => {
           // simple grid layout
           const cols = Math.ceil(Math.sqrt(res.nodes.length));
           const x = (i % cols) * 200;
           const y = Math.floor(i / cols) * 100;
           return {
             id: n.id,
             position: { x, y },
             data: { label: `${n.name}\n${n.version || '?'}` },
             style: {
               border: n.risk_level === 'critical' || n.risk_level === 'high' ? '2px solid red' : '1px solid #ccc',
               borderRadius: '5px',
               padding: '10px',
               background: '#fff',
               fontSize: '12px',
               fontFamily: 'monospace'
             }
           };
        });
        const newEdges = res.edges.map(e => ({
          id: e.id,
          source: e.source,
          target: e.target,
          markerEnd: { type: MarkerType.ArrowClosed },
          style: { stroke: '#999' }
        }));
        setNodes(newNodes);
        setEdges(newEdges);
      })
      .catch(console.error)
      .finally(() => setIsLoading(false));
  }, [params.id, setEdges, setNodes]);

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
    <div className="h-full w-full relative flex flex-col">
      <div className="absolute top-4 left-4 z-10 bg-background/80 backdrop-blur-sm p-2 rounded-md border text-sm shadow-sm pointer-events-none">
        {data.total_nodes} nodes • {data.total_edges} edges
        {data.truncated && " (Truncated)"}
      </div>
      <div className="flex-1 bg-muted/10">
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
      </div>
    </div>
  );
}
