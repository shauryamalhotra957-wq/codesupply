"use client";

import { useState, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { Upload, FileArchive, ArrowRight, ShieldCheck, FileJson, Activity } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { api } from '@/lib/api';
import { Sidebar } from '@/components/layout/sidebar';
import { Topbar } from '@/components/layout/topbar';

export default function LandingPage() {
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const router = useRouter();

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleUpload(e.dataTransfer.files[0]);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      handleUpload(e.target.files[0]);
    }
  };

  const handleUpload = async (file: File) => {
    setError(null);
    setIsUploading(true);
    try {
      if (file.size > 100 * 1024 * 1024) {
        throw new Error("This archive exceeds the 100 MB upload limit.");
      }
      const scan = await api.uploadScan(file);
      router.push(`/scan/${scan.id}`);
    } catch (err: any) {
      setError(err.message || "Failed to upload file");
      setIsUploading(false);
    }
  };

  const handleSampleScan = async () => {
    setError(null);
    setIsUploading(true);
    try {
      const scan = await api.createSampleScan();
      router.push(`/scan/${scan.id}`);
    } catch (err: any) {
      setError(err.message || "Failed to create sample scan");
      setIsUploading(false);
    }
  };

  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar />
      <div className="flex-1 flex flex-col lg:pl-64">
        <Topbar />
        
        <main className="flex-1 overflow-auto flex flex-col items-center justify-center p-6 lg:p-12">
          <div className="max-w-4xl w-full space-y-12 animate-in fade-in slide-in-from-bottom-4 duration-500">
            
            <div className="text-center space-y-4">
              <h1 className="text-4xl lg:text-5xl font-bold tracking-tight">
                Understand your software supply chain.
              </h1>
              <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
                Upload a project. Map its dependencies. Find known risk. Generate a standards-based SBOM.
              </p>
            </div>

            <Card className="border-2 overflow-hidden shadow-lg">
              <CardContent className="p-0">
                <div 
                  className={`
                    p-12 flex flex-col items-center justify-center text-center transition-all duration-200 border-dashed border-2 m-4 rounded-xl
                    ${isDragging ? 'border-primary bg-primary/5 scale-[1.02]' : 'border-border bg-muted/30'}
                    ${isUploading ? 'opacity-50 pointer-events-none' : 'cursor-pointer'}
                  `}
                  onDragOver={handleDragOver}
                  onDragLeave={handleDragLeave}
                  onDrop={handleDrop}
                  onClick={() => !isUploading && fileInputRef.current?.click()}
                >
                  <input 
                    type="file" 
                    ref={fileInputRef} 
                    className="hidden" 
                    accept=".zip,.tar.gz,.tgz" 
                    onChange={handleFileSelect}
                  />
                  
                  <div className="h-20 w-20 rounded-full bg-background shadow-sm flex items-center justify-center mb-6">
                    {isUploading ? (
                      <Upload className="h-8 w-8 text-primary animate-bounce" />
                    ) : (
                      <FileArchive className="h-8 w-8 text-muted-foreground" />
                    )}
                  </div>
                  
                  <h3 className="text-2xl font-semibold mb-2">
                    {isUploading ? "Uploading project..." : "Drop ZIP here"}
                  </h3>
                  
                  {!isUploading && (
                    <>
                      <p className="text-muted-foreground mb-6">
                        or click to choose a file
                      </p>
                      
                      <Button className="mb-4" onClick={(e) => { e.stopPropagation(); fileInputRef.current?.click(); }}>
                        Choose file
                      </Button>
                      
                      <p className="text-xs text-muted-foreground">
                        Maximum archive size: 100 MB • Supported: npm · Python · Maven
                      </p>
                    </>
                  )}
                  
                  {error && (
                    <div className="mt-4 p-3 bg-destructive/10 text-destructive rounded-md text-sm max-w-md w-full">
                      {error}
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            <div className="text-center">
              <Button variant="ghost" className="text-muted-foreground hover:text-foreground group" onClick={handleSampleScan} disabled={isUploading}>
                Try sample project
                <ArrowRight className="ml-2 h-4 w-4 group-hover:translate-x-1 transition-transform" />
              </Button>
            </div>

            <div className="grid md:grid-cols-3 gap-6 pt-8 border-t">
              <div className="space-y-3">
                <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center">
                  <ShieldCheck className="h-5 w-5 text-primary" />
                </div>
                <h3 className="font-semibold text-lg">Evidence-backed analysis</h3>
                <p className="text-sm text-muted-foreground">
                  Every component is traced back to a specific file and line of code, providing undeniable proof of its presence.
                </p>
              </div>
              <div className="space-y-3">
                <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center">
                  <Activity className="h-5 w-5 text-primary" />
                </div>
                <h3 className="font-semibold text-lg">Honest uncertainty</h3>
                <p className="text-sm text-muted-foreground">
                  We do not guess. If a version cannot be conclusively resolved, we mark it as unknown rather than providing false confidence.
                </p>
              </div>
              <div className="space-y-3">
                <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center">
                  <FileJson className="h-5 w-5 text-primary" />
                </div>
                <h3 className="font-semibold text-lg">Standards-based output</h3>
                <p className="text-sm text-muted-foreground">
                  Export valid CycloneDX 1.6/1.7 SBOMs that integrate seamlessly with your existing security tools and compliance workflows.
                </p>
              </div>
            </div>
            
          </div>
        </main>
      </div>
    </div>
  );
}
