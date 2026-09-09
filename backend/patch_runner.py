import re

with open('app/workers/runner.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Add import at the top
code = code.replace(
    "from sqlalchemy.ext.asyncio import AsyncSession",
    "from sqlalchemy.ext.asyncio import AsyncSession\nfrom app.api.ws import manager\nfrom app.api.routes import _scan_to_response, _get_stages"
)

broadcast_func = '''
    async def _broadcast_scan(self, db, scan_id: str):
        try:
            # We must commit before reading to ensure latest state? No, we just modified the objects, but let's refresh or fetch.
            # actually we can just select it
            result = await db.execute(select(Scan).where(Scan.id == scan_id))
            scan = result.scalar_one_or_none()
            if scan:
                stages = await _get_stages(scan_id, db)
                response = _scan_to_response(scan, stages)
                await manager.broadcast_scan_update(scan_id, response.model_dump(mode="json"))
        except Exception as e:
            logger.error(f"WS Broadcast error: {e}")
'''

# Insert broadcast_func into ScanWorker
code = code.replace(
    "    async def _update_stage(",
    broadcast_func + "\n    async def _update_stage("
)

# Replace 'await db.commit()' in _update_stage with 'await db.commit(); await self._broadcast_scan(db, scan_id)'
# Wait, _update_stage has 'await db.commit()' at the end.
code = re.sub(
    r'(await db\.commit\(\))(\s*)$',
    r'\1\n        await self._broadcast_scan(db, scan_id)\2',
    code,
    flags=re.MULTILINE
)

# Wait, process_scan also modifies scan.status and calls db.commit() in multiple places.
# It's safer to just replace all 'await db.commit()' with 'await db.commit(); await self._broadcast_scan(db, scan_id)' inside process_scan.
# Actually let's just do it manually in the file via replace_file_content or a script...

with open('app/workers/runner.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("patched")
