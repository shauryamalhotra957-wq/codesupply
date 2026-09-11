export interface ExecutiveReportMetadata {
  scanId: string;
  projectName: string;
  generatedAt: string;
  grade: 'A' | 'B' | 'C' | 'D' | 'F';
  totalCves: number;
}
