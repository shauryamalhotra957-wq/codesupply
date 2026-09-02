import React, { useState, useEffect } from 'react';
import { 
  Download, 
  FileJson, 
  FileSpreadsheet, 
  FileText, 
  Copy, 
  Check, 
  ShieldCheck, 
  ExternalLink,
  Search,
  Code
} from 'lucide-react';
import { getExportUrl, getProjectSbom } from '../api';

export default function ExportView({ project }) {
  const [sbomData, setSbomData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [copied, setCopied] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    if (project?.id) {
      setIsLoading(true);
      getProjectSbom(project.id)
        .then(data => setSbomData(data))
        .catch(err => console.error(err))
        .finally(() => setIsLoading(false));
    }
  }, [project?.id]);

  const handleCopyJson = () => {
    if (sbomData) {
      navigator.clipboard.writeText(JSON.stringify(sbomData, null, 2));
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const jsonString = sbomData ? JSON.stringify(sbomData, null, 2) : '';

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white flex items-center space-x-2.5">
          <Download className="w-6 h-6 text-indigo-400" />
          <span>Export & CycloneDX SBOM Hub</span>
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          Download standardized SBOM artifacts, tabular CSV inventories, and PDF security reports.
        </p>
      </div>

      {/* 3 Main Export Action Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* CycloneDX JSON */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 flex flex-col justify-between space-y-4 hover:border-indigo-500/50 transition shadow-xl">
          <div className="space-y-3">
            <div className="w-12 h-12 rounded-xl bg-indigo-600/10 border border-indigo-500/20 text-indigo-400 flex items-center justify-center font-bold">
              <FileJson className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h3 className="text-base font-bold text-white">CycloneDX v1.5 JSON</h3>
                <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-300">
                  Standard
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-1 leading-relaxed">
                Industry-standard machine-readable Software Bill of Materials with unique serial numbers, PURLs, and dependency DAG.
              </p>
            </div>
          </div>

          <a
            href={getExportUrl(project.id, 'cyclonedx')}
            download
            className="w-full flex items-center justify-center space-x-2 bg-indigo-600 hover:bg-indigo-500 text-white py-2.5 rounded-xl text-xs font-semibold shadow-md shadow-indigo-600/30 transition"
          >
            <Download className="w-4 h-4" />
            <span>Download CycloneDX JSON</span>
          </a>
        </div>

        {/* CSV Inventory */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 flex flex-col justify-between space-y-4 hover:border-emerald-500/50 transition shadow-xl">
          <div className="space-y-3">
            <div className="w-12 h-12 rounded-xl bg-emerald-600/10 border border-emerald-500/20 text-emerald-400 flex items-center justify-center font-bold">
              <FileSpreadsheet className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h3 className="text-base font-bold text-white">CSV Inventory</h3>
                <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300">
                  Tabular
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-1 leading-relaxed">
                Complete spreadsheet containing component names, pinned versions, ecosystems, licenses, and provenance paths.
              </p>
            </div>
          </div>

          <a
            href={getExportUrl(project.id, 'csv')}
            download
            className="w-full flex items-center justify-center space-x-2 bg-emerald-600 hover:bg-emerald-500 text-white py-2.5 rounded-xl text-xs font-semibold shadow-md shadow-emerald-600/30 transition"
          >
            <Download className="w-4 h-4" />
            <span>Download CSV Spreadsheet</span>
          </a>
        </div>

        {/* PDF Audit Report */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 flex flex-col justify-between space-y-4 hover:border-blue-500/50 transition shadow-xl">
          <div className="space-y-3">
            <div className="w-12 h-12 rounded-xl bg-blue-600/10 border border-blue-500/20 text-blue-400 flex items-center justify-center font-bold">
              <FileText className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h3 className="text-base font-bold text-white">Executive PDF Report</h3>
                <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-blue-500/20 text-blue-300">
                  Audit Doc
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-1 leading-relaxed">
                Comprehensive security audit PDF document formatted with executive metrics summary, anomaly explanations, and SBOM table.
              </p>
            </div>
          </div>

          <a
            href={getExportUrl(project.id, 'report')}
            download
            className="w-full flex items-center justify-center space-x-2 bg-blue-600 hover:bg-blue-500 text-white py-2.5 rounded-xl text-xs font-semibold shadow-md shadow-blue-600/30 transition"
          >
            <Download className="w-4 h-4" />
            <span>Download PDF Report</span>
          </a>
        </div>
      </div>

      {/* Live CycloneDX JSON Viewer */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-2xl space-y-0">
        <div className="bg-slate-950/80 px-6 py-4 border-b border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-center space-x-2">
            <Code className="w-4 h-4 text-indigo-400" />
            <h3 className="text-sm font-bold text-white">Live CycloneDX v1.5 SBOM JSON Preview</h3>
            <span className="text-[10px] font-mono text-slate-400 bg-slate-800 px-2 py-0.5 rounded">
              {sbomData?.serialNumber || 'Loading...'}
            </span>
          </div>

          <div className="flex items-center space-x-3">
            <button
              onClick={handleCopyJson}
              className="flex items-center space-x-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 px-3 py-1.5 rounded-lg text-xs font-medium border border-slate-700 transition"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
              <span>{copied ? 'Copied JSON!' : 'Copy to Clipboard'}</span>
            </button>
          </div>
        </div>

        <div className="p-4 bg-slate-950 max-h-[500px] overflow-y-auto font-mono text-xs text-slate-300 leading-relaxed">
          {isLoading ? (
            <div className="text-center py-12 text-slate-500">Loading CycloneDX SBOM payload...</div>
          ) : (
            <pre className="select-all">{jsonString}</pre>
          )}
        </div>
      </div>
    </div>
  );
}
