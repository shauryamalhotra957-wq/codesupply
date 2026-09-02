import React from 'react';
import { 
  ShieldCheck, 
  LayoutDashboard, 
  Network, 
  Layers, 
  AlertTriangle, 
  Download, 
  UploadCloud, 
  PlayCircle,
  FolderGit2
} from 'lucide-react';

export default function Navbar({ 
  currentTab, 
  setCurrentTab, 
  activeProject, 
  projectsList, 
  onSelectProject, 
  onQuickDemo 
}) {
  const tabs = [
    { id: 'landing', label: 'Upload & Demo', icon: UploadCloud },
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard, disabled: !activeProject },
    { id: 'graph', label: 'Dependency Graph', icon: Network, disabled: !activeProject },
    { id: 'components', label: 'Components', icon: Layers, disabled: !activeProject },
    { id: 'findings', label: 'Risk Findings', icon: AlertTriangle, disabled: !activeProject, badge: activeProject?.findings_count },
    { id: 'export', label: 'Export & SBOM', icon: Download, disabled: !activeProject },
  ];

  return (
    <header className="bg-slate-900/90 backdrop-blur-md border-b border-slate-800 sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo Branding */}
          <div className="flex items-center space-x-3 cursor-pointer" onClick={() => setCurrentTab('landing')}>
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 to-indigo-400 flex items-center justify-center shadow-lg shadow-indigo-500/20 text-white font-bold">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="text-xl font-bold text-white tracking-tight">CodeSupply</span>
                <span className="text-[10px] uppercase font-semibold px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                  SIH1449 MVP
                </span>
              </div>
              <p className="text-xs text-slate-400 hidden sm:block">Automated SBOM Generation & Risk Engine</p>
            </div>
          </div>

          {/* Navigation Tabs */}
          <nav className="hidden md:flex space-x-1">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              const isActive = currentTab === tab.id;
              const isDisabled = tab.disabled;

              return (
                <button
                  key={tab.id}
                  disabled={isDisabled}
                  onClick={() => setCurrentTab(tab.id)}
                  className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-xs font-medium transition-all ${
                    isActive
                      ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                      : isDisabled
                      ? 'text-slate-600 cursor-not-allowed opacity-50'
                      : 'text-slate-300 hover:text-white hover:bg-slate-800/80'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{tab.label}</span>
                  {tab.badge > 0 && (
                    <span className={`ml-1.5 px-1.5 py-0.2 rounded-full text-[10px] font-bold ${
                      isActive ? 'bg-white text-indigo-700' : 'bg-red-500/20 text-red-400 border border-red-500/30'
                    }`}>
                      {tab.badge}
                    </span>
                  )}
                </button>
              );
            })}
          </nav>

          {/* Right Action: Active Project Switcher & Quick Demo */}
          <div className="flex items-center space-x-3">
            {projectsList.length > 0 && (
              <div className="relative">
                <select
                  value={activeProject?.id || ''}
                  onChange={(e) => onSelectProject(e.target.value)}
                  className="bg-slate-800 border border-slate-700 text-slate-200 text-xs rounded-lg px-3 py-2 pr-8 focus:ring-2 focus:ring-indigo-500 focus:outline-none appearance-none cursor-pointer"
                >
                  <option value="" disabled>Select Scanned Project</option>
                  {projectsList.map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.name} ({p.total_components} pkgs)
                    </option>
                  ))}
                </select>
                <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-slate-400">
                  <FolderGit2 className="w-3.5 h-3.5" />
                </div>
              </div>
            )}

            <button
              onClick={onQuickDemo}
              className="hidden lg:flex items-center space-x-1.5 bg-slate-800 hover:bg-slate-700 text-indigo-300 hover:text-white border border-indigo-500/30 hover:border-indigo-500/60 px-3 py-2 rounded-lg text-xs font-semibold transition"
            >
              <PlayCircle className="w-4 h-4 text-indigo-400" />
              <span>1-Click Demo</span>
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Sub-Navigation */}
      <div className="md:hidden border-t border-slate-800 px-2 py-2 flex space-x-1 overflow-x-auto">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = currentTab === tab.id;
          const isDisabled = tab.disabled;
          return (
            <button
              key={tab.id}
              disabled={isDisabled}
              onClick={() => setCurrentTab(tab.id)}
              className={`flex items-center space-x-1.5 px-2.5 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap transition ${
                isActive
                  ? 'bg-indigo-600 text-white'
                  : isDisabled
                  ? 'text-slate-600 opacity-40'
                  : 'text-slate-300 hover:bg-slate-800'
              }`}
            >
              <Icon className="w-3.5 h-3.5" />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>
    </header>
  );
}
