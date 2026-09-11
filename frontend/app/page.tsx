"use client";

import { useState, useRef, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { 
  Upload, 
  FileArchive, 
  ArrowRight, 
  ShieldCheck, 
  FileJson, 
  Activity, 
  Globe, 
  Zap, 
  CheckCircle2, 
  Sparkles,
  Layers,
  Search,
  Lock
} from 'lucide-react';
import { Button } from '@/components/ui/button';
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
    <div className="flex min-h-screen bg-background relative overflow-hidden selection:bg-purple-500/20">
      {/* Wispr Flow Atmospheric Ambient Glow */}
      <div className="fixed top-0 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-gradient-to-b from-purple-600/15 via-blue-600/10 to-transparent blur-3xl pointer-events-none -z-10 rounded-full" />
      <div className="fixed -bottom-32 right-1/4 w-[500px] h-[500px] bg-gradient-to-tr from-indigo-500/10 to-transparent blur-3xl pointer-events-none -z-10 rounded-full" />

      <Sidebar />
      <div className="flex-1 flex flex-col lg:pl-64">
        <Topbar />
        
        <main className="flex-1 flex flex-col items-center justify-center px-4 py-12 lg:py-16">
          <div className="max-w-4xl w-full space-y-10 animate-fade-in-up">
            
            {/* Wispr Floating Pill Announcement */}
            <div className="flex justify-center">
              <div className="inline-flex items-center gap-2.5 px-4 py-1.5 rounded-full border border-border/60 bg-card/40 backdrop-blur-xl text-xs font-medium shadow-sm hover:border-border transition-colors">
                <span className="flex h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
                <span className="text-muted-foreground">Supply Chain Flow Engine</span>
                <span className="text-border">|</span>
                <span className="text-foreground flex items-center gap-1 font-semibold">
                  CycloneDX 1.7 & SPDX 2.3 Ready <Sparkles className="w-3 h-3 text-purple-500" />
                </span>
              </div>
            </div>

            {/* Hero Section */}
            <div className="text-center space-y-4 max-w-2xl mx-auto">
              <h1 className="text-4xl sm:text-5xl lg:text-6xl font-black tracking-tight text-foreground leading-[1.1]">
                Speak to your code. <br />
                <span className="bg-gradient-to-r from-purple-500 via-indigo-400 to-blue-500 bg-clip-text text-transparent">
                  Secure every dependency.
                </span>
              </h1>
              <p className="text-base sm:text-lg text-muted-foreground leading-relaxed">
                Effortless software bill of materials and vulnerability intelligence. 
                Pure deterministic parsing without ever running untrusted code.
              </p>

              {/* Signature Wispr Flow Audio/Security Wave Visualizer */}
              <div className="flex items-center justify-center gap-1.5 pt-2">
                <span className="w-1 rounded-full bg-gradient-to-t from-purple-600 to-indigo-400 wave-bar-1" />
                <span className="w-1 rounded-full bg-gradient-to-t from-purple-500 to-blue-400 wave-bar-2" />
                <span className="w-1.5 rounded-full bg-gradient-to-t from-indigo-500 to-purple-400 wave-bar-3" />
                <span className="w-1 rounded-full bg-gradient-to-t from-blue-500 to-indigo-400 wave-bar-4" />
                <span className="w-1 rounded-full bg-gradient-to-t from-purple-600 to-blue-500 wave-bar-5" />
                <span className="text-xs font-mono text-muted-foreground ml-2">5 Ecosystems Active</span>
              </div>
            </div>

            {/* Wispr Glass Dropzone Capsule */}
            <div className="wispr-glow max-w-2xl mx-auto w-full">
              <div
                className={`
                  wispr-glass rounded-3xl p-8 sm:p-12 transition-all duration-300 text-center relative group
                  ${isDragging ? 'border-purple-500/80 bg-purple-500/[0.08] scale-[1.01]' : 'hover:border-border'}
                  ${isUploading ? 'opacity-60 pointer-events-none' : 'cursor-pointer'}
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

                <div className="flex flex-col items-center justify-center space-y-4">
                  <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-purple-600/20 to-indigo-600/20 border border-purple-500/30 flex items-center justify-center group-hover:scale-110 transition-transform duration-300 shadow-inner">
                    {isUploading ? (
                      <Activity className="h-8 w-8 text-purple-400 animate-spin" />
                    ) : (
                      <Upload className="h-8 w-8 text-purple-400 group-hover:text-purple-300 transition-colors" />
                    )}
                  </div>

                  <div className="space-y-1.5">
                    <div className="text-base sm:text-lg font-bold text-foreground">
                      {isUploading ? "Analyzing software supply chain..." : "Drop your project archive here"}
                    </div>
                    <p className="text-xs sm:text-sm text-muted-foreground">
                      Drag and drop a <code className="text-foreground font-mono bg-muted/60 px-1.5 py-0.5 rounded">.zip</code> or click to browse files
                    </p>
                  </div>

                  {/* Ecosystem badges pill strip */}
                  <div className="flex flex-wrap items-center justify-center gap-1.5 pt-2">
                    {["npm", "Python", "Maven", "Go", "Rust"].map((eco) => (
                      <span key={eco} className="px-2.5 py-0.5 rounded-full bg-background/50 border border-border/40 text-[11px] font-medium text-muted-foreground">
                        {eco}
                      </span>
                    ))}
                  </div>

                  {error && (
                    <div className="text-xs font-semibold text-red-500 bg-red-500/10 border border-red-500/20 px-3 py-1.5 rounded-full mt-2">
                      {error}
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Quick Actions Dock */}
            <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
              <Button
                onClick={handleSampleScan}
                disabled={isUploading}
                className="w-full sm:w-auto rounded-full px-6 py-5 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white font-semibold text-sm shadow-[0_0_25px_rgba(139,92,246,0.3)] transition-all duration-300 gap-2"
              >
                <Zap className="h-4 w-4" />
                Scan Demo Project (Instant)
                <ArrowRight className="h-4 w-4 ml-1" />
              </Button>
              <Button
                variant="outline"
                onClick={() => fileInputRef.current?.click()}
                disabled={isUploading}
                className="w-full sm:w-auto rounded-full px-6 py-5 border-border/60 bg-card/40 backdrop-blur-xl text-foreground font-medium text-sm hover:bg-card/70 transition-all gap-2"
              >
                <FileArchive className="h-4 w-4 text-muted-foreground" />
                Choose Local File
              </Button>
            </div>

            {/* Feature Cards in Wispr Frosted Glass */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-6">
              <div className="wispr-glass rounded-2xl p-5 space-y-2 border border-border/40 hover:border-purple-500/30 transition-colors">
                <div className="w-8 h-8 rounded-xl bg-purple-500/10 flex items-center justify-center text-purple-400">
                  <Layers className="h-4 w-4" />
                </div>
                <h3 className="font-bold text-sm text-foreground">Dual Standard SBOM</h3>
                <p className="text-xs text-muted-foreground leading-relaxed">
                  Export CycloneDX 1.7 JSON and SPDX 2.3 ISO standard formats with complete dependency graphs and PURLs.
                </p>
              </div>

              <div className="wispr-glass rounded-2xl p-5 space-y-2 border border-border/40 hover:border-indigo-500/30 transition-colors">
                <div className="w-8 h-8 rounded-xl bg-indigo-500/10 flex items-center justify-center text-indigo-400">
                  <Search className="h-4 w-4" />
                </div>
                <h3 className="font-bold text-sm text-foreground">OSV & CISA KEV Intelligence</h3>
                <p className="text-xs text-muted-foreground leading-relaxed">
                  Batch queries against real-time OSV.dev advisories, mapped to CVSS v3.1 scores and weaponized CISA KEV tags.
                </p>
              </div>

              <div className="wispr-glass rounded-2xl p-5 space-y-2 border border-border/40 hover:border-blue-500/30 transition-colors">
                <div className="w-8 h-8 rounded-xl bg-blue-500/10 flex items-center justify-center text-blue-400">
                  <Lock className="h-4 w-4" />
                </div>
                <h3 className="font-bold text-sm text-foreground">Zero Code Execution</h3>
                <p className="text-xs text-muted-foreground leading-relaxed">
                  Pure static parser engine. Zip Slip suppression, magic bytes validation, and decompression bomb protection.
                </p>
              </div>
            </div>

          </div>
        </main>
      </div>
    </div>
  );
}
