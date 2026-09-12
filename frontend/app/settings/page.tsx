"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Select } from "@/components/ui/select";
import { 
  Settings as SettingsIcon, 
  ShieldCheck, 
  Database, 
  FileCode2, 
  Sparkles, 
  Check, 
  Save 
} from "lucide-react";

export default function SettingsPage() {
  const [osvUrl, setOsvUrl] = useState("https://api.osv.dev");
  const [cacheTtl, setCacheTtl] = useState("24");
  const [maxUpload, setMaxUpload] = useState("100");
  const [defaultFormat, setDefaultFormat] = useState("cyclonedx-1.7");
  const [saved, setSaved] = useState(false);

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 2500);
  };

  return (
    <div className="p-6 md:p-10 max-w-4xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-extrabold tracking-tight flex items-center gap-3">
          <SettingsIcon className="h-8 w-8 text-primary" /> System Settings & Configuration
        </h1>
        <p className="text-muted-foreground mt-1">
          Configure security policies, vulnerability data sources, and SBOM export preferences.
        </p>
      </div>

      <div className="space-y-6">
        {/* Vulnerability Sources */}
        <Card className="border-border/50">
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <Database className="h-4 w-4 text-purple-400" /> Vulnerability Intelligence Data Sources
            </CardTitle>
            <CardDescription>
              Configure the authoritative external vulnerability feed for deterministic CVE matching.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="osvUrl">OSV.dev API Endpoint</Label>
              <Input
                id="osvUrl"
                value={osvUrl}
                onChange={(e) => setOsvUrl(e.target.value)}
                className="font-mono text-sm"
              />
              <p className="text-xs text-muted-foreground">
                Primary API for querying Open Source Vulnerabilities across PyPI, npm, Maven, Go, and Cargo.
              </p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="cacheTtl">Local Advisory Cache TTL (Hours)</Label>
                <Input
                  id="cacheTtl"
                  type="number"
                  value={cacheTtl}
                  onChange={(e) => setCacheTtl(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label>Lookup Strategy</Label>
                <div className="pt-2">
                  <Badge variant="outline" className="text-green-400 border-green-500/30 bg-green-500/10">
                    Active (Live Batch + SQLite Cache)
                  </Badge>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Security & Extraction Policies */}
        <Card className="border-border/50">
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <ShieldCheck className="h-4 w-4 text-green-400" /> Secure File Handling Guardrails
            </CardTitle>
            <CardDescription>
              Enforced zero-code-execution sandbox limits protecting against hostile archives.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div className="space-y-2">
                <Label htmlFor="maxUpload">Max Upload Size (MB)</Label>
                <Input
                  id="maxUpload"
                  type="number"
                  value={maxUpload}
                  onChange={(e) => setMaxUpload(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label>Max Decompressed Size</Label>
                <Input disabled value="500 MB" />
              </div>
              <div className="space-y-2">
                <Label>Max File Count</Label>
                <Input disabled value="10,000 files" />
              </div>
            </div>

            <div className="pt-2 border-t border-border/30 grid grid-cols-2 gap-2 text-xs text-muted-foreground">
              <div className="flex items-center gap-1.5">
                <Check className="h-3.5 w-3.5 text-green-400" /> Strict Zip Slip Traversal Suppression
              </div>
              <div className="flex items-center gap-1.5">
                <Check className="h-3.5 w-3.5 text-green-400" /> Decompression Bomb Ratio Cap (100:1)
              </div>
              <div className="flex items-center gap-1.5">
                <Check className="h-3.5 w-3.5 text-green-400" /> Pure Static AST Parsing (No Code Execution)
              </div>
              <div className="flex items-center gap-1.5">
                <Check className="h-3.5 w-3.5 text-green-400" /> Automatic Temp Directory Cleanup
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Standards & SBOM Formats */}
        <Card className="border-border/50">
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <FileCode2 className="h-4 w-4 text-blue-400" /> Compliance & SBOM Standards
            </CardTitle>
            <CardDescription>
              Select default machine-readable bill-of-materials generation standards.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label>Default Export Specification</Label>
              <Select 
                value={defaultFormat} 
                onChange={(e) => setDefaultFormat(e.target.value)}
                className="w-full sm:w-80"
              >
                <option value="cyclonedx-1.7">CycloneDX 1.7 JSON (EO 14028 / NTIA)</option>
                <option value="spdx-2.3">SPDX 2.3 JSON (ISO/IEC 5962:2021)</option>
                <option value="vex">CycloneDX 1.7 VEX (Vulnerability Exploitability)</option>
              </Select>
            </div>

            <div className="p-3 bg-muted/20 rounded-lg text-xs text-muted-foreground space-y-1">
              <span className="font-semibold text-foreground">Compliance Verification:</span>
              <p>
                Generated SBOMs include NTIA minimum elements: Supplier Name, Component Name, Version String,
                Other Unique Identifiers (PURL), Relationship Assertions, Author, and Timestamp.
              </p>
            </div>
          </CardContent>
        </Card>

        {/* AI Explainer Settings */}
        <Card className="border-border/50">
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-purple-400" /> AI Security Explainer
            </CardTitle>
            <CardDescription>
              Settings for component explainability and prescriptive risk summaries.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm font-semibold">Engine Mode</div>
                <div className="text-xs text-muted-foreground">
                  Deterministic Rule-Based Intelligence with optional LLM augmentation
                </div>
              </div>
              <Badge variant="outline" className="text-purple-400 border-purple-500/30 bg-purple-500/10">
                Deterministic Fallback Active
              </Badge>
            </div>

            <p className="text-xs text-muted-foreground pt-1">
              Product Principle: The deterministic scanner remains the source of truth. The AI explainer never fabricates findings, CVEs, or dependencies.
            </p>
          </CardContent>
        </Card>

        {/* Save Button */}
        <div className="flex justify-end pt-4">
          <Button onClick={handleSave} className="gap-2 bg-purple-600 hover:bg-purple-700 text-white min-w-[120px]">
            {saved ? (
              <>
                <Check className="h-4 w-4" /> Saved!
              </>
            ) : (
              <>
                <Save className="h-4 w-4" /> Save Changes
              </>
            )}
          </Button>
        </div>
      </div>
    </div>
  );
}
