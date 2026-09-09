with open('app/scans/page.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

import re
code = re.sub(
    r'<Link href=\{/scans/compare\?base=&compare=\}>',
    '<Link href={`/scans/compare?base=${selectedScans[1]}&compare=${selectedScans[0]}`}>',
    code
)

with open('app/scans/page.tsx', 'w', encoding='utf-8') as f:
    f.write(code)
