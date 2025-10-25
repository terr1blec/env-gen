from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class WorkflowContext:
    """Shared state for the MCP offline generation workflow."""

    workspace_root: Path
    schema_path: Path
    schema: Dict[str, Any]
    slug: str
    server_name: str
    server_module_path: Path
    dataset_module_path: Path
    dataset_json_path: Path
    metadata_json_path: Path
    tests_dir: Path
    transcripts_dir: Path
    logs_dir: Path | None = None
    domain: Optional[str] = None
    domain_slug: Optional[str] = None
    log_file_path: Path | None = None
    recommended_paths: Dict[str, Path] = field(default_factory=dict)
    schema_summary: str = ""
    notes: List[str] = field(default_factory=list)
    data_contract: Dict[str, Any] | None = None
    expected_tool_names: List[str] = field(default_factory=list)

    def resolve_path(self, value: str | Path) -> Path:
        """Resolve a workspace-relative path, preventing directory escape."""
        candidate = Path(value)
        if not candidate.is_absolute():
            candidate = (self.workspace_root / candidate).resolve()
        else:
            candidate = candidate.resolve()

        if candidate == self.workspace_root or self.workspace_root in candidate.parents:
            return candidate
        raise ValueError(f"Path {value} is outside the workspace root {self.workspace_root}")

    def relative(self, value: Path) -> str:
        """Return a workspace-relative string for a resolved path."""
        try:
            return str(value.relative_to(self.workspace_root))
        except ValueError:
            return str(value)


def slugify(value: str) -> str:
    """Create a filesystem-friendly slug."""
    allowed = "abcdefghijklmnopqrstuvwxyz0123456789-_"
    simplified = value.strip().lower().replace(" ", "-")
    return "".join(ch for ch in simplified if ch in allowed) or "server"


def load_schema(schema_path: Path) -> Dict[str, Any]:
    return json.loads(schema_path.read_text(encoding="utf-8"))


def build_schema_summary(context: WorkflowContext) -> str:
    metadata = context.schema.get("metadata", {})
    server_info = metadata.get("server_info_crawled", {})
    tools = server_info.get("tools", [])
    lines = [
        f"Server name: {context.server_name}",
        f"Schema file: {context.relative(context.schema_path)}",
        f"Planned slug: {context.slug}",
        f"Tool count: {len(tools)}",
    ]
    for item in tools:
        name = item.get("name", "<unknown>")
        description = item.get("description", "").strip()
        parameters = item.get("parameters", [])
        lines.append(f"- {name}: {description}")
        if parameters:
            for param in parameters:
                param_name = param.get("name", "")
                required = param.get("required", False)
                param_type = param.get("type", "unknown")
                required_flag = "required" if required else "optional"
                lines.append(f"    - {param_name} ({param_type}, {required_flag})")
    lines.append("")
    lines.append("Recommended output locations:")
    for key, path in context.recommended_paths.items():
        lines.append(f"- {key}: {context.relative(path)}")
    return "\n".join(lines)
