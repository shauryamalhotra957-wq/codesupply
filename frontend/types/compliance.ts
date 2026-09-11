export interface ComplianceScore {
  standard: string;
  status: 'compliant' | 'warning' | 'non_compliant';
  score: number;
  details: string;
}
