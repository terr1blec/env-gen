from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import Any, Optional, List

from agents import set_tracing_disabled
from agents.extensions.models.litellm_model import LitellmModel

from .agents import build_agent_suite
from .context import WorkflowContext, build_schema_summary, load_schema, slugify
from .logging_utils import init_workflow_logger
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

    domain_name: Optional[str] = None
    domain_slug: Optional[str] = None
    try:
        schema_rel = schema_path.relative_to(workspace_root)
    except ValueError:
        schema_rel = None

    if schema_rel is not None:
        parts = list(schema_rel.parts)
        if "mcp_servers" in parts:
            idx = parts.index("mcp_servers")
            if idx + 1 < len(parts):
                domain_name = parts[idx + 1]
                domain_slug = slugify(domain_name)

    output_root = args.output_dir if args.output_dir.is_absolute() else workspace_root / args.output_dir
    output_root = output_root.resolve()
    ensure_directory(output_root)

    if domain_slug:
        domain_output_root = output_root / domain_slug
        ensure_directory(domain_output_root)
        output_dir = domain_output_root / slug
    else:
        output_dir = output_root / slug
    ensure_directory(output_dir)

    transcripts_root = (
        args.transcripts_dir if args.transcripts_dir.is_absolute() else workspace_root / args.transcripts_dir
    )
    transcripts_root = transcripts_root.resolve()
    ensure_directory(transcripts_root)

    if domain_slug:
        transcripts_dir = transcripts_root / domain_slug / slug
    else:
        transcripts_dir = transcripts_root / slug
    ensure_directory(transcripts_dir)

    module_slug = slug.replace("-", "_")

    server_module_path = output_dir / f"{module_slug}_server.py"
    database_module_path = output_dir / f"{module_slug}_database.py"
    database_json_path = output_dir / f"{module_slug}_database.json"
    metadata_json_path = output_dir / f"{module_slug}_metadata.json"
    tests_root = workspace_root / "tests"
    if domain_slug:
        tests_dir = tests_root / domain_slug / slug
    else:
        tests_dir = tests_root / slug
    logs_root = workspace_root / "logs"
    if domain_slug:
        logs_dir = logs_root / domain_slug / slug
    else:
        logs_dir = logs_root / slug
    ensure_directory(tests_dir)
    ensure_directory(logs_dir)

    context = WorkflowContext(
        workspace_root=workspace_root,
        schema_path=schema_path,
        schema=schema,
        slug=slug,
        server_name=raw_name,
        domain=domain_name,
        domain_slug=domain_slug,
        server_module_path=server_module_path,
        database_module_path=database_module_path,
        database_json_path=database_json_path,
        metadata_json_path=metadata_json_path,
        tests_dir=tests_dir,
        transcripts_dir=transcripts_dir,
        logs_dir=logs_dir,
    )
    context.recommended_paths = {
        "server_module": server_module_path,
        "database_module": database_module_path,
        "database_json": database_json_path,
        "metadata_json": metadata_json_path,
        "tests_directory": tests_dir,
        "transcripts_directory": transcripts_dir,
    }
    sample_database_path: Optional[Path] = None
    sample_root = workspace_root / "workflow" / "sample_data"
    candidate_paths: List[Path] = []
    if domain_slug:
        candidate_paths.append(sample_root / domain_slug / f"{slug}.json")
    candidate_paths.append(sample_root / f"{slug}.json")
    for candidate in candidate_paths:
        if candidate.exists():
            sample_database_path = candidate.resolve()
            context.sample_database_path = sample_database_path
            context.recommended_paths["sample_database"] = sample_database_path
            break
    context.register_allowed_root(
        server_module_path.parent,
        database_module_path.parent,
        database_json_path.parent,
        metadata_json_path.parent,
        tests_dir,
        transcripts_dir,
        logs_dir,
    )
    context.register_allowed_root(
        server_module_path,
        database_module_path,
        database_json_path,
        metadata_json_path,
    )
    server_tools = server_info.get("tools", [])
    context.expected_tool_names = [
        tool.get("name")
        for tool in server_tools
        if isinstance(tool, dict) and tool.get("name")
    ]
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
        raise ValueError("API key is required. Please set the API key in the environment variables or pass it as an argument.")
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

    try:
        step_results = await execute_workflow(
            context=context,
            agents=agents,
            goal_prompt=args.prompt,
            max_turns=args.max_turns,
        )
    except RuntimeError as exc:
        logger.error("Workflow terminated prematurely: %s", exc)
        raise
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

