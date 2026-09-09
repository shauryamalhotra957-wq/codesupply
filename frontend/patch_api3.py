with open('lib/api.ts', 'r', encoding='utf-8') as f:
    code = f.read()

import re
code = re.sub(r'async getScanDiff.*?return fetchWithBase.*?\}', '', code, flags=re.DOTALL)

diff_method = '''
  async getScanDiff(baseScanId: string, compareScanId: string) {
    return fetchWithBase("/scans/" + baseScanId + "/diff/" + compareScanId);
  }
'''

code = code.replace(
    '  async getHealth(): Promise<HealthResponse> {',
    diff_method + '\n  async getHealth(): Promise<HealthResponse> {'
)

with open('lib/api.ts', 'w', encoding='utf-8') as f:
    f.write(code)
