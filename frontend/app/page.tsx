"use client";

import { useState, useRef } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { 
  Upload, 
  FileArchive, 
  ArrowRight, 
  ShieldCheck, 
  FileJson, 
  Activity, 
  Zap, 
  CheckCircle2, 
  Sparkles,
  Layers,
  Search,
  Lock,
  GitCompare,
  FileText,
  Cpu,
  ArrowUpRight
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

  const ecosystems = [
    { name: "Node.js", tag: "npm", files: "package.json, package-lock.json (v1/v2/v3)" },
    { name: "Python", tag: "PyPI", files: "requirements.txt, pyproject.toml" },
    { name: "Java / JVM", tag: "Maven", files: "pom.xml" },
    { name: "Go", tag: "Go Modules", files: "go.mod" },
    { name: "Rust", tag: "Cargo", files: "Cargo.toml" },
  ];

  return (
    <div className="flex min-h-screen bg-background relative overflow-hidden selection:bg-purple-500/20">
      {/* Wispr Flow Atmospheric Ambient Glow */}
      <div className="fixed top-0 left-1/2 -translate-x-1/2 w-[900px] h-[450px] bg-gradient-to-b from-purple-600/15 via-indigo-600/10 to-transparent blur-3xl pointer-events-none -z-10 rounded-full" />
      <div className="fixed -bottom-40 right-1/4 w-[600px] h-[600px] bg-gradient-to-tr from-indigo-500/10 via-purple-500/5 to-transparent blur-3xl pointer-events-none -z-10 rounded-full" />

      <Sidebar />
      <div className="flex-1 flex flex-col lg:pl-64">
        <Topbar />
        
        <main className="flex-1 flex flex-col items-center justify-start px-4 py-12 lg:py-16">
          <div className="max-w-5xl w-full space-y-12 animate-fade-in-up">
            
            {/* Top Pill Announcement */}
            <div className="flex justify-center">
              <div className="inline-flex items-center gap-2.5 px-4 py-1.5 rounded-full border border-border/60 bg-card/40 backdrop-blur-xl text-xs font-medium shadow-sm hover:border-border transition-colors">
                <span className="flex h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
                <span className="text-muted-foreground font-mono">SIH1449</span>
                <span className="text-border">|</span>
                <span className="text-foreground flex items-center gap-1 font-semibold">
                  CycloneDX 1.7 & SPDX 2.3 Ready <Sparkles className="w-3 h-3 text-purple-400" />
                </span>
              </div>
            </div>

            {/* Editorial Hero Section */}
            <div className="text-center space-y-4 max-w-3xl mx-auto">
              <h1 className="text-4xl sm:text-6xl lg:text-7xl font-black tracking-tight text-foreground leading-[1.08]">
                Map every dependency. <br />
                <span className="bg-gradient-to-r from-purple-400 via-indigo-300 to-blue-400 bg-clip-text text-transparent">
                  Expose every risk.
                </span>
              </h1>
              <p className="text-base sm:text-lg text-muted-foreground leading-relaxed max-w-2xl mx-auto">
                Autonomous software supply chain intelligence for SIH1449. Parse multi-ecosystem archives, resolve transitive dependency graphs, detect known vulnerabilities via OSV & CISA KEV, and export compliance-grade SBOMs.
              </p>

              {/* Status Telemetry Strip */}
              <div className="flex flex-wrap items-center justify-center gap-2 pt-2">
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-card/40 border border-border/50 text-xs text-muted-foreground backdrop-blur-md">
                  <span className="w-2 h-2 rounded-full bg-emerald-400" />
                  <span className="font-mono text-[11px] text-foreground font-semibold">Static AST Engine</span>
                  <span className="text-border">|</span>
                  <span>5 Ecosystems</span>
                  <span className="text-border">|</span>
                  <span>Zero Code Execution</span>
                </div>
              </div>
            </div>

            {/* Dropzone Capsule */}
            <div className="wispr-glow max-w-2xl mx-auto w-full">
              <div
                className={`wispr-glass rounded-3xl p-8 sm:p-12 transition-all duration-300 text-center relative group ${
                  isDragging ? 'border-purple-500/80 bg-purple-500/[0.08] scale-[1.01]' : 'hover:border-border'
                } ${isUploading ? 'opacity-60 pointer-events-none' : 'cursor-pointer'}`}
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
                    <div className="text-xs font-semibold text-red-400 bg-red-500/10 border border-red-500/20 px-3 py-1.5 rounded-full mt-2">
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
                className="w-full sm:w-auto rounded-full px-7 py-6 bg-gradient-to-r from-purple-600 via-indigo-600 to-purple-600 hover:from-purple-500 hover:to-indigo-500 text-white font-semibold text-sm shadow-[0_0_30px_rgba(139,92,246,0.35)] transition-all duration-300 gap-2"
              >
                <Zap className="h-4 w-4 fill-current" />
                Scan Demo Project (Instant)
                <ArrowRight className="h-4 w-4 ml-1" />
              </Button>
              <Button
                variant="outline"
                onClick={() => fileInputRef.current?.click()}
                disabled={isUploading}
                className="w-full sm:w-auto rounded-full px-7 py-6 border-border/60 bg-card/40 backdrop-blur-xl text-foreground font-medium text-sm hover:bg-card/70 transition-all gap-2"
              >
                <FileArchive className="h-4 w-4 text-muted-foreground" />
                Choose Local Archive
              </Button>
            </div>

            {/* Bento Grid Feature Architecture */}
            <div className="pt-8 space-y-4">
              <div className="text-center space-y-1">
                <h2 className="text-2xl font-bold tracking-tight text-foreground">
                  Enterprise Supply Chain Architecture
                </h2>
                <p className="text-xs text-muted-foreground max-w-lg mx-auto">
                  Built for precision, speed, and strict zero-trust sandbox execution.
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2">
                {/* Bento Card 1 */}
                <div className="wispr-glass rounded-2xl p-6 space-y-3 border border-border/40 hover:border-purple-500/30 transition-all group">
                  <div className="w-10 h-10 rounded-xl bg-purple-500/10 flex items-center justify-center text-purple-400 group-hover:scale-105 transition-transform">
                    <Layers className="h-5 w-5" />
                  </div>
                  <h3 className="font-bold text-sm text-foreground">Dual SBOM Compliance</h3>
                  <p className="text-xs text-muted-foreground leading-relaxed">
                    Full OWASP CycloneDX 1.7 JSON and ISO/IEC 5962:2021 SPDX 2.3 exports with canonical Package URLs (PURLs) and cryptographically verifiable hashes.
                  </p>
                </div>

                {/* Bento Card 2 */}
                <div className="wispr-glass rounded-2xl p-6 space-y-3 border border-border/40 hover:border-indigo-500/30 transition-all group">
                  <div className="w-10 h-10 rounded-xl bg-indigo-500/10 flex items-center justify-center text-indigo-400 group-hover:scale-105 transition-transform">
                    <Search className="h-5 w-5" />
                  </div>
                  <h3 className="font-bold text-sm text-foreground">Real-Time Vulnerability Intel</h3>
                  <p className="text-xs text-muted-foreground leading-relaxed">
                    Sub-second batch queries against OSV.dev advisories, mapped to CVSS v3.1 mathematical severity and correlated with CISA Known Exploited Vulnerabilities (KEV).
                  </p>
                </div>

                {/* Bento Card 3 */}
                <div className="wispr-glass rounded-2xl p-6 space-y-3 border border-border/40 hover:border-blue-500/30 transition-all group">
                  <div className="w-10 h-10 rounded-xl bg-blue-500/10 flex items-center justify-center text-blue-400 group-hover:scale-105 transition-transform">
                    <Lock className="h-5 w-5" />
                  </div>
                  <h3 className="font-bold text-sm text-foreground">Zero Code Execution Sandbox</h3>
                  <p className="text-xs text-muted-foreground leading-relaxed">
                    Pure static AST parsing without invoking npm, pip, or cargo. Zip Slip path traversal mitigation, decompression bomb limits, and magic byte validation.
                  </p>
                </div>

                {/* Bento Card 4 */}
                <div className="wispr-glass rounded-2xl p-6 space-y-3 border border-border/40 hover:border-emerald-500/30 transition-all group">
                  <div className="w-10 h-10 rounded-xl bg-emerald-500/10 flex items-center justify-center text-emerald-400 group-hover:scale-105 transition-transform">
                    <Cpu className="h-5 w-5" />
                  </div>
                  <h3 className="font-bold text-sm text-foreground">Transitive DAG Synthesis</h3>
                  <p className="text-xs text-muted-foreground leading-relaxed">
                    Constructs complete Directed Acyclic Graphs, separating direct from transitive dependencies, surfacing hidden depth risks and deep dependencies.
                  </p>
                </div>

                {/* Bento Card 5 */}
                <div className="wispr-glass rounded-2xl p-6 space-y-3 border border-border/40 hover:border-amber-500/30 transition-all group">
                  <div className="w-10 h-10 rounded-xl bg-amber-500/10 flex items-center justify-center text-amber-400 group-hover:scale-105 transition-transform">
                    <FileText className="h-5 w-5" />
                  </div>
                  <h3 className="font-bold text-sm text-foreground">Executive Security Audit</h3>
                  <p className="text-xs text-muted-foreground leading-relaxed">
                    Generates standalone, printable HTML and JSON audit reports featuring letter-grade risk scoring (A to F), remediation guidance, and license attributions.
                  </p>
                </div>

                {/* Bento Card 6 */}
                <div className="wispr-glass rounded-2xl p-6 space-y-3 border border-border/40 hover:border-rose-500/30 transition-all group">
                  <div className="w-10 h-10 rounded-xl bg-rose-500/10 flex items-center justify-center text-rose-400 group-hover:scale-105 transition-transform">
                    <GitCompare className="h-5 w-5" />
                  </div>
                  <h3 className="font-bold text-sm text-foreground">Supply Chain Drift & Diff</h3>
                  <p className="text-xs text-muted-foreground leading-relaxed">
                    Diff any two historical project baselines to track added or removed packages, dependency drift, version bumps, and newly emerged CVE exposures.
                  </p>
                </div>
              </div>
            </div>

            {/* Ecosystem Support Matrix */}
            <div className="wispr-glass rounded-3xl p-6 sm:p-8 space-y-4 border border-border/40">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-2 border-b border-border/30">
                <div>
                  <h3 className="font-bold text-base text-foreground">Supported Manifests & Formats</h3>
                  <p className="text-xs text-muted-foreground">Multi-ecosystem parsing with native lockfile resolution</p>
                </div>
                <div className="flex items-center gap-2">
                  <span className="px-2.5 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-[11px] font-medium text-emerald-400">
                    All 5 Engines Ready
                  </span>
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3 pt-1">
                {ecosystems.map((eco) => (
                  <div key={eco.name} className="p-3.5 rounded-xl bg-card/30 border border-border/30 space-y-1.5">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-foreground">{eco.name}</span>
                      <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-purple-500/10 text-purple-400 border border-purple-500/20">
                        {eco.tag}
                      </span>
                    </div>
                    <p className="text-[11px] font-mono text-muted-foreground leading-tight">
                      {eco.files}
                    </p>
                  </div>
                ))}
              </div>
            </div>

            {/* Footer */}
            <div className="text-center pt-4 pb-8 text-xs text-muted-foreground border-t border-border/30 flex flex-col sm:flex-row items-center justify-between gap-2">
              <div>
                <span>CodeSupply - Built for Smart India Hackathon (SIH1449)</span>
              </div>
              <div className="flex items-center gap-4">
                <Link href="/scans" className="hover:text-foreground transition-colors">Scan History</Link>
                <Link href="https://github.com/shauryamalhotra957-wq/codesupply" target="_blank" className="hover:text-foreground transition-colors flex items-center gap-1">
                  GitHub <ArrowUpRight className="w-3 h-3" />
                </Link>
              </div>
            </div>

          </div>
        </main>
      </div>
    </div>
  );
}
