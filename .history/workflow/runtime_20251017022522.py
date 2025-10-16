from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from agents import set_tracing_disabled
from agents.extensions.models.litellm_model import LitellmModel

from .agents import build_agent_suite
from .context import WorkflowContext, build_schema_summary, load_schema, slugify
from .logging_utils import get_workflow_logger, init_workflow_logger
from .orchestrator import execute_workflow
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

    module_slug = slug.replace("-", "_")

    server_module_path = output_dir / f"{module_slug}_server.py"
    dataset_module_path = output_dir / f"{module_slug}_dataset.py"
    dataset_json_path = output_dir / f"{module_slug}_dataset.json"
    tests_dir = workspace_root / "tests" / slug
    logs_dir = workspace_root / "logs" / slug
    ensure_directory(logs_dir)

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
        logs_dir=logs_dir,
    )
    context.recommended_paths = {
        "server_module": server_module_path,
        "dataset_module": dataset_module_path,
        "dataset_json": dataset_json_path,
        "tests_directory": tests_dir,
    }
    context.schema_summary = build_schema_summary(context)
    return context


async def run_workflow(args: Any) -> str:
    context = prepare_context(args)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = (context.logs_dir or (context.workspace_root / "logs")) / f"workflow_{timestamp}.log"
    context.log_file_path = log_file

    logger = init_workflow_logger(log_file)
    logger.info("Prepared context for schema: %s", context.schema_path)
    logger.info("Recommended output paths:")
    for key, path in context.recommended_paths.items():
        logger.info("  - %s: %s", key, context.relative(path))

    api_key = (
        getattr(args, "api_key", None)
        or os.getenv("DEEPSEEK_API_KEY")
        or os.getenv("LITELLM_API_KEY")
        or os.getenv("API_KEY")
    )
    if not api_key: 
        raise ValueError("API key is required")
    base_url: Optional[str] = (
        getattr(args, "base_url", None)
        or os.getenv("DEEPSEEK_BASE_URL")
        or os.getenv("LITELLM_BASE_URL")
        or os.getenv("BASE_URL")
        or "https://api.deepseek.com"
    )

    set_tracing_disabled(disabled=True)

    model = LitellmModel(model=args.model, api_key=api_key, base_url=base_url)
    agents = build_agent_suite(context, model)
    logger.info("Starting multi-agent pipeline with model %s...", args.model)

    step_results = await execute_workflow(
        context=context,
        agents=agents,
        goal_prompt=args.prompt,
        max_turns=args.max_turns,
    )
    logger.info("Multi-agent pipeline complete.")

    summary_lines = [
        f"Workflow slug: {context.slug}",
        "Outputs:",
    ]
    for key, value in context.recommended_paths.items():
        summary_lines.append(f"- {key}: {context.relative(value)}")

    summary_lines.append("")
    summary_lines.append("Step outcomes:")
    for step in step_results:
        summary_lines.append(f"[{step.name}] {step.output}")
        logger.info("Step %s result: %s", step.name, step.output)

    return "\n".join(summary_lines)


__all__ = ["prepare_context", "run_workflow"]
