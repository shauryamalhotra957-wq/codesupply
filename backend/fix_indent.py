import re

with open('app/workers/runner.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Dynamically capture indentation
def replacer(match):
    indent = match.group(1)
    return f"{indent}await db.commit()\n{indent}await self._broadcast_scan(db, scan_id)"

code = re.sub(r'(^[ \t]+)await db\.commit\(\)', replacer, code, flags=re.MULTILINE)

with open('app/workers/runner.py', 'w', encoding='utf-8') as f:
    f.write(code)
