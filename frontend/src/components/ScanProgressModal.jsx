import React, { useEffect, useState } from 'react';
import { 
  CheckCircle2, 
  Loader2, 
  Layers, 
  FileSearch, 
  GitFork, 
  ShieldCheck, 
  FileJson, 
  AlertTriangle 
} from 'lucide-react';

export default function ScanProgressModal({ isOpen, projectName }) {
  const steps = [
    { id: 1, label: 'Uploading Archive', icon: Layers },
    { id: 2, label: 'Detecting Project Ecosystems', icon: FileSearch },
    { id: 3, label: 'Parsing Manifests & Lockfiles', icon: FileSearch },
    { id: 4, label: 'Extracting Exact Versions', icon: CheckCircle2 },
    { id: 5, label: 'Normalizing Canonical PURLs', icon: CheckCircle2 },
    { id: 6, label: 'Building Dependency DAG Graph', icon: GitFork },
    { id: 7, label: 'Generating CycloneDX 1.5 JSON', icon: FileJson },
    { id: 8, label: 'Running Risk & Anomaly Engine', icon: AlertTriangle },
  ];

  const [currentStep, setCurrentStep] = useState(1);

  useEffect(() => {
    if (!isOpen) {
      setCurrentStep(1);
      return;
    }

    const interval = setInterval(() => {
      setCurrentStep((prev) => (prev < 8 ? prev + 1 : prev));
    }, 280);

    return () => clearInterval(interval);
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-md flex items-center justify-center z-50 p-4">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-6">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-indigo-600/20 text-indigo-400 flex items-center justify-center">
            <Loader2 className="w-5 h-5 animate-spin" />
          </div>
          <div>
            <h3 className="text-base font-bold text-white">Scanning Software Repository</h3>
            <p className="text-xs text-slate-400 truncate max-w-[280px]">
              {projectName || 'Processing project archive...'}
            </p>
          </div>
        </div>

        {/* Pipeline Step List */}
        <div className="space-y-2.5">
          {steps.map((step) => {
            const Icon = step.icon;
            const isCompleted = step.id < currentStep;
            const isCurrent = step.id === currentStep;

            return (
              <div
                key={step.id}
                className={`flex items-center justify-between px-3 py-2 rounded-lg text-xs transition-all ${
                  isCurrent
                    ? 'bg-indigo-600/20 border border-indigo-500/40 text-indigo-200'
                    : isCompleted
                    ? 'bg-slate-800/40 text-slate-300'
                    : 'text-slate-500 opacity-60'
                }`}
              >
                <div className="flex items-center space-x-2.5">
                  {isCompleted ? (
                    <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                  ) : isCurrent ? (
                    <Loader2 className="w-4 h-4 text-indigo-400 animate-spin shrink-0" />
                  ) : (
                    <div className="w-4 h-4 rounded-full border border-slate-700 shrink-0" />
                  )}
                  <span className={isCurrent ? 'font-semibold text-white' : ''}>{step.label}</span>
                </div>
                {isCompleted && (
                  <span className="text-[10px] text-emerald-400 font-mono">Done</span>
                )}
              </div>
            );
          })}
        </div>

        <div className="text-center pt-2">
          <p className="text-[11px] text-slate-500">
            Static extraction with ZipSlip defense. Zero code execution.
          </p>
        </div>
      </div>
    </div>
  );
}
