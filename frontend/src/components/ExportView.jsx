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
import { getExportUrl, getProjectSbom, getProjectSpdx } from '../api';

export default function ExportView({ project }) {
  const [activeFormat, setActiveFormat] = useState('cyclonedx');
  const [sbomData, setSbomData] = useState(null);
  const [spdxData, setSpdxData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [copied, setCopied] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    if (project?.id) {
      setIsLoading(true);
      Promise.all([
        getProjectSbom(project.id).catch(() => null),
        getProjectSpdx(project.id).catch(() => null)
      ])
        .then(([cdx, spdx]) => {
          setSbomData(cdx);
          setSpdxData(spdx);
        })
        .catch(err => console.error(err))
        .finally(() => setIsLoading(false));
    }
  }, [project?.id]);

  const currentData = activeFormat === 'cyclonedx' ? sbomData : spdxData;

  const handleCopyJson = () => {
    if (currentData) {
      navigator.clipboard.writeText(JSON.stringify(currentData, null, 2));
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const jsonString = currentData ? JSON.stringify(currentData, null, 2) : '';

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white flex items-center space-x-2.5">
          <Download className="w-6 h-6 text-indigo-400" />
          <span>Export & SBOM Compliance Hub</span>
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          Download standardized CycloneDX v1.5 and SPDX v2.3 SBOM artifacts, CSV inventories, and PDF security reports.
        </p>
      </div>

      {/* 4 Main Export Action Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* CycloneDX JSON */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 flex flex-col justify-between space-y-4 hover:border-indigo-500/50 transition shadow-xl">
          <div className="space-y-3">
            <div className="w-10 h-10 rounded-xl bg-indigo-600/10 border border-indigo-500/20 text-indigo-400 flex items-center justify-center font-bold">
              <FileJson className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-semibold text-white text-sm">CycloneDX 1.5 JSON</h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Standard SBOM format with full dependency DAG graph relationships.
              </p>
            </div>
          </div>
          <a
            href={getExportUrl(project?.id, 'cyclonedx')}
            download
            className="w-full py-2 px-3 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-semibold flex items-center justify-center space-x-2 transition shadow-lg shadow-indigo-600/20"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Download CycloneDX</span>
          </a>
        </div>

        {/* SPDX 2.3 JSON */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 flex flex-col justify-between space-y-4 hover:border-emerald-500/50 transition shadow-xl">
          <div className="space-y-3">
            <div className="w-10 h-10 rounded-xl bg-emerald-600/10 border border-emerald-500/20 text-emerald-400 flex items-center justify-center font-bold">
              <Code className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-semibold text-white text-sm">SPDX 2.3 JSON</h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Linux Foundation standard with Package URLs and license identifiers.
              </p>
            </div>
          </div>
          <a
            href={getExportUrl(project?.id, 'spdx')}
            download
            className="w-full py-2 px-3 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-semibold flex items-center justify-center space-x-2 transition shadow-lg shadow-emerald-600/20"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Download SPDX 2.3</span>
          </a>
        </div>

        {/* CSV Inventory */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 flex flex-col justify-between space-y-4 hover:border-blue-500/50 transition shadow-xl">
          <div className="space-y-3">
            <div className="w-10 h-10 rounded-xl bg-blue-600/10 border border-blue-500/20 text-blue-400 flex items-center justify-center font-bold">
              <FileSpreadsheet className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-semibold text-white text-sm">CSV Inventory</h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Tabular spreadsheet export for spreadsheets and licensing audits.
              </p>
            </div>
          </div>
          <a
            href={getExportUrl(project?.id, 'csv')}
            download
            className="w-full py-2 px-3 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-xl text-xs font-semibold flex items-center justify-center space-x-2 transition border border-slate-700"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Download CSV</span>
          </a>
        </div>

        {/* Executive PDF Report */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 flex flex-col justify-between space-y-4 hover:border-violet-500/50 transition shadow-xl">
          <div className="space-y-3">
            <div className="w-10 h-10 rounded-xl bg-violet-600/10 border border-violet-500/20 text-violet-400 flex items-center justify-center font-bold">
              <FileText className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-semibold text-white text-sm">PDF Audit Report</h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Formatted executive summary report with risk findings and advice.
              </p>
            </div>
          </div>
          <a
            href={getExportUrl(project?.id, 'report')}
            target="_blank"
            rel="noopener noreferrer"
            className="w-full py-2 px-3 bg-violet-600 hover:bg-violet-500 text-white rounded-xl text-xs font-semibold flex items-center justify-center space-x-2 transition shadow-lg shadow-violet-600/20"
          >
            <ExternalLink className="w-3.5 h-3.5" />
            <span>View PDF Report</span>
          </a>
        </div>
      </div>

      {/* Interactive JSON Viewer with Format Toggle */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-2xl">
        <div className="px-6 py-4 border-b border-slate-800 flex flex-wrap items-center justify-between gap-4 bg-slate-950/60">
          <div className="flex items-center space-x-3">
            <div className="flex bg-slate-900 border border-slate-800 rounded-lg p-0.5">
              <button
                onClick={() => setActiveFormat('cyclonedx')}
                className={`px-3 py-1 text-xs font-medium rounded-md transition ${
                  activeFormat === 'cyclonedx'
                    ? 'bg-indigo-600 text-white shadow'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                CycloneDX 1.5
              </button>
              <button
                onClick={() => setActiveFormat('spdx')}
                className={`px-3 py-1 text-xs font-medium rounded-md transition ${
                  activeFormat === 'spdx'
                    ? 'bg-emerald-600 text-white shadow'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                SPDX 2.3
              </button>
            </div>
            <span className="text-xs text-slate-500">
              {activeFormat === 'cyclonedx' ? 'specVersion 1.5' : 'spdxVersion 2.3'}
            </span>
          </div>

          <div className="flex items-center space-x-3">
            <div className="relative">
              <Search className="w-3.5 h-3.5 text-slate-500 absolute left-3 top-2.5" />
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search JSON content..."
                className="bg-slate-900 border border-slate-800 rounded-lg pl-8 pr-3 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500/50 w-48 sm:w-64"
              />
            </div>
            <button
              onClick={handleCopyJson}
              disabled={!currentData}
              className="py-1.5 px-3 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 rounded-lg text-xs font-medium flex items-center space-x-1.5 transition disabled:opacity-50"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
              <span>{copied ? 'Copied' : 'Copy JSON'}</span>
            </button>
          </div>
        </div>

        {/* Code Content */}
        <div className="p-6 max-h-[500px] overflow-auto font-mono text-xs text-indigo-300/90 leading-relaxed">
          {isLoading ? (
            <div className="py-16 text-center text-slate-500">Generating SBOM document...</div>
          ) : currentData ? (
            <pre className="whitespace-pre">{jsonString}</pre>
          ) : (
            <div className="py-16 text-center text-slate-500">No SBOM generated yet.</div>
          )}
        </div>
      </div>
    </div>
  );
}
