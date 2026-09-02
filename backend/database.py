import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional

DB_PATH = Path(__file__).parent / "codesupply.db"


@contextmanager
def get_db() -> Generator[sqlite3.Connection, None, None]:
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    """Initializes SQLite tables for projects, components, relationships, findings, and SBOMs."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                created_at TEXT NOT NULL,
                file_size_bytes INTEGER DEFAULT 0,
                ecosystems TEXT NOT NULL,
                manifest_files TEXT NOT NULL,
                total_components INTEGER DEFAULT 0,
                direct_count INTEGER DEFAULT 0,
                transitive_count INTEGER DEFAULT 0,
                pinned_count INTEGER DEFAULT 0,
                unpinned_count INTEGER DEFAULT 0,
                findings_count INTEGER DEFAULT 0,
                critical_findings INTEGER DEFAULT 0,
                high_findings INTEGER DEFAULT 0,
                medium_findings INTEGER DEFAULT 0,
                low_findings INTEGER DEFAULT 0,
                status TEXT DEFAULT 'READY'
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS components (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT NOT NULL,
                name TEXT NOT NULL,
                version TEXT,
                raw_specifier TEXT,
                ecosystem TEXT NOT NULL,
                direct INTEGER NOT NULL,
                source_file TEXT,
                source_files_json TEXT,
                purl TEXT NOT NULL,
                scope TEXT DEFAULT 'required',
                license TEXT,
                integrity TEXT,
                resolved_url TEXT,
                dependencies_json TEXT,
                metadata_json TEXT,
                FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS relationships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT NOT NULL,
                parent_purl TEXT NOT NULL,
                child_purl TEXT NOT NULL,
                rel_type TEXT DEFAULT 'direct',
                FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS findings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT NOT NULL,
                component_name TEXT NOT NULL,
                severity TEXT NOT NULL,
                category TEXT NOT NULL,
                title TEXT NOT NULL,
                evidence TEXT,
                explanation TEXT,
                recommendation TEXT,
                FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sbom_records (
                project_id TEXT PRIMARY KEY,
                cyclonedx_json TEXT NOT NULL,
                graph_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
        """)

# Initialize database on module load
init_db()


class DatabaseRepository:
    """Helper methods for database CRUD operations."""

    @staticmethod
    def save_project(project_data: Dict[str, Any]):
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO projects (
                    id, name, created_at, file_size_bytes, ecosystems, manifest_files,
                    total_components, direct_count, transitive_count, pinned_count, unpinned_count,
                    findings_count, critical_findings, high_findings, medium_findings, low_findings, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    project_data["id"],
                    project_data["name"],
                    project_data["created_at"],
                    project_data.get("file_size_bytes", 0),
                    json.dumps(project_data["ecosystems"]),
                    json.dumps(project_data["manifest_files"]),
                    project_data.get("total_components", 0),
                    project_data.get("direct_count", 0),
                    project_data.get("transitive_count", 0),
                    project_data.get("pinned_count", 0),
                    project_data.get("unpinned_count", 0),
                    project_data.get("findings_count", 0),
                    project_data.get("critical_findings", 0),
                    project_data.get("high_findings", 0),
                    project_data.get("medium_findings", 0),
                    project_data.get("low_findings", 0),
                    project_data.get("status", "READY"),
                ),
            )

    @staticmethod
    def save_components(project_id: str, components: List[Dict[str, Any]]):
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM components WHERE project_id = ?", (project_id,))
            for c in components:
                cursor.execute(
                    """
                    INSERT INTO components (
                        project_id, name, version, raw_specifier, ecosystem, direct,
                        source_file, source_files_json, purl, scope, license,
                        integrity, resolved_url, dependencies_json, metadata_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        project_id,
                        c["name"],
                        c.get("version"),
                        c.get("raw_specifier"),
                        c["ecosystem"],
                        1 if c.get("direct", True) else 0,
                        c.get("source_file", ""),
                        json.dumps(c.get("source_files", [])),
                        c["purl"],
                        c.get("scope", "required"),
                        c.get("license"),
                        c.get("integrity"),
                        c.get("resolved_url"),
                        json.dumps(c.get("dependencies", [])),
                        json.dumps(c.get("metadata", {})),
                    ),
                )

    @staticmethod
    def save_findings(project_id: str, findings: List[Dict[str, Any]]):
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM findings WHERE project_id = ?", (project_id,))
            for f in findings:
                cursor.execute(
                    """
                    INSERT INTO findings (
                        project_id, component_name, severity, category, title, evidence, explanation, recommendation
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        project_id,
                        f["component_name"],
                        f["severity"],
                        f["category"],
                        f["title"],
                        f.get("evidence", ""),
                        f.get("explanation", ""),
                        f.get("recommendation", ""),
                    ),
                )

    @staticmethod
    def save_sbom_and_graph(project_id: str, cyclonedx_dict: Dict[str, Any], graph_dict: Dict[str, Any], created_at: str):
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO sbom_records (project_id, cyclonedx_json, graph_json, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (project_id, json.dumps(cyclonedx_dict), json.dumps(graph_dict), created_at),
            )

    @staticmethod
    def get_projects() -> List[Dict[str, Any]]:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM projects ORDER BY created_at DESC")
            rows = cursor.fetchall()
            results = []
            for r in rows:
                d = dict(r)
                d["ecosystems"] = json.loads(d["ecosystems"])
                d["manifest_files"] = json.loads(d["manifest_files"])
                results.append(d)
            return results

    @staticmethod
    def get_project(project_id: str) -> Optional[Dict[str, Any]]:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
            row = cursor.fetchone()
            if not row:
                return None
            d = dict(row)
            d["ecosystems"] = json.loads(d["ecosystems"])
            d["manifest_files"] = json.loads(d["manifest_files"])
            return d

    @staticmethod
    def get_components(project_id: str) -> List[Dict[str, Any]]:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM components WHERE project_id = ? ORDER BY direct DESC, name ASC", (project_id,))
            rows = cursor.fetchall()
            results = []
            for r in rows:
                d = dict(r)
                d["direct"] = bool(d["direct"])
                d["source_files"] = json.loads(d["source_files_json"]) if d.get("source_files_json") else []
                d["dependencies"] = json.loads(d["dependencies_json"]) if d.get("dependencies_json") else []
                d["metadata"] = json.loads(d["metadata_json"]) if d.get("metadata_json") else {}
                results.append(d)
            return results

    @staticmethod
    def get_findings(project_id: str) -> List[Dict[str, Any]]:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM findings WHERE project_id = ? ORDER BY id ASC", (project_id,))
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

    @staticmethod
    def get_sbom(project_id: str) -> Optional[Dict[str, Any]]:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT cyclonedx_json FROM sbom_records WHERE project_id = ?", (project_id,))
            row = cursor.fetchone()
            if row:
                return json.loads(row["cyclonedx_json"])
            return None

    @staticmethod
    def get_graph(project_id: str) -> Optional[Dict[str, Any]]:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT graph_json FROM sbom_records WHERE project_id = ?", (project_id,))
            row = cursor.fetchone()
            if row:
                return json.loads(row["graph_json"])
            return None
