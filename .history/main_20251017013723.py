from __future__ import annotations

import argparse
import asyncio
import os
import sys
from pathlib import Path

from workflow.runtime import run_workflow


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the MCP offline server generation workflow.")
    parser.add_argument(
        "--schema",
        type=Path,
        default=Path("cf_0014.@smithery-ai_google-maps_labeled.json"),
        help="Path to the MCP schema JSON file.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("generated"),
        help="Directory where generated modules and datasets will be stored.",
    )
    parser.add_argument(
        "--transcripts-dir",
        type=Path,
        default=Path("transcripts"),
        help="Directory where agent transcripts can be written by downstream tooling.",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=os.getenv("WORKFLOW_MODEL", "deepseek/deepseek-chat"),
        help="OpenAI model identifier for all agents.",
    )
    parser.add_argument(
        "--max-turns",
        type=int,
        default=24,
        help="Maximum number of agent turns to allow for the workflow.",
    )
    parser.add_argument(
        "--prompt",
        type=str,
        default="Construct the offline MCP server, dataset generator, dataset, and tests based on the provided schema.",
        help="High-level goal shared across agents during the workflow.",
    )
    parser.add_argument(
        "--api-key",
        type=str,
        default=None,
        help="Override API key passed to LiteLLM (falls back to DEEPSEEK_API_KEY / API_KEY environments).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        summary = asyncio.run(run_workflow(args))
    except Exception as exc:
        print(f"Workflow failed: {exc}", file=sys.stderr)
        sys.exit(1)

    print("Workflow completed.")
    print(summary)


if __name__ == "__main__":
    main()
