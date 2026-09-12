export type ScanStatus = 
  | "queued" | "extracting" | "discovering" | "parsing" 
  | "normalizing" | "resolving" | "sbom_generation" 
  | "sbom_validation" | "vulnerability_analysis" 
  | "risk_analysis" | "complete" | "failed";

export type RiskLevel = "critical" | "high" | "medium" | "low" | "unknown" | "none";
export type VersionConfidence = "exact" | "declared_range" | "inferred" | "unknown";
export type DependencyType = "direct" | "transitive" | "unknown";
export type LookupStatus = "checked" | "unavailable" | "cached" | "not_applicable" | "unknown";

export interface Scan {
  id: string;
  status: ScanStatus;
  filename: string;
  file_size: number;
  project_name: string | null;
  created_at: string;
  started_at: string | null;
  completed_at: string | null;
  error_message: string | null;
  error_code: string | null;
  total_components: number;
  total_vulnerabilities: number;
  total_manifests: number;
  stages: ScanStage[];
}

export interface ScanListResponse {
  items: Scan[];
  total: number;
}

export interface ScanStage {
  id: string;
  stage_name: string;
  status: "pending" | "running" | "completed" | "failed";
  started_at: string | null;
  completed_at: string | null;
  message: string | null;
  completed_count: number | null;
  total_count: number | null;
}

export interface ScanSummary {
  scan_id: string;
  total_components: number;
  total_vulnerabilities: number;
  total_high_critical: number;
  total_unknown_versions: number;
  components_by_ecosystem: Record<string, number>;
  components_by_risk: Record<string, number>;
  components_by_type: Record<string, number>;
  vulnerabilities_by_severity: Record<string, number>;
  sbom_valid: boolean | null;
  intelligence_status: string;
  intelligence_checked: number;
  intelligence_total: number;
  intelligence_cached: number;
  scan_duration_seconds: number | null;
  manifests_discovered: number;
}

export interface Component {
  id: string;
  name: string;
  version: string | null;
  ecosystem: string;
  package_manager: string | null;
  dependency_type: DependencyType;
  source_file: string;
  source_location: string | null;
  version_confidence: VersionConfidence;
  purl: string | null;
  license: string | null;
  risk_level: RiskLevel;
  risk_score: number | null;
  original_declaration: string | null;
  normalized_name: string;
  vulnerabilities: Vulnerability[];
  risk_reasons: RiskReason[];
  evidence: Evidence[];
}

export interface ComponentListResponse {
  items: Component[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

export interface Vulnerability {
  id: string;
  vuln_id: string;
  aliases: string[];
  summary: string;
  severity: string;
  affected_range: string | null;
  fixed_version: string | null;
  references: string[];
  source: string;
  modified_at: string | null;
  cvss_score: number | null;
  cvss_vector: string | null;
  component_id: string;
  component_name?: string;
  component_version?: string;
  component_ecosystem?: string;
}

export interface RiskReason {
  reason_type: string;
  description: string;
  severity_contribution: number;
}

export interface Evidence {
  id: string;
  source_file: string;
  source_location: string | null;
  method: string;
  confidence: string;
  value: string;
  evidence_type: string;
}

export interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
  total_nodes: number;
  total_edges: number;
  truncated: boolean;
}

export interface GraphNode {
  id: string;
  name: string;
  version: string | null;
  ecosystem: string;
  risk_level: RiskLevel;
  dependency_type: DependencyType;
  vulnerability_count: number;
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  confidence: string;
}

export interface SBOMData {
  format: string;
  spec_version: string;
  component_count: number;
  relationship_count: number;
  is_valid: boolean | null;
  validation_errors: string[];
  validation_warnings: string[];
  content: any;
}

export interface HealthResponse {
  status: string;
  version: string;
  database: string;
}

export interface RemediationAction {
  component_id: string;
  component_name: string;
  current_version: string;
  ecosystem: string;
  target_version: string;
  upgrade_command: string;
  severity: "critical" | "high" | "medium" | "low" | "info" | "none";
  max_cvss_score: number | null;
  vulns_fixed: string[];
  breaking_change_risk: "low" | "medium" | "high";
  risk_reduction_score: number;
  rationale: string;
}

export interface RemediationsResponse {
  scan_id: string;
  total_remediations: number;
  remediations: RemediationAction[];
}

export interface ComponentExplanation {
  component_id: string;
  component_name: string;
  version: string | null;
  summary: string;
  why_it_matters: string;
  what_to_do: string;
  technical_detail: string;
  label: string;
  disclaimer: string;
}


