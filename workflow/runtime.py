from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import Any, Optional, List

from agents import set_tracing_disabled
from agents.extensions.models.litellm_model import LitellmModel

from .agents import build_agent_suite
from .config import WorkflowConfig, load_config
from .context import WorkflowContext, build_schema_summary, load_schema, slugify
from .logging_utils import init_workflow_logger
from .orchestrator import execute_workflow
from .utils import ensure_directory
from .observability import ObservabilityTracker
from .progress import create_progress_tracker, StageStatus


def prepare_context(args: Any, config: Optional[WorkflowConfig] = None) -> WorkflowContext:
    """Prepare the workflow context from command-line arguments.
    
    Args:
        args: Command-line arguments
        config: Optional workflow configuration. If not provided, will be loaded from default locations.
    
    Returns:
        Initialized WorkflowContext
    """
    if config is None:
        # Load configuration from file or environment variables
        config_path = getattr(args, "config", None)
        config = load_config(config_path)
    
    workspace_root = Path(__file__).resolve().parent.parent
    schema_path = args.schema if args.schema.is_absolute() else workspace_root / args.schema
    schema_path = schema_path.resolve()
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")

    schema = load_schema(schema_path)
    metadata = schema.get("metadata", {})
    server_info = metadata.get("server_info_crawled", {})
    raw_name = server_info.get("name") or metadata.get("server_name") or schema_path.stem
    slug_input = getattr(args, "slug", None)
    slug_source = slug_input if slug_input else raw_name
    slug = slugify(slug_source)

    domain_override = getattr(args, "domain", None)
    domain_name: Optional[str] = domain_override
    domain_slug: Optional[str] = slugify(domain_override) if domain_override else None
    try:
        schema_rel = schema_path.relative_to(workspace_root)
    except ValueError:
        schema_rel = None

    if schema_rel is not None and not domain_override:
        parts = list(schema_rel.parts)
        if "mcp_servers" in parts:
            idx = parts.index("mcp_servers")
            if idx + 1 < len(parts):
                domain_name = parts[idx + 1]
                domain_slug = slugify(domain_name)

    # Use configured directory names
    output_root_name = config.directories.output_dir_name
    output_root = args.output_dir if args.output_dir.is_absolute() else workspace_root / output_root_name
    output_root = output_root.resolve()
    ensure_directory(output_root)

    if domain_slug:
        domain_output_root = output_root / domain_slug
        ensure_directory(domain_output_root)
        output_dir = domain_output_root / slug
    else:
        output_dir = output_root / slug
    ensure_directory(output_dir)

    transcripts_root_name = getattr(args, "transcripts_dir_name", None) or config.directories.transcripts_dir_name
    transcripts_root = (
        args.transcripts_dir if args.transcripts_dir.is_absolute() else workspace_root / transcripts_root_name
    )
    transcripts_root = transcripts_root.resolve()
    ensure_directory(transcripts_root)

    if domain_slug:
        transcripts_dir = transcripts_root / domain_slug / slug
    else:
        transcripts_dir = transcripts_root / slug
    ensure_directory(transcripts_dir)

    module_slug = slug.replace("-", "_")

    # Use configured file naming patterns
    server_module_path = output_dir / f"{module_slug}{config.file_naming.server_suffix}"
    database_module_path = output_dir / f"{module_slug}{config.file_naming.database_suffix}"
    database_json_path = output_dir / f"{module_slug}{config.file_naming.database_json_suffix}"
    metadata_json_path = output_dir / f"{module_slug}{config.file_naming.metadata_suffix}"
    
    tests_root_name = getattr(args, "tests_dir_name", None) or config.directories.tests_dir_name
    tests_root = workspace_root / tests_root_name
    if domain_slug:
        tests_dir = tests_root / domain_slug / slug
    else:
        tests_dir = tests_root / slug
    
    logs_root_name = getattr(args, "logs_dir_name", None) or config.directories.logs_dir_name
    logs_root = workspace_root / logs_root_name
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
    context.config = config
    context.recommended_paths = {
        "server_module": server_module_path,
        "database_module": database_module_path,
        "database_json": database_json_path,
        "metadata_json": metadata_json_path,
        "tests_directory": tests_dir,
        "transcripts_directory": transcripts_dir,
    }
    sample_database_path: Optional[Path] = None
    sample_root = workspace_root / "workflow" / config.directories.sample_data_dir_name
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


