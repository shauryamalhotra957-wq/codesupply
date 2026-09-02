const API_BASE = '/api/projects';

export async function listProjects() {
  const res = await fetch(API_BASE);
  if (!res.ok) throw new Error('Failed to fetch projects');
  return res.json();
}

export async function uploadProjectArchive(file) {
  const formData = new FormData();
  formData.append('file', file);

  const res = await fetch(`${API_BASE}/upload`, {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Failed to upload project archive');
  }

  return res.json();
}

export async function loadDemoProject(sampleType) {
  const res = await fetch(`${API_BASE}/demo/${sampleType}`, {
    method: 'POST',
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to load demo project '${sampleType}'`);
  }

  return res.json();
}

export async function getProject(projectId) {
  const res = await fetch(`${API_BASE}/${projectId}`);
  if (!res.ok) throw new Error('Failed to fetch project');
  return res.json();
}

export async function getProjectComponents(projectId) {
  const res = await fetch(`${API_BASE}/${projectId}/components`);
  if (!res.ok) throw new Error('Failed to fetch components');
  return res.json();
}

export async function getProjectGraph(projectId) {
  const res = await fetch(`${API_BASE}/${projectId}/graph`);
  if (!res.ok) throw new Error('Failed to fetch dependency graph');
  return res.json();
}

export async function getProjectFindings(projectId) {
  const res = await fetch(`${API_BASE}/${projectId}/findings`);
  if (!res.ok) throw new Error('Failed to fetch findings');
  return res.json();
}

export async function getProjectSbom(projectId) {
  const res = await fetch(`${API_BASE}/${projectId}/sbom`);
  if (!res.ok) throw new Error('Failed to fetch CycloneDX SBOM');
  return res.json();
}

export async function getProjectSpdx(projectId) {
  const res = await fetch(`${API_BASE}/${projectId}/spdx`);
  if (!res.ok) throw new Error('Failed to fetch SPDX SBOM');
  return res.json();
}

export function getExportUrl(projectId, type) {
  if (type === 'cyclonedx') return `${API_BASE}/${projectId}/export/cyclonedx`;
  if (type === 'spdx') return `${API_BASE}/${projectId}/export/spdx`;
  if (type === 'csv') return `${API_BASE}/${projectId}/export/csv`;
  if (type === 'report') return `${API_BASE}/${projectId}/report`;
  return `${API_BASE}/${projectId}`;
}
