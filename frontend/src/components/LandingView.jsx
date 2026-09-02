import React, { useState, useRef } from 'react';
import { 
  UploadCloud, 
  FileCode2, 
  Layers, 
  ShieldAlert, 
  FileCheck, 
  Cpu, 
  Boxes, 
  AlertOctagon, 
  Sparkles,
  ArrowRight,
  Lock,
  FileArchive
} from 'lucide-react';

export default function LandingView({ onUpload, onLoadDemo, isScanning }) {
  const [isDragOver, setIsDragOver] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [errorMessage, setErrorMessage] = useState('');
  const fileInputRef = useRef(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = () => {
    setIsDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    setErrorMessage('');
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const file = e.dataTransfer.files[0];
      processFile(file);
    }
  };

  const handleFileChange = (e) => {
    setErrorMessage('');
    if (e.target.files && e.target.files.length > 0) {
      const file = e.target.files[0];
      processFile(file);
    }
  };

  const processFile = (file) => {
    if (!file.name.toLowerCase().endsWith('.zip')) {
      setErrorMessage('Please select a valid .zip software project archive.');
      return;
    }
    if (file.size > 50 * 1024 * 1024) {
      setErrorMessage('Archive exceeds the 50MB maximum upload limit.');
      return;
    }
    setSelectedFile(file);
    onUpload(file);
  };

  const demoCards = [
    {
      id: 'python-project',
      title: 'Python FastAPI Microservice',
      ecosystem: 'PyPI',
      ecoColor: 'from-blue-600/20 to-blue-500/10 text-blue-400 border-blue-500/30',
      icon: FileCode2,
      desc: 'Pinned dependencies in requirements.txt & pyproject.toml with clean specifier resolution.',
      tags: ['requirements.txt', 'pyproject.toml', 'PEP 621', '7 Pinned Components'],
    },
    {
      id: 'node-project',
      title: 'Node.js Express API',
      ecosystem: 'NPM',
      ecoColor: 'from-emerald-600/20 to-emerald-500/10 text-emerald-400 border-emerald-500/30',
      icon: Boxes,
      desc: 'Lockfile v3 parsing with deep direct vs transitive tree mapping and SHA-512 hashes.',
      tags: ['package.json', 'package-lock.json v3', 'Transitive DAG', '15+ Components'],
    },
    {
      id: 'mixed-project',
      title: 'Fullstack Monorepo',
      ecosystem: 'Mixed (PyPI + NPM)',
      ecoColor: 'from-purple-600/20 to-purple-500/10 text-purple-400 border-purple-500/30',
      icon: Layers,
      desc: 'Multi-manifest repo with Python backend and React client parsed into a single unified SBOM.',
      tags: ['Multi-Ecosystem', 'Unified CycloneDX', 'Monorepo Root'],
    },
    {
      id: 'broken-project',
      title: 'Anomalous / Broken Project',
      ecosystem: 'Risk Showcase',
      ecoColor: 'from-amber-600/20 to-red-500/10 text-amber-400 border-amber-500/30',
      icon: AlertOctagon,
      desc: 'Showcases unpinned dependencies, conflicting specifiers, duplicate entries, and deprecated libraries.',
      tags: ['Unpinned Versions', 'Conflicts', 'Duplicates', 'Risk Explanation Engine'],
    },
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-12">
      {/* Hero Section */}
      <div className="text-center space-y-4 max-w-3xl mx-auto">
        <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-indigo-950/80 border border-indigo-500/30 text-indigo-300 text-xs font-medium">
          <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
          <span>SIH1449: Software Bill of Materials (SBOM) Generation Tool</span>
        </div>
        <h1 className="text-4xl sm:text-5xl font-extrabold text-white tracking-tight leading-tight">
          Automated SBOM Generation & <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 via-purple-300 to-indigo-200">Supply-Chain Risk Intelligence</span>
        </h1>
        <p className="text-base text-slate-400 leading-relaxed">
          Upload any software repository archive. CodeSupply safely identifies multi-ecosystem dependencies,
          extracts exact versions, builds transitive trees, generates standard 
          <strong className="text-slate-200"> CycloneDX v1.5 JSON</strong>, and surfaces deterministic supply-chain anomalies.
        </p>
      </div>

      {/* Upload Dropzone */}
      <div className="max-w-2xl mx-auto">
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className={`border-2 border-dashed rounded-2xl p-8 sm:p-12 text-center cursor-pointer transition-all duration-200 ${
            isDragOver
              ? 'border-indigo-500 bg-indigo-500/10 scale-[1.01]'
              : 'border-slate-800 hover:border-slate-700 bg-slate-900/60 hover:bg-slate-900/90'
          }`}
        >
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            accept=".zip"
            className="hidden"
          />

          <div className="w-16 h-16 rounded-2xl bg-indigo-600/10 border border-indigo-500/20 text-indigo-400 flex items-center justify-center mx-auto mb-4">
            <UploadCloud className="w-8 h-8" />
          </div>

          <h3 className="text-lg font-semibold text-white mb-1">
            {isScanning ? 'Extracting and scanning project...' : 'Upload Project Archive (.zip)'}
          </h3>
          <p className="text-xs text-slate-400 mb-4">
            Drag and drop your project ZIP file here, or click to browse (Max 50MB)
          </p>

          <div className="flex flex-wrap items-center justify-center gap-2 text-[11px] text-slate-500">
            <span className="flex items-center space-x-1">
              <Lock className="w-3 h-3 text-emerald-400" />
              <span>Static Sandboxed (No Code Execution)</span>
            </span>
            <span>•</span>
            <span>ZipSlip Protected</span>
            <span>•</span>
            <span>Auto Cleanup</span>
          </div>

          {errorMessage && (
            <div className="mt-4 p-3 bg-red-950/60 border border-red-800 text-red-300 rounded-lg text-xs font-medium">
              {errorMessage}
            </div>
          )}
        </div>
      </div>

      {/* 1-Click Interactive Demo Scenarios */}
      <div className="space-y-4">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <div>
            <h2 className="text-lg font-bold text-white flex items-center space-x-2">
              <span>🚀 1-Click Pre-Packaged Demo Scenarios</span>
            </h2>
            <p className="text-xs text-slate-400">Instantly test the SBOM pipeline on curated real-world repository samples</p>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {demoCards.map((card) => {
            const Icon = card.icon;
            return (
              <div
                key={card.id}
                onClick={() => onLoadDemo(card.id)}
                className="bg-slate-900/80 hover:bg-slate-800/90 border border-slate-800 hover:border-indigo-500/50 rounded-xl p-5 cursor-pointer transition-all duration-200 group flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <div className="w-9 h-9 rounded-lg bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-200 group-hover:text-indigo-400 transition">
                      <Icon className="w-5 h-5" />
                    </div>
                    <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border ${card.ecoColor}`}>
                      {card.ecosystem}
                    </span>
                  </div>

                  <h3 className="text-sm font-bold text-white group-hover:text-indigo-300 transition mb-1.5">
                    {card.title}
                  </h3>
                  <p className="text-xs text-slate-400 leading-relaxed mb-4">
                    {card.desc}
                  </p>
                </div>

                <div>
                  <div className="flex flex-wrap gap-1.5 mb-4">
                    {card.tags.map((tag, i) => (
                      <span key={i} className="text-[10px] bg-slate-800/90 text-slate-400 px-2 py-0.5 rounded">
                        {tag}
                      </span>
                    ))}
                  </div>

                  <button
                    disabled={isScanning}
                    className="w-full flex items-center justify-center space-x-1.5 bg-slate-800 group-hover:bg-indigo-600 text-slate-300 group-hover:text-white py-2 rounded-lg text-xs font-semibold transition shadow-sm"
                  >
                    <span>Run Scan Demo</span>
                    <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 transition-transform" />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Architecture & Capabilities Section */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-6 border-t border-slate-800">
        <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-5">
          <div className="w-8 h-8 rounded-lg bg-indigo-500/10 text-indigo-400 flex items-center justify-center mb-3">
            <FileCheck className="w-4 h-4" />
          </div>
          <h4 className="text-sm font-bold text-white mb-1">Standard CycloneDX 1.5</h4>
          <p className="text-xs text-slate-400 leading-relaxed">
            Generates standardized Software Bill of Materials with unique serial numbers, component PURLs, licenses, and full dependency trees.
          </p>
        </div>

        <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-5">
          <div className="w-8 h-8 rounded-lg bg-emerald-500/10 text-emerald-400 flex items-center justify-center mb-3">
            <Lock className="w-4 h-4" />
          </div>
          <h4 className="text-sm font-bold text-white mb-1">Zero Code Execution Safety</h4>
          <p className="text-xs text-slate-400 leading-relaxed">
            Statically parses manifests without executing untrusted code. Employs path traversal (ZipSlip) defenses and safe temporary isolation.
          </p>
        </div>

        <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-5">
          <div className="w-8 h-8 rounded-lg bg-amber-500/10 text-amber-400 flex items-center justify-center mb-3">
            <ShieldAlert className="w-4 h-4" />
          </div>
          <h4 className="text-sm font-bold text-white mb-1">Deterministic Anomaly Engine</h4>
          <p className="text-xs text-slate-400 leading-relaxed">
            Detects unpinned dependencies, conflicting version bounds, duplicate declarations, and deprecated components with remediation advice.
          </p>
        </div>
      </div>
    </div>
  );
}
