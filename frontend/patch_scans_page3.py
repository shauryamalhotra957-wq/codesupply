with open('app/scans/page.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

code = code.replace(
    'import { Checkbox } from "@/components/ui/checkbox";',
    ''
)

code = code.replace(
    '<Checkbox \n                          checked={selectedScans.includes(scan.id)}\n                          onCheckedChange={() => toggleScanSelection({ stopPropagation: () => {} } as any, scan.id)}\n                          disabled={!selectedScans.includes(scan.id) && selectedScans.length >= 2}\n                        />',
    '<input type="checkbox" className="h-4 w-4 rounded border-gray-300" checked={selectedScans.includes(scan.id)} onChange={(e) => toggleScanSelection(e as any, scan.id)} disabled={!selectedScans.includes(scan.id) && selectedScans.length >= 2} />'
)

with open('app/scans/page.tsx', 'w', encoding='utf-8') as f:
    f.write(code)
