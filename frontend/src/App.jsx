import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import LandingView from './components/LandingView';
import DashboardView from './components/DashboardView';
import DependencyGraphView from './components/DependencyGraphView';
import ComponentsTableView from './components/ComponentsTableView';
import FindingsView from './components/FindingsView';
import ExportView from './components/ExportView';
import ComponentDrawer from './components/ComponentDrawer';
import ScanProgressModal from './components/ScanProgressModal';
import SbomDiffModal from './components/SbomDiffModal';
import { 
  listProjects, 
  uploadProjectArchive, 
  loadDemoProject, 
  getProject, 
  getProjectComponents, 
  getProjectGraph, 
  getProjectFindings 
} from './api';

export default function App() {
  const [currentTab, setCurrentTab] = useState('landing');
  const [activeProject, setActiveProject] = useState(null);
  const [projectsList, setProjectsList] = useState([]);
  const [components, setComponents] = useState([]);
  const [graphData, setGraphData] = useState(null);
  const [findings, setFindings] = useState([]);
  const [selectedComponent, setSelectedComponent] = useState(null);
  const [isScanning, setIsScanning] = useState(false);
  const [isDiffModalOpen, setIsDiffModalOpen] = useState(false);
  const [scanProjectName, setScanProjectName] = useState('');
  const [globalError, setGlobalError] = useState('');

  // Initial load of past scans
  useEffect(() => {
    refreshProjects();
  }, []);

  const refreshProjects = async () => {
    try {
      const list = await listProjects();
      setProjectsList(list);
      if (list.length > 0 && !activeProject) {
        loadProjectDetails(list[0].id);
      }
    } catch (err) {
      console.error('Failed to load projects:', err);
    }
  };

  const loadProjectDetails = async (projectId) => {
    try {
      const [proj, comps, graph, fnds] = await Promise.all([
        getProject(projectId),
        getProjectComponents(projectId),
        getProjectGraph(projectId),
        getProjectFindings(projectId),
      ]);
      setActiveProject(proj);
      setComponents(comps);
      setGraphData(graph);
      setFindings(fnds);
    } catch (err) {
      console.error('Failed to load project details:', err);
      setGlobalError('Failed to load project scan details.');
    }
  };

  const handleSelectProject = (projectId) => {
    loadProjectDetails(projectId);
  };

  const handleUploadProject = async (file) => {
    setIsScanning(true);
    setScanProjectName(file.name);
    setGlobalError('');

    try {
      const newProj = await uploadProjectArchive(file);
      // Wait briefly so user sees the progress pipeline animation
      setTimeout(async () => {
        await refreshProjects();
        await loadProjectDetails(newProj.id);
        setIsScanning(false);
        setCurrentTab('dashboard');
      }, 1400);
    } catch (err) {
      setIsScanning(false);
      setGlobalError(err.message || 'Error processing archive.');
      alert(`Scan failed: ${err.message}`);
    }
  };

  const handleLoadDemo = async (sampleType) => {
    setIsScanning(true);
    setScanProjectName(`Sample: ${sampleType}`);
    setGlobalError('');

    try {
      const newProj = await loadDemoProject(sampleType);
      setTimeout(async () => {
        await refreshProjects();
        await loadProjectDetails(newProj.id);
        setIsScanning(false);
        setCurrentTab('dashboard');
      }, 1400);
    } catch (err) {
      setIsScanning(false);
      setGlobalError(err.message || 'Error loading demo.');
      alert(`Demo load failed: ${err.message}`);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      {/* Top Navigation */}
      <Navbar
        currentTab={currentTab}
        setCurrentTab={setCurrentTab}
        activeProject={activeProject}
        projectsList={projectsList}
        onSelectProject={handleSelectProject}
        onQuickDemo={() => handleLoadDemo('python-project')}
        onOpenCompare={() => setIsDiffModalOpen(true)}
      />

      {/* Main Content Area */}
      <main className="flex-1">
        {currentTab === 'landing' && (
          <LandingView
            onUpload={handleUploadProject}
            onLoadDemo={handleLoadDemo}
            isScanning={isScanning}
          />
        )}

        {currentTab === 'dashboard' && activeProject && (
          <DashboardView
            project={activeProject}
            components={components}
            findings={findings}
            onNavigateTab={setCurrentTab}
            onSelectComponent={setSelectedComponent}
          />
        )}

        {currentTab === 'graph' && activeProject && (
          <DependencyGraphView
            graphData={graphData}
            components={components}
            onSelectComponent={setSelectedComponent}
          />
        )}

        {currentTab === 'components' && activeProject && (
          <ComponentsTableView
            components={components}
            findings={findings}
            onSelectComponent={setSelectedComponent}
          />
        )}

        {currentTab === 'findings' && activeProject && (
          <FindingsView
            findings={findings}
            components={components}
            onSelectComponent={setSelectedComponent}
          />
        )}

        {currentTab === 'export' && activeProject && (
          <ExportView
            project={activeProject}
          />
        )}
      </main>

      {/* Slide-out Component Detail Drawer */}
      <ComponentDrawer
        component={selectedComponent}
        findings={findings}
        allComponents={components}
        onClose={() => setSelectedComponent(null)}
        onSelectComponent={setSelectedComponent}
      />

      {/* Scan Pipeline Progress Modal */}
      <ScanProgressModal
        isOpen={isScanning}
        projectName={scanProjectName}
      />

      {/* SBOM Comparison & Drift Modal */}
      <SbomDiffModal
        currentProject={activeProject}
        isOpen={isDiffModalOpen}
        onClose={() => setIsDiffModalOpen(false)}
      />

      {/* Footer */}
      <footer className="border-t border-slate-900 bg-slate-950 py-6 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
          <div>
            CodeSupply • SIH1449 Automated SBOM Generation & Supply-Chain Risk Engine
          </div>
          <div className="flex items-center space-x-4 text-slate-400">
            <span>CycloneDX 1.5 JSON</span>
            <span>•</span>
            <span>PyPI & NPM</span>
            <span>•</span>
            <span>Safe Extraction</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
