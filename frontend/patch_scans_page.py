import re

with open('app/scans/page.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

# Add state
state_code = '''
  const [selectedScans, setSelectedScans] = useState<string[]>([]);
  
  const toggleScanSelection = (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    setSelectedScans(prev => 
      prev.includes(id) ? prev.filter(s => s !== id) : [...prev, id].slice(-2)
    );
  };
'''

code = code.replace(
    '  const [error, setError] = useState<string | null>(null);',
    '  const [error, setError] = useState<string | null>(null);\n' + state_code
)

# Add Checkbox import (use standard input type checkbox if no UI component)
code = code.replace(
    'import { Package, ShieldAlert, ArrowUpRight, Plus, RefreshCw, Layers } from "lucide-react";',
    'import { Package, ShieldAlert, ArrowUpRight, Plus, RefreshCw, Layers, GitCompare } from "lucide-react";\nimport { Checkbox } from "@/components/ui/checkbox";'
)

# Add compare button to header
compare_btn = '''
          {selectedScans.length === 2 && (
            <Button size="sm" variant="secondary" asChild className="mr-2 border-primary/20 bg-primary/10 hover:bg-primary/20 text-primary">
              <Link href={/scans/compare?base=&compare=}>
                <GitCompare className="h-4 w-4 mr-1.5" />
                Compare Scans
              </Link>
            </Button>
          )}
'''
code = code.replace(
    '<Button variant="outline" size="sm" onClick={fetchScans} disabled={isLoading}>',
    compare_btn + '\n          <Button variant="outline" size="sm" onClick={fetchScans} disabled={isLoading}>'
)

# Add table header for checkbox
code = code.replace(
    '<TableHead>Project / Archive</TableHead>',
    '<TableHead className="w-[40px]"></TableHead>\n                    <TableHead>Project / Archive</TableHead>'
)

# Add table cell for checkbox
checkbox_cell = '''
                      <TableCell onClick={(e) => e.stopPropagation()}>
                        <Checkbox 
                          checked={selectedScans.includes(scan.id)}
                          onCheckedChange={() => toggleScanSelection({ stopPropagation: () => {} } as any, scan.id)}
                          disabled={!selectedScans.includes(scan.id) && selectedScans.length >= 2}
                        />
                      </TableCell>
'''
code = code.replace(
    '<TableCell className="font-medium">',
    checkbox_cell + '\n                      <TableCell className="font-medium">'
)

with open('app/scans/page.tsx', 'w', encoding='utf-8') as f:
    f.write(code)
