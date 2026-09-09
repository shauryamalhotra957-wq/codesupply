"use client";

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { SBOMData } from '@/types';
import { Skeleton } from '@/components/ui/skeleton';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Download, Copy, CheckCircle2, XCircle } from 'lucide-react';
import { ScrollArea } from '@/components/ui/scroll-area';

export default function SBOMPage({ params }: { params: { id: string } }) {
  const [sbom, setSbom] = useState<SBOMData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [showRaw, setShowRaw] = useState(true);

  useEffect(() => {
    setIsLoading(true);
    api.getSBOM(params.id)
      .then(setSbom)
      .catch(console.error)
      .finally(() => setIsLoading(false));
  }, [params.id]);

  const handleDownload = async () => {
    try {
      const blob = await api.downloadSBOM(params.id);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `sbom-${params.id.substring(0,8)}.json`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error(err);
    }
  };

  const handleCopy = () => {
    if (sbom?.content) {
      navigator.clipboard.writeText(JSON.stringify(sbom.content, null, 2));
    }
  };

  if (isLoading) {
    return (
      <div className="p-6 space-y-6 h-full flex flex-col">
        <Skeleton className="h-32 w-full" />
        <Skeleton className="flex-1 w-full" />
      </div>
    );
  }

  if (!sbom) return null;

  return (
    <div className="p-6 h-full flex flex-col gap-6">
      <Card>
        <CardContent className="p-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="space-y-2">
            <div className="flex items-center gap-3">
              <Badge className="bg-[#0070B8] text-white">CycloneDX</Badge>
              <span className="font-mono text-sm text-muted-foreground">v{sbom.spec_version}</span>
            </div>
            <div className="flex items-center gap-2 mt-2">
              {sbom.is_valid ? (
                <CheckCircle2 className="h-5 w-5 text-green-500" />
              ) : (
                <XCircle className="h-5 w-5 text-destructive" />
              )}
              <span className="font-medium">
                {sbom.is_valid ? 'Valid SBOM' : 'Validation Failed'}
              </span>
            </div>
            <p className="text-sm text-muted-foreground">
              {sbom.component_count} components • {sbom.relationship_count} relationships
            </p>
          </div>
          
          <div className="flex gap-2">
            <Button variant="outline" onClick={handleCopy}>
              <Copy className="h-4 w-4 mr-2" /> Copy JSON
            </Button>
            <Button onClick={handleDownload}>
              <Download className="h-4 w-4 mr-2" /> Download
            </Button>
          </div>
        </CardContent>
      </Card>

      {!sbom.is_valid && sbom.validation_errors && sbom.validation_errors.length > 0 && (
        <Card className="border-destructive/50 bg-destructive/5">
          <CardContent className="p-4">
            <h3 className="font-semibold text-destructive flex items-center gap-2 mb-2">
              <XCircle className="h-4 w-4" /> Validation Errors
            </h3>
            <ul className="list-disc pl-5 text-sm space-y-1">
              {sbom.validation_errors.map((err, i) => (
                <li key={i}>{err}</li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

      <Card className="flex-1 flex flex-col min-h-[400px]">
        <div className="flex justify-between items-center p-4 border-b">
          <h3 className="font-semibold">Raw Source</h3>
        </div>
        <ScrollArea className="flex-1 bg-[#1e1e1e] text-[#d4d4d4] rounded-b-lg">
          <pre className="p-4 text-xs font-mono">
            {JSON.stringify(sbom.content, null, 2)}
          </pre>
        </ScrollArea>
      </Card>
    </div>
  );
}
