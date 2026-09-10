"use client";

import { useState, useRef, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Upload, FileArchive, ArrowRight, ShieldCheck, FileJson, Activity, Globe, Zap, CheckCircle } from 'lucide-react';
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
  
  // Animation state for stats
  const [stats, setStats] = useState({ ecosystems: 0, speed: 0 });

  useEffect(() => {
    const timer = setTimeout(() => {
      setStats({ ecosystems: 5, speed: 100 });
    }, 500);
    return () => clearTimeout(timer);
  }, []);

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
        
        <main className="flex-1 overflow-auto relative">
          {/* Subtle gradient background hero section */}
          <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-background to-secondary/20 pointer-events-none -z-10" />
          
          <div className="flex flex-col items-center justify-center p-6 lg:p-12 min-h-full">
            <div className="max-w-4xl w-full space-y-12 animate-fade-in-up">
              
              <div className="text-center space-y-6">
                <h1 className="text-4xl lg:text-6xl font-extrabold tracking-tight">
                  Understand your <span className="text-gradient">software supply chain.</span>
                </h1>
                <p className="text-xl text-muted-foreground max-w-2xl mx-auto leading-relaxed">
                  Upload a project. Map its dependencies. Find known risk. Generate a standards-based SBOM.
                </p>
                
                {/* Animated stats counter */}
                <div className="flex justify-center gap-8 pt-4">
                  <div className="flex items-center gap-2">
                    <Globe className="h-5 w-5 text-primary" />
                    <span className="font-semibold">{stats.ecosystems} Ecosystems</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Zap className="h-5 w-5 text-primary" />
                    <span className="font-semibold">Real-time OSV</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <CheckCircle className="h-5 w-5 text-primary" />
                    <span className="font-semibold">CycloneDX 1.7</span>
                  </div>
                </div>
              </div>

              <Card className="border-2 overflow-hidden shadow-xl hover:shadow-2xl transition-shadow duration-300 bg-background/50 backdrop-blur-sm">
                <CardContent className="p-0">
                  <div 
                    className={`
                      p-16 flex flex-col items-center justify-center text-center transition-all duration-300 border-dashed border-2 m-4 rounded-xl group
                      ${isDragging ? 'border-primary bg-primary/10 scale-[1.02] shadow-inner' : 'border-border/50 bg-muted/20 hover:border-primary/50 hover:bg-muted/40'}
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
                    
                    <div className="h-24 w-24 rounded-full bg-background shadow-md flex items-center justify-center mb-8 group-hover:scale-110 transition-transform duration-300">
                      {isUploading ? (
                        <Upload className="h-10 w-10 text-primary animate-bounce" />
                      ) : (
                        <FileArchive className="h-10 w-10 text-muted-foreground group-hover:text-primary transition-colors" />
                      )}
                    </div>
                    
                    <h3 className="text-3xl font-bold mb-3">
                      {isUploading ? "Processing project..." : "Drop ZIP here"}
                    </h3>
                    
                    {!isUploading && (
                      <>
                        <p className="text-lg text-muted-foreground mb-8">
                          or click to browse your files
                        </p>
                        
                        <Button size="lg" className="mb-6 font-semibold shadow-lg hover:shadow-primary/25 transition-all" onClick={(e) => { e.stopPropagation(); fileInputRef.current?.click(); }}>
                          Choose File
                        </Button>
                        
                        <div className="flex flex-col items-center gap-2">
                          <p className="text-sm font-medium text-muted-foreground">
                            Supported: npm · Python · Maven · Go · Rust
                          </p>
                          <p className="text-xs text-muted-foreground/70">
                            Maximum archive size: 100 MB
                          </p>
                        </div>
                      </>
                    )}
                    
                    {error && (
                      <div className="mt-6 p-4 bg-destructive/10 text-destructive rounded-lg text-sm font-medium max-w-md w-full border border-destructive/20 animate-in fade-in zoom-in-95">
                        {error}
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>

              <div className="text-center pb-4">
                <Button variant="ghost" size="lg" className="text-muted-foreground hover:text-foreground group font-medium" onClick={handleSampleScan} disabled={isUploading}>
                  Try sample project
                  <ArrowRight className="ml-2 h-5 w-5 group-hover:translate-x-1.5 transition-transform" />
                </Button>
              </div>

              <div className="grid md:grid-cols-3 gap-8 pt-10 border-t border-border/50">
                <div className="space-y-4 hover:-translate-y-1 transition-transform duration-300">
                  <div className="h-12 w-12 rounded-xl bg-primary/10 flex items-center justify-center shadow-sm">
                    <ShieldCheck className="h-6 w-6 text-primary" />
                  </div>
                  <h3 className="font-bold text-xl">Evidence-backed analysis</h3>
                  <p className="text-muted-foreground leading-relaxed">
                    Every component is traced back to a specific file and line of code, providing undeniable proof of its presence.
                  </p>
                </div>
                <div className="space-y-4 hover:-translate-y-1 transition-transform duration-300">
                  <div className="h-12 w-12 rounded-xl bg-primary/10 flex items-center justify-center shadow-sm">
                    <Activity className="h-6 w-6 text-primary" />
                  </div>
                  <h3 className="font-bold text-xl">Honest uncertainty</h3>
                  <p className="text-muted-foreground leading-relaxed">
                    We do not guess. If a version cannot be conclusively resolved, we mark it as unknown rather than providing false confidence.
                  </p>
                </div>
                <div className="space-y-4 hover:-translate-y-1 transition-transform duration-300">
                  <div className="h-12 w-12 rounded-xl bg-primary/10 flex items-center justify-center shadow-sm">
                    <FileJson className="h-6 w-6 text-primary" />
                  </div>
                  <h3 className="font-bold text-xl">Standards-based output</h3>
                  <p className="text-muted-foreground leading-relaxed">
                    Export valid CycloneDX 1.6/1.7 SBOMs that integrate seamlessly with your existing security tools and compliance workflows.
                  </p>
                </div>
              </div>
              
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
