from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Optional

from agents import RunResult, Runner, set_tracing_disabled
from agents.run import RunConfig
from agents.extensions.models.litellm_model import LitellmModel

from .agents import build_agents
from .context import WorkflowContext, build_schema_summary, load_schema, slugify
from .utils import ensure_directory


def prepare_context(args: Any) -> WorkflowContext:
    workspace_root = Path(__file__).resolve().parent.parent
    schema_path = args.schema if args.schema.is_absolute() else workspace_root / args.schema
    schema_path = schema_path.resolve()
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")

    schema = load_schema(schema_path)
    metadata = schema.get("metadata", {})
    server_info = metadata.get("server_info_crawled", {})
    raw_name = server_info.get("name") or metadata.get("server_name") or schema_path.stem
    slug = slugify(raw_name)

    output_dir = args.output_dir if args.output_dir.is_absolute() else workspace_root / args.output_dir
    output_dir = output_dir.resolve()
    ensure_directory(output_dir)

    transcripts_dir = (
        args.transcripts_dir if args.transcripts_dir.is_absolute() else workspace_root / args.transcripts_dir
    )
    transcripts_dir = transcripts_dir.resolve()
    ensure_directory(transcripts_dir)

    server_module_path = output_dir / f"{slug}_server.py"
    dataset_module_path = output_dir / f"{slug}_dataset.py"
    dataset_json_path = output_dir / f"{slug}_dataset.json"
    tests_dir = workspace_root / "tests" / slug

    context = WorkflowContext(
        workspace_root=workspace_root,
        schema_path=schema_path,
        schema=schema,
        slug=slug,
        server_name=raw_name,
        server_module_path=server_module_path,
        dataset_module_path=dataset_module_path,
        dataset_json_path=dataset_json_path,
        tests_dir=tests_dir,
        transcripts_dir=transcripts_dir,
    )
    context.recommended_paths = {
        "server_module": server_module_path,
        "dataset_module": dataset_module_path,
        "dataset_json": dataset_json_path,
        "tests_directory": tests_dir,
    }
    context.schema_summary = build_schema_summary(context)
    return context


async def run_workflow(args: Any) -> RunResult:
    context = prepare_context(args)

    api_key = (
        getattr(args, "api_key", None)
        or os.getenv("DEEPSEEK_API_KEY")
        or os.getenv("LITELLM_API_KEY")
        or os.getenv("API_KEY")
        or "sk-f4605f9bf44d418895fe946cfa17dd7d"
    )
    base_url: Optional[str] = (
        getattr(args, "base_url", None)
        or os.getenv("DEEPSEEK_BASE_URL")
        or os.getenv("LITELLM_BASE_URL")
        or os.getenv("BASE_URL")
        or "https://api.deepseek.com"
    )

    set_tracing_disabled(disabled=True)

    model = LitellmModel(model=args.model, api_key=api_key, base_url=base_url)
    coordinator = build_agents(context, model)

    run_config = RunConfig(
        workflow_name=f"offline-mcp-generator::{context.slug}",
    )

    result = await Runner.run(
        coordinator,
        args.prompt,
        context=context,
        run_config=run_config,
        max_turns=args.max_turns,
    )
    return result


__all__ = ["prepare_context", "run_workflow"]