async def run_workflow(args: Any, config: Optional[WorkflowConfig] = None) -> str:
    """Run the complete workflow.
    
    Args:
        args: Command-line arguments
        config: Optional workflow configuration
    
    Returns:
        Summary string of workflow results
    """
    # Load configuration if not provided
    if config is None:
        config_path = getattr(args, "config", None)
        config = load_config(config_path)
    
    context = prepare_context(args, config)
    
    # Use configured log file pattern
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = config.file_naming.log_file_pattern.replace("{timestamp}", timestamp)
    log_file = (context.logs_dir or (context.workspace_root / config.directories.logs_dir_name)) / log_filename
    context.log_file_path = log_file

    logger = init_workflow_logger(log_file, config)
    logger.info("Prepared context for schema: %s", context.schema_path)
    logger.info("Recommended output paths:")
    for key, path in context.recommended_paths.items():
        logger.info("  - %s: %s", key, context.relative(path))

    # Get API key from configured sources
    api_key = getattr(args, "api_key", None)
    if not api_key:
        for env_var in config.model.api_key_env_vars:
            api_key = os.getenv(env_var)
            if api_key:
                break
    
    if not api_key: 
        raise ValueError(
            f"API key is required. Please set one of the following environment variables: "
            f"{', '.join(config.model.api_key_env_vars)} or pass it as an argument."
        )
    
    # Get base URL from configured sources
    base_url: Optional[str] = getattr(args, "base_url", None)
    if not base_url:
        for env_var in config.model.base_url_env_vars:
            base_url = os.getenv(env_var)
            if base_url:
                break
    
    if not base_url:
        base_url = config.model.default_base_url

    set_tracing_disabled(disabled=True)

    # Use configured model if not specified in args
    model_name = getattr(args, "model", None) or config.model.default_model
    model = LitellmModel(model=model_name, api_key=api_key, base_url=base_url)
    agents = build_agent_suite(context, model)
    logger.info("Starting multi-agent pipeline with model %s...", model_name)

    # Initialize observability tracker
    tracker = ObservabilityTracker(context)
    
    # Initialize progress visualizer
    enable_progress = getattr(args, "enable_progress", True)
    progress = create_progress_tracker(enabled=enable_progress)
    
    # Store progress in context for later use
    context._progress = progress
    context._tracker = tracker
    
    # Start progress visualization
    progress.start()
    logger.info("Observability and progress tracking initialized")

    # Use configured max_turns if not specified in args
    max_turns = getattr(args, "max_turns", None) or config.execution.max_turns_per_agent
    
    # Default goal prompt
    goal_prompt = "Construct the offline MCP server, database generator, database, and tests based on the provided schema."

    try:
        step_results = await execute_workflow(
            context=context,
            agents=agents,
            goal_prompt=goal_prompt,
            max_turns=max_turns,
            config=config,
            tracker=tracker,
        )
    except RuntimeError as exc:
        logger.error("Workflow terminated prematurely: %s", exc)
        progress.stop()
        raise
    except Exception as exc:
        logger.exception("Unexpected error during workflow execution")
        progress.stop()
        raise
    
    logger.info("Multi-agent pipeline complete.")
    
    # Stop progress and print summary
    progress.stop()
    progress.print_summary()
    
    # Export trace
    if tracker._trace_file:
        trace_export_path = context.logs_dir / f"trace_summary_{context.slug}.json"
        tracker.export_trace(trace_export_path)
        logger.info("Exported detailed trace to %s", context.relative(trace_export_path))

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

