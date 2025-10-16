from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any, Dict


def ensure_directory(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def format_command_output(result: subprocess.CompletedProcess[str]) -> Dict[str, Any]:
    args = result.args
    if isinstance(args, (list, tuple)):
        command = " ".join(str(part) for part in args)
    else:
        command = str(args)
    return {
        "cmd": command,
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }
