with open("backend/app/workers/runner.py", "r", encoding="utf-8") as f:
    code = f.read()

# Remove global import
code = code.replace("from app.api.routes import _scan_to_response, _get_stages\n", "")
code = code.replace("from app.api.routes import _get_stages, _scan_to_response\n", "")

# Add local import inside _broadcast_scan
local_import = """    async def _broadcast_scan(self, db, scan_id: str):
        from app.api.routes import _get_stages, _scan_to_response
"""
code = code.replace("    async def _broadcast_scan(self, db, scan_id: str):", local_import)

with open("backend/app/workers/runner.py", "w", encoding="utf-8") as f:
    f.write(code)
