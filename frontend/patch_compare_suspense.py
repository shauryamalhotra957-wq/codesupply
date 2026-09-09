with open('app/scans/compare/page.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

code = code.replace('import { useEffect, useState } from "react";', 'import { useEffect, useState, Suspense } from "react";')

# Rename ComparePage to ComparePageContent
code = code.replace('export default function ComparePage() {', 'function ComparePageContent() {')

# Add new default export
wrapper = '''
export default function ComparePage() {
  return (
    <Suspense fallback={<div className="p-12 text-center text-muted-foreground">Loading comparison...</div>}>
      <ComparePageContent />
    </Suspense>
  );
}
'''

with open('app/scans/compare/page.tsx', 'w', encoding='utf-8') as f:
    f.write(code + "\n" + wrapper)
