with open('lib/api.ts', 'r', encoding='utf-8') as f:
    code = f.read()

code = code.replace(
    '  // Health',
    '''
  // Scan Diff
  async getScanDiff(baseScanId: string, compareScanId: string) {
    const res = await fetch(\/api/scans/\/diff/\);
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.error?.message || 'Failed to fetch scan diff');
    }
    return res.json();
  },

  // Health'''
)

with open('lib/api.ts', 'w', encoding='utf-8') as f:
    f.write(code)
