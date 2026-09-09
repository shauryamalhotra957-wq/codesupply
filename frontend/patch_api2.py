with open('lib/api.ts', 'r', encoding='utf-8') as f:
    code = f.read()

diff_method = '''
  async getScanDiff(baseScanId: string, compareScanId: string) {
    return fetchWithBase(/scans//diff/);
  }
'''

code = code.replace(
    '  async getHealth(): Promise<HealthResponse> {',
    diff_method + '\n  async getHealth(): Promise<HealthResponse> {'
)

with open('lib/api.ts', 'w', encoding='utf-8') as f:
    f.write(code)
