import {
  Scan,
  ScanListResponse,
  ScanSummary,
  ComponentListResponse,
  Component,
  GraphData,
  Vulnerability,
  SBOMData,
  HealthResponse,
  RemediationsResponse,
  ComponentExplanation
} from "@/types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = "ApiError";
  }
}

async function fetchWithBase(endpoint: string, options: RequestInit = {}) {
  const url = `${API_BASE}${endpoint}`;
  const response = await fetch(url, {
    ...options,
    headers: {
      ...options.headers,
    },
  });

  if (!response.ok) {
    let message = "An error occurred";
    try {
      const data = await response.json();
      message = data.error?.message || data.message || data.detail || message;
    } catch {
      // Ignored
    }
    throw new ApiError(response.status, message);
  }

  // Handle blob responses
  if (options.headers && (options.headers as Record<string, string>)["Accept"] === "application/json" === false) {
     const contentType = response.headers.get("content-type");
     if (contentType && !contentType.includes("application/json")) {
         return response.blob();
     }
  }

  return response.json();
}

class ApiClient {
  async uploadScan(file: File): Promise<Scan> {
    const formData = new FormData();
    formData.append("file", file);
    return fetchWithBase("/scans", {
      method: "POST",
      body: formData,
    });
  }

  async createSampleScan(): Promise<Scan> {
    return fetchWithBase("/scans/sample", {
      method: "POST",
    });
  }

  async listScans(params?: { limit?: number; offset?: number }): Promise<ScanListResponse> {
    const searchParams = new URLSearchParams();
    if (params?.limit) searchParams.append("limit", String(params.limit));
    if (params?.offset) searchParams.append("offset", String(params.offset));
    const qs = searchParams.toString();
    return fetchWithBase(`/scans${qs ? `?${qs}` : ''}`);
  }

  async getScan(scanId: string): Promise<Scan> {
    return fetchWithBase(`/scans/${scanId}`);
  }

  async getScanSummary(scanId: string): Promise<ScanSummary> {
    return fetchWithBase(`/scans/${scanId}/summary`);
  }

  async getComponents(scanId: string, params?: Record<string, any>): Promise<ComponentListResponse> {
    const searchParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== "") {
          searchParams.append(key, String(value));
        }
      });
    }
    const queryString = searchParams.toString();
    const url = `/scans/${scanId}/components${queryString ? `?${queryString}` : ''}`;
    return fetchWithBase(url);
  }

  async getComponent(scanId: string, componentId: string): Promise<Component> {
    return fetchWithBase(`/scans/${scanId}/components/${componentId}`);
  }

  async getGraph(scanId: string, params?: Record<string, any>): Promise<GraphData> {
    const searchParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== "") {
          searchParams.append(key, String(value));
        }
      });
    }
    const queryString = searchParams.toString();
    const url = `/scans/${scanId}/graph${queryString ? `?${queryString}` : ''}`;
    return fetchWithBase(url);
  }

  async getVulnerabilities(scanId: string): Promise<{ items: Vulnerability[] }> {
    return fetchWithBase(`/scans/${scanId}/vulnerabilities`);
  }

  async getSBOM(scanId: string): Promise<SBOMData> {
    return fetchWithBase(`/scans/${scanId}/sbom`);
  }

  async getSPDX(scanId: string): Promise<any> {
    return fetchWithBase(`/scans/${scanId}/sbom/spdx`);
  }

  async downloadSBOM(scanId: string): Promise<Blob> {
    const response = await fetch(`${API_BASE}/scans/${scanId}/download/sbom`, {
      method: 'GET',
    });
    if (!response.ok) {
       throw new ApiError(response.status, "Failed to download SBOM");
    }
    return response.blob();
  }

  async downloadSPDX(scanId: string): Promise<Blob> {
    const response = await fetch(`${API_BASE}/scans/${scanId}/download/spdx`, {
      method: 'GET',
    });
    if (!response.ok) {
       throw new ApiError(response.status, "Failed to download SPDX SBOM");
    }
    return response.blob();
  }

  async downloadReportHTML(scanId: string): Promise<string> {
    const response = await fetch(`${API_BASE}/scans/${scanId}/report/html`, {
      method: 'GET',
    });
    if (!response.ok) {
       throw new ApiError(response.status, "Failed to fetch Executive Report");
    }
    return response.text();
  }

  async retryScan(scanId: string): Promise<Scan> {
    return fetchWithBase(`/scans/${scanId}/retry`, {
      method: "POST",
    });
  }

  async getVEX(scanId: string): Promise<any> {
    return fetchWithBase(`/scans/${scanId}/vex`);
  }

  async downloadVEX(scanId: string): Promise<Blob> {
    const response = await fetch(`${API_BASE}/scans/${scanId}/download/vex`, {
      method: "GET",
    });
    if (!response.ok) {
      throw new ApiError(response.status, "Failed to download VEX document");
    }
    return response.blob();
  }

  async getRemediations(scanId: string): Promise<RemediationsResponse> {
    return fetchWithBase(`/scans/${scanId}/remediations`);
  }

  exportCSVUrl(scanId: string): string {
    return `${API_BASE}/scans/${scanId}/export/csv`;
  }

  downloadVEXUrl(scanId: string): string {
    return `${API_BASE}/scans/${scanId}/download/vex`;
  }


  


  async explainComponent(scanId: string, componentId: string): Promise<ComponentExplanation> {
    return fetchWithBase(`/scans/${scanId}/components/${componentId}/explain`, {
      method: "POST",
    });
  }

  async getScanDiff(baseScanId: string, compareScanId: string) {
    return fetchWithBase("/scans/" + baseScanId + "/diff/" + compareScanId);
  }

  async getHealth(): Promise<HealthResponse> {
    return fetchWithBase("/health");
  }
}

export const api = new ApiClient();
