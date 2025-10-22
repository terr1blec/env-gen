from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from agents.run_context import RunContextWrapper
from agents.tool import function_tool

from .context import WorkflowContext
from .utils import ensure_directory, format_command_output


@function_tool
def describe_schema(ctx: RunContextWrapper[WorkflowContext]) -> str:
    """Return a human-readable summary of the MCP schema and recommended outputs."""
    return ctx.context.schema_summary


@function_tool
def get_recommended_paths(ctx: RunContextWrapper[WorkflowContext]) -> Dict[str, str]:
    """Return the recommended output paths relative to the workspace root."""
    context = ctx.context
    return {key: context.relative(path) for key, path in context.recommended_paths.items()}


@function_tool
def list_directory(
    ctx: RunContextWrapper[WorkflowContext],
    relative_path: Optional[str] = None,
) -> List[str]:
    """List files and directories under the given workspace-relative location."""
    base = ctx.context.workspace_root if relative_path is None else ctx.context.resolve_path(relative_path)
    if not base.exists():
        raise FileNotFoundError(f"Directory not found: {ctx.context.relative(base)}")
    if not base.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {ctx.context.relative(base)}")
    return sorted(entry.name for entry in base.iterdir())


@function_tool
def read_text(ctx: RunContextWrapper[WorkflowContext], relative_path: str) -> str:
    """Read a UTF-8 encoded text file relative to the workspace root."""
    path = ctx.context.resolve_path(relative_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {ctx.context.relative(path)}")
    if not path.is_file():
        raise IsADirectoryError(f"Path is not a file: {ctx.context.relative(path)}")
    return path.read_text(encoding="utf-8")


@function_tool
def write_text(
    ctx: RunContextWrapper[WorkflowContext],
    relative_path: str,
    content: str,
) -> str:
    """Write UTF-8 text to the given workspace-relative path, overwriting when present."""
    path = ctx.context.resolve_path(relative_path)
    ensure_directory(path.parent)
    path.write_text(content, encoding="utf-8")
    return f"Wrote {len(content)} characters to {ctx.context.relative(path)}"


@function_tool
def ensure_dir(ctx: RunContextWrapper[WorkflowContext], relative_path: str) -> str:
    """Ensure a workspace-relative directory exists."""
    path = ctx.context.resolve_path(relative_path)
    ensure_directory(path)
    return f"Directory ready: {ctx.context.relative(path)}"


@function_tool
def write_json(
    ctx: RunContextWrapper[WorkflowContext],
    relative_path: str,
    data: Any,
    *,
    indent: int = 2,
    sort_keys: bool = True,
) -> str:
    """Serialize JSON data to the given workspace-relative path."""
    path = ctx.context.resolve_path(relative_path)
    ensure_directory(path.parent)
    json_content = json.dumps(data, indent=indent, sort_keys=sort_keys, ensure_ascii=False)
    path.write_text(json_content, encoding="utf-8")
    return f"Wrote JSON to {ctx.context.relative(path)}"


@function_tool
def run_python(
    ctx: RunContextWrapper[WorkflowContext],
    entrypoint: str,
    args: Optional[List[str]] = None,
    *,
    as_module: bool = False,
    cwd: Optional[str] = None,
    timeout_seconds: float = 180.0,
) -> Dict[str, Any]:
    """
    Execute Python code inside the workspace.

    Args:
        entrypoint: Module name when `as_module=True`, otherwise workspace-relative script path.
        args: Optional command-line arguments.
        as_module: Run `python -m entrypoint` when True (only 'pytest' is permitted).
        cwd: Optional workspace-relative working directory.
        timeout_seconds: Timeout for the process.
    """
    args = args or []
    python_executable = sys.executable

    if cwd:
        working_dir = ctx.context.resolve_path(cwd)
    else:
        working_dir = ctx.context.workspace_root

    if as_module:
        if entrypoint not in {"pytest"}:
            raise ValueError("Only running pytest modules is permitted in module mode.")
        command: List[str] = [python_executable, "-m", entrypoint, *args]
    else:
        script_path = ctx.context.resolve_path(entrypoint)
        command = [python_executable, str(script_path), *args]

    try:
        completed = subprocess.run(
            command,
            cwd=str(working_dir),
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired as exc:
        return {
            "cmd": " ".join(command),
            "returncode": None,
            "stdout": exc.stdout or "",
            "stderr": f"Process timed out after {timeout_seconds} seconds.",
        }

    return format_command_output(completed)


@function_tool
def record_note(ctx: RunContextWrapper[WorkflowContext], note: str) -> str:
    """Append a coordination note shared across all agents."""
    ctx.context.notes.append(note)
    return f"Recorded note #{len(ctx.context.notes)}"


@function_tool
def get_notes(ctx: RunContextWrapper[WorkflowContext]) -> Dict[str, List[str]]:
    """Retrieve all coordination notes."""
    return {"notes": ctx.context.notes, "count": len(ctx.context.notes)}


TOOLS = [
    describe_schema,
    get_recommended_paths,
    list_directory,
    read_text,
    write_text,
    write_json,
    ensure_dir,
    run_python,
    record_note,
    get_notes,
]

__all__ = [
    "describe_schema",
    "get_recommended_paths",
    "list_directory",
    "read_text",
    "write_text",
    "write_json",
    "ensure_dir",
    "run_python",
    "record_note",
    "get_notes",
    "TOOLS",
]
