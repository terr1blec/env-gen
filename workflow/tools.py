from __future__ import annotations

import base64
import binascii
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
    content: str | None = None,
    *,
    content_lines: Optional[List[str]] = None,
    content_base64: Optional[str] = None,
) -> str:
    """Write UTF-8 text to the given workspace-relative path, overwriting when present.

    Exactly one content source must be provided: `content` (plain text), `content_lines`
    (list of lines to be joined with newlines), or `content_base64` (UTF-8 decoded).
    """
    provided = [value is not None for value in (content, content_lines, content_base64)]
    if provided.count(True) != 1:
        raise ValueError("Provide exactly one of content, content_lines, or content_base64.")

    path = ctx.context.resolve_path(relative_path)
    ctx.context.ensure_write_allowed(path)
    ensure_directory(path.parent)

    if content is not None:
        final_content = content
    elif content_lines is not None:
        final_content = "\n".join(content_lines)
    else:
        try:
            decoded = base64.b64decode(content_base64 or "", validate=True)
        except (ValueError, binascii.Error) as exc:
            raise ValueError("Invalid base64 content provided to write_text.") from exc
        try:
            final_content = decoded.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValueError("Decoded base64 content is not valid UTF-8.") from exc

    path.write_text(final_content, encoding="utf-8")
    return f"Wrote {len(final_content)} characters to {ctx.context.relative(path)}"


@function_tool
def ensure_dir(ctx: RunContextWrapper[WorkflowContext], relative_path: str) -> str:
    """Ensure a workspace-relative directory exists."""
    path = ctx.context.resolve_path(relative_path)
    ctx.context.ensure_write_allowed(path)
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
    ctx.context.ensure_write_allowed(path)
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
    timeout_seconds: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Execute Python code inside the workspace.

    Args:
        entrypoint: Module name when `as_module=True`, otherwise workspace-relative script path.
        args: Optional command-line arguments.
        as_module: Run `python -m entrypoint` when True (only 'pytest' is permitted by default).
        cwd: Optional workspace-relative working directory.
        timeout_seconds: Timeout for the process. If not provided, uses config default.
    """
    args = args or []
    python_executable = sys.executable
    
    # Get configuration from context
    config = ctx.context.config
    if config is None:
        from .config import WorkflowConfig
        config = WorkflowConfig()
    
    # Use configured timeout if not provided
    if timeout_seconds is None:
        timeout_seconds = config.execution.python_timeout_seconds

    if cwd:
        working_dir = ctx.context.resolve_path(cwd)
    else:
        working_dir = ctx.context.workspace_root

    if as_module:
        allowed_modules = set(config.execution.allowed_modules)
        if entrypoint not in allowed_modules:
            raise ValueError(
                f"Module '{entrypoint}' is not permitted. Allowed modules: {', '.join(sorted(allowed_modules))}"
            )
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
