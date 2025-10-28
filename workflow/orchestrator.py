from __future__ import annotations

import ast
import json
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from textwrap import dedent
from typing import Any, Dict, List, Set, Optional

from agents import Runner
from agents.items import ToolCallItem, ToolCallOutputItem
from agents.run import RunConfig
from agents.exceptions import ModelBehaviorError

from .agents import AgentSuite
from .context import WorkflowContext
from .config import WorkflowConfig
from .logging_utils import get_workflow_logger
from .observability import ObservabilityTracker
from .progress import StageStatus


@dataclass
class StepResult:
    name: str
    description: str
    output: str
    success: bool = True

def _get_stage_id_from_step_name(step_name: str) -> str:
    """Map step name to stage ID for progress tracking."""
    if "schema_planning" in step_name:
        return "planning"
    elif "database_generation" in step_name:
        return "database_gen"
    elif "database_sampling" in step_name or "database_executor" in step_name:
        return "database_exec"
    elif "server_generation" in step_name:
        return "server_gen"
    elif "code_review" in step_name or "review" in step_name:
        return "review"
    elif "integration_tests" in step_name or "test" in step_name:
        return "testing"
    return "unknown"


async def _run_agent_step(
    *,
    name: str,
    agent,
    prompt: str,
    context: WorkflowContext,
    max_turns: int,
    workflow_slug: str,
    tracker: Optional[ObservabilityTracker] = None,
    cycle: Optional[int] = None,
) -> StepResult:
    logger = get_workflow_logger()
    run_config = RunConfig(workflow_name=f"offline-mcp::{workflow_slug}::{name}")

    # Get progress tracker from context if available
    progress = getattr(context, '_progress', None)
    stage_id = _get_stage_id_from_step_name(name)
    
    # Update progress: starting stage
    if progress:
        progress.update_stage(
            stage_id=stage_id,
            status=StageStatus.IN_PROGRESS,
            message=f"Starting {agent.name}",
            cycle=cycle,
        )

    # Record agent start
    if tracker:
        tracker.start_agent(
            agent_name=agent.name,
            step_name=name,
            cycle=cycle,
            prompt=prompt,
        )

    logger.info(
        "[%s] starting (max_turns=%s). Prompt: %s",
        name,
        max_turns,
        prompt.strip(),
    )
    
    success = True
    try:
        result = await Runner.run(
            agent,
            prompt,
            context=context,
            run_config=run_config,
            max_turns=max_turns,
        )
    except ModelBehaviorError as exc:
        success = False
        error_msg = str(exc)
        logger.warning("[%s] model behavior warning: %s", name, error_msg)

        if tracker:
            tracker.record_note(
                message=f"Model behavior warning in {name}: {error_msg}",
                metadata={"agent": agent.name},
            )

        _record_model_behavior_warning(context, name, error_msg)

        short_msg = error_msg[:60]
        if progress:
            progress.update_stage(
                stage_id=stage_id,
                status=StageStatus.IN_PROGRESS,
                message=f"Warning: {short_msg}",
                cycle=cycle,
            )

        return StepResult(
            name=name,
            description=prompt,
            output=f"WARNING: {error_msg}",
            success=False,
        )
    except Exception as exc:
        success = False
        logger.exception("[%s] failed with error", name)
        if tracker:
            tracker.record_error(exc, step_name=name)
        if progress:
            progress.update_stage(
                stage_id=stage_id,
                status=StageStatus.FAILED,
                message=f"Error: {str(exc)[:50]}",
            )
        raise

    output_text = result.final_output if result.final_output is not None else "(no final output)"
    logger.info(
        "[%s] completed. Output: %s",
        name,
        output_text,
    )
    
    # Log tool activity and record to tracker
    _log_tool_activity(name, result, tracker, progress, stage_id)
    
    # Record agent completion
    if tracker:
        tracker.end_agent(
            step_name=name,
            output=output_text,
            success=success,
        )
    
    # Update progress: completed stage
    if progress and "review" not in name:  # Review status updated separately
        progress.update_stage(
            stage_id=stage_id,
            status=StageStatus.COMPLETED,
            message="Done",
        )
    
    return StepResult(name=name, description=prompt, output=output_text.strip(), success=success)


async def execute_workflow(
    *,
    context: WorkflowContext,
    agents: AgentSuite,
    goal_prompt: str,
    max_turns: int,
    config: WorkflowConfig | None = None,
    tracker: Optional[ObservabilityTracker] = None,
) -> List[StepResult]:
    logger = get_workflow_logger()
    step_results: List[StepResult] = []
    
    # Use config from context if not provided
    if config is None:
        if context.config is not None:
            config = context.config
        else:
            from .config import WorkflowConfig
            config = WorkflowConfig()
    
    # Store config in context for other components
    if context.config is None:
        context.config = config

    database_module_rel = context.relative(context.database_module_path)
    database_json_rel = context.relative(context.database_json_path)
    server_module_rel = context.relative(context.server_module_path)
    metadata_json_rel = context.relative(context.metadata_json_path)
    tests_dir_rel = context.relative(context.tests_dir)

    planner_prompt = dedent(
        f"""
        {goal_prompt}

        You are the Schema Planner. Analyze the schema file and produce an actionable plan.
        Use `describe_schema` and `get_recommended_paths` for context, and capture concrete tasks for later agents via `record_note` so they can reference the notes.
        Be explicit about offline database synthesis, server implementation, metadata JSON production, and testing requirements.
        You MUST record at least one `DATA CONTRACT` note that lists the exact offline database structure (top-level keys, important nested fields, and types) that all agents must follow—do not proceed without writing this note.
        Record open questions if expectations are unclear.
        Document the required metadata JSON schema (tool name, description, input_schema with `type`, `properties`, and `required`, output_schema with `type`, `properties`) so builders align on structure.
        Return a succinct plan summary after confirming the DATA CONTRACT note exists.
        """
    ).strip()
    step_results.append(
        await _run_agent_step(
            name="schema_planning",
            agent=agents.schema_planner,
            prompt=planner_prompt,
            context=context,
            max_turns=max_turns,
            workflow_slug=context.slug,
            tracker=tracker,
        )
    )

    if config.validation.require_data_contract:
        if not any(note.strip().upper().startswith("DATA CONTRACT") for note in context.notes):
            raise RuntimeError(
                "Schema planning must record a DATA CONTRACT note detailing the offline database structure before continuing."
            )
    context.data_contract = _load_data_contract(context, config)

    # Pre-run purge: remove any stray files in output dir not among canonical outputs
    _purge_output_dir_unexpected(
        context,
        allowed={
            context.database_module_path.resolve(),
            context.database_json_path.resolve(),
            context.server_module_path.resolve(),
            context.metadata_json_path.resolve(),
        },
        note_label="PRE_RUN",
    )

    review_feedback: str | None = None
    max_review_cycles = config.review.max_review_cycles
    needs_database_update = True
    for cycle in range(max_review_cycles):
        revision_suffix = ""
        if review_feedback:
            pending_items = _extract_review_feedback_items(review_feedback)
            revision_suffix = _format_revision_suffix(pending_items, review_feedback)
        else:
            pending_items = []

        sample_note = ""
        if context.sample_database_path:
            sample_note = (
                f"\nIf the sample database at `{context.relative(context.sample_database_path)}` exists, "
                "load it and derive the offline database strictly from its records (do not invent synthetic values). "
                "Raise a clarification note if required fields are missing."
            )

        if needs_database_update:
            parent_dir = context.database_module_path.parent
            before_snapshot: Set[Path] = set()
            if parent_dir.exists():
                before_snapshot = {path.resolve() for path in parent_dir.iterdir()}

            database_instructions = dedent(
                f"""
                Generate or update the offline database synthesis module at `{database_module_rel}` and ensure it writes JSON to `{database_json_rel}`.
                Rely on planning notes (`get_notes`) and verify the schema expectations.
                Implement deterministic data generation when a seed is provided.
                Read the DATA CONTRACT note before coding and ensure the written JSON matches the documented keys precisely.
                If the contract is missing details, record a clarifying note before continuing.
                Limit file writes to the recommended database module and database JSON paths—capture any additional context in transcripts or shared notes instead.
                {sample_note}
                """
            ).strip()
            database_prompt = f"{database_instructions}{revision_suffix}"
            step_results.append(
                await _run_agent_step(
                    name=f"database_generation_cycle_{cycle + 1}",
                    agent=agents.dataset_builder,
                    prompt=database_prompt,
                    context=context,
                    max_turns=max_turns,
                    workflow_slug=context.slug,
                    tracker=tracker,
                    cycle=cycle + 1,
                )
            )

            _detect_unexpected_artifacts(context, before_snapshot)

            # Post-database-generation purge to catch any leftover or pre-existing extras
            allowed_outputs = {
                context.database_module_path.resolve(),
                context.database_json_path.resolve(),
                context.server_module_path.resolve(),
                context.metadata_json_path.resolve(),
            }

            if not _ensure_update_database_function(context):
                _purge_output_dir_unexpected(
                    context,
                    allowed=allowed_outputs,
                    note_label="POST_DATABASE_GEN",
                )
                logger.warning(
                    "Database module missing required update_database helper; queuing another generation cycle."
                )
                continue

            _purge_output_dir_unexpected(
                context,
                allowed=allowed_outputs,
                note_label="POST_DATABASE_GEN",
            )

            sampling_prompt = dedent(
                f"""
                Immediately execute the offline database module `{database_module_rel}` so that it writes `{database_json_rel}`.
                Use `run_python` to run the module right after modifications, confirm the JSON exists, and compare its structure against the DATA CONTRACT note.
                Record a coordination note summarizing any mismatches before the server implementation runs.
                """
            ).strip()
            step_results.append(
                await _run_agent_step(
                    name=f"database_sampling_cycle_{cycle + 1}",
                    agent=agents.dataset_executor,
                    prompt=sampling_prompt,
                    context=context,
                    max_turns=max_turns,
                    workflow_slug=context.slug,
                    tracker=tracker,
                    cycle=cycle + 1,
                )
            )
            _validate_database_against_contract(context, config, tracker)
            needs_database_update = False
        else:
            logger.info(
                "[database_generation_cycle_%s] Skipping offline database regeneration; no revisions requested.",
                cycle + 1,
            )

        server_instructions = dedent(
            f"""
            Implement or refine the FastMCP server module at `{server_module_rel}` backed by the offline database JSON.
            Ensure the module exposes the tools described in the schema, depends solely on the local database, and stays aligned with any documented notes.
            Always load the generated database from `{database_json_rel}` according to the DATA CONTRACT note, validate required keys exist, and only fall back to inline defaults if the JSON file is missing or malformed.
            Remove or update any hardcoded structures that diverge from the shared contract.
            Also produce a metadata JSON file at `{metadata_json_rel}` with the top-level shape `{{'name': <server name>, 'description': <short summary>, 'tools': [...]}}`.
            The `name` value must exactly match `{context.server_name}`.
            Each entry in `tools` is an object containing `name` (str), `description` (str), `input_schema` (an object with `type: 'object'`, a `properties` map of parameter names to objects with `type` and `description`, plus a `required` array), and `output_schema` (an object with `type: 'object'` and a `properties` map of output field names to objects with `type` and `description`).
            For example: {{"name": "getcurrency", "description": "Get the current exchange rate for a specific currency pair", "input_schema": {{"type": "object", "properties": {{"basecurrency": {{"type": "string", "description": "The base currency code, e.g., USD"}}, "targetcurrency": {{"type": "string", "description": "The target currency code, e.g., EUR"}}}}, "required": ["basecurrency", "targetcurrency"]}}, "output_schema": {{"type": "object", "properties": {{"exchangerate": {{"type": "number", "description": "The current exchange rate from base currency to target currency"}}, "last_updated": {{"type": "string", "description": "The date and time when the exchange rate was last updated"}}}}}}}}.
            Ensure the JSON is UTF-8 encoded and contains no extra top-level fields.
            Do not author extra helper modules or documentation outside the recommended paths; store supplementary materials in the transcripts directory or notes.
            """
        ).strip()
        server_prompt = f"{server_instructions}{revision_suffix}"
        server_result = await _run_agent_step(
            name=f"server_generation_cycle_{cycle + 1}",
            agent=agents.server_builder,
            prompt=server_prompt,
            context=context,
            max_turns=max_turns,
            workflow_slug=context.slug,
            tracker=tracker,
            cycle=cycle + 1,
        )
        step_results.append(server_result)

        if not server_result.success:
            logger.warning(
                "[server_generation_cycle_%s] Server builder returned warning; skipping metadata validation this cycle.",
                cycle + 1,
            )
        else:
            _validate_metadata_against_expected_tools(context, config, tracker)

        _ensure_recommended_paths_note(context)

        # Post-server-generation purge to remove any extra helper files
        _purge_output_dir_unexpected(
            context,
            allowed={
                context.database_module_path.resolve(),
                context.database_json_path.resolve(),
                context.server_module_path.resolve(),
                context.metadata_json_path.resolve(),
            },
            note_label="POST_SERVER_GEN",
        )

        review_prompt = dedent(
            """
            Thoroughly review the generated offline database module, server module, and metadata JSON file.
            Use `read_text` to inspect code, cross-check against schema expectations, and confirm the metadata accurately lists tool name, description, input schema, and output schema.
            Verify the database generator, produced JSON, and server module all adhere to the shared DATA CONTRACT note, and ensure the server loads the generated JSON rather than relying on divergent defaults.
            Confirm the metadata JSON has only `name`, `description`, and `tools` at the top level, the `name` matches the server name, and each tool entry matches the required schema (`name`, `description`, and nested `input_schema`/`output_schema` objects with `type`, `properties`, and `required` arrays).
            Inspect the recommended directories to ensure no stray helper files were created outside the approved paths; note any extras that should be moved to transcripts.
            If everything looks good, respond with `APPROVED:` followed by a short justification.
            If revisions are required, respond with `REVISIONS_NEEDED:` and list concrete fixes.
            Record essential feedback with `record_note` so builders can iterate.
            """
        ).strip()
        review_result = await _run_agent_step(
            name=f"code_review_cycle_{cycle + 1}",
            agent=agents.reviewer,
            prompt=review_prompt,
            context=context,
            max_turns=max_turns,
            workflow_slug=context.slug,
            tracker=tracker,
            cycle=cycle + 1,
        )
        step_results.append(review_result)

        verdict_text = review_result.output
        new_feedback_items = _extract_review_feedback_items(verdict_text)
        
        # Get progress for status update
        progress = getattr(context, '_progress', None)
        
        if _is_approved(verdict_text):
            review_feedback = None
            logger.info("[code_review_cycle_%s] Review approved, proceeding.", cycle + 1)
            
            # Update progress: review completed
            if progress:
                progress.update_stage(
                    stage_id="review",
                    status=StageStatus.COMPLETED,
                    message="Approved",
                )
            
            # Record decision to tracker
            if tracker:
                tracker.record_decision(
                    step_name=f"code_review_cycle_{cycle + 1}",
                    decision="APPROVED",
                    reasoning="Code review passed all checks",
                )
            break

        review_feedback = verdict_text
        _record_review_feedback_notes(context, new_feedback_items, verdict_text)
        needs_database_update = _database_revision_requested(new_feedback_items, review_feedback, config)
        
        logger.info(
            "[code_review_cycle_%s] Review requested revisions; iterating...",
            cycle + 1,
        )
        
        # Update progress: revisions needed
        if progress:
            progress.update_stage(
                stage_id="review",
                status=StageStatus.IN_PROGRESS,
                message=f"Revisions needed (cycle {cycle + 1})",
            )
        
        # Record decision to tracker
        if tracker:
            tracker.record_decision(
                step_name=f"code_review_cycle_{cycle + 1}",
                decision="REVISIONS_NEEDED",
                reasoning=f"Review cycle {cycle + 1} requested {len(new_feedback_items)} revisions",
            )
    else:
        failure_message = "Code review did not pass after multiple iterations. Check review feedback notes for details."
        if review_feedback:
            failure_message = f"{failure_message}\nLast reviewer feedback:\n{review_feedback.strip()}"
        logger.error(failure_message)
        raise RuntimeError(failure_message)

    test_prompt = dedent(
        f"""
        Write and execute automated tests ensuring the FastMCP server works with the offline database.
        Place tests under `{tests_dir_rel}`, run them with `run_python` (`pytest`) targeting that directory, and verify the metadata JSON at `{metadata_json_rel}` remains aligned with the server's exposed tools.
        Ensure tests import the server module, load the generated database JSON at `{database_json_rel}`, and assert the DATA CONTRACT keys exist and are consumed correctly.
        Validate that metadata uses the top-level fields `name`, `description`, and `tools`, that the name matches the server name, and that each tool entry follows the required schema for input and output definitions.
        Keep all test artifacts within the tests directory and record extra findings via transcripts or notes.
        Summarize the results and highlight any remaining issues.
        """
    ).strip()
    step_results.append(
        await _run_agent_step(
            name="integration_tests",
            agent=agents.test_agent,
            prompt=test_prompt,
            context=context,
            max_turns=max_turns,
            workflow_slug=context.slug,
            tracker=tracker,
        )
    )

    # Final purge to ensure the output directory is clean
    _purge_output_dir_unexpected(
        context,
        allowed={
            context.database_module_path.resolve(),
            context.database_json_path.resolve(),
            context.server_module_path.resolve(),
            context.metadata_json_path.resolve(),
        },
        note_label="FINAL",
    )

    return step_results


__all__ = ["execute_workflow", "StepResult"]


def _extract_review_feedback_items(feedback: str) -> List[str]:
    items: List[str] = []
    pattern = re.compile(r"^\s*(?:\d+[\).\s-]+|[-*+])\s+(.*)")
    for line in feedback.splitlines():
        match = pattern.match(line)
        if match:
            item = match.group(1).strip()
            if item:
                items.append(item)
        else:
            stripped = line.strip()
            if stripped and stripped.upper().startswith("REVISIONS_NEEDED"):
                continue
    return items


def _format_revision_suffix(items: List[str], raw_feedback: str) -> str:
    if items:
        bullet_lines = "\n".join(f"{index + 1}. {item}" for index, item in enumerate(items))
        return "\n\nThe latest review feedback, please handle each item one by one:\n" + bullet_lines + "\n"
    cleaned = raw_feedback.strip()
    if cleaned:
        return "\n\nReview feedback:\n" + cleaned + "\n"
    return "\n"


def _record_review_feedback_notes(context: WorkflowContext, items: List[str], raw_feedback: str) -> None:
    if raw_feedback.strip():
        raw_note = f"REVIEW_FEEDBACK_RAW: {raw_feedback.strip()}"
        if raw_note not in context.notes:
            context.notes.append(raw_note)
    for item in items:
        formatted = item.strip()
        if not formatted:
            continue
        note = f"REVIEW_FEEDBACK: {formatted}"
        if note not in context.notes:
            context.notes.append(note)


def _database_revision_requested(items: List[str], raw_feedback: str, config: WorkflowConfig) -> bool:
    data_terms = tuple(config.review.database_keywords)
    negative_indicators = tuple(config.review.negative_indicators)

    def _mentions_data_issue(text: str) -> bool:
        lowered = text.lower()
        if not any(term in lowered for term in data_terms):
            return False
        return any(term in lowered for term in negative_indicators)

    for item in items:
        if _mentions_data_issue(item):
            return True

    for line in raw_feedback.splitlines():
        if _mentions_data_issue(line):
            return True

    return False


def _is_approved(feedback: str) -> bool:
    # Prefer explicit first-line verdict if present
    for line in feedback.splitlines():
        clean = line.strip()
        if not clean:
            continue
        stripped = clean
        while stripped and stripped[0] in "*_`-:> ":
            stripped = stripped[1:]
        upper = stripped.upper()
        if upper.startswith("APPROVED"):
            return True
        if upper.startswith("REVISIONS_NEEDED"):
            return False
        # keep scanning subsequent lines
    # Fallback: scan entire text for clear approval signal
    text_upper = feedback.upper()
    if "APPROVED" in text_upper:
        return True
    if "REVISIONS_NEEDED" in text_upper:
        return False
    return False


def _log_tool_activity(
    step_name: str,
    result,
    tracker: Optional[ObservabilityTracker] = None,
    progress=None,
    stage_id: Optional[str] = None,
) -> None:
    logger = get_workflow_logger()
    tool_calls: list[str] = []
    tool_outputs: list[str] = []

    # Get agent name from result if available
    agent_name = getattr(result, "agent_name", "unknown")
    if hasattr(result, "agent") and hasattr(result.agent, "name"):
        agent_name = result.agent.name

    for item in getattr(result, "new_items", []):
        if isinstance(item, ToolCallItem):
            function = getattr(item.raw_item, "function", None)
            name = getattr(function, "name", None)
            if not name and hasattr(item.raw_item, "name"):
                name = getattr(item.raw_item, "name", None)
            if not name:
                name = getattr(item.raw_item, "type", "unknown")
            tool_calls.append(str(name))
            
            # Record to progress
            if progress and stage_id:
                progress.record_tool_call(agent_name, str(name), stage_id)
            
            # Record to tracker
            if tracker:
                # Extract arguments if available
                args = {}
                if function and hasattr(function, "arguments"):
                    try:
                        import json
                        args = json.loads(function.arguments)
                    except:
                        args = {"raw": str(function.arguments)[:100]}
                
                call_start = tracker.record_tool_call(
                    step_name=step_name,
                    tool_name=str(name),
                    tool_args=args,
                )
        elif isinstance(item, ToolCallOutputItem):
            tool_name = getattr(item.raw_item, "call_id", None)
            summary = item.output
            if isinstance(summary, dict):
                summary = summary.get("result") or summary.get("message") or "dict"
            tool_outputs.append(f"{tool_name or 'tool'} -> {summary}")
            
            # Record result to tracker (we don't have the exact start time here, so using current time)
            if tracker and tool_calls:
                tracker.record_tool_result(
                    step_name=step_name,
                    tool_name=tool_calls[-1] if tool_calls else "unknown",
                    result=summary,
                    start_time=time.time(),  # Approximate
                )

    if tool_calls:
        logger.info("[%s] tool calls: %s", step_name, ", ".join(tool_calls))
    else:
        logger.info("[%s] tool calls: (none)", step_name)

    if tool_outputs:
        logger.info("[%s] tool outputs: %s", step_name, "; ".join(tool_outputs))


def _load_data_contract(context: WorkflowContext, config: WorkflowConfig) -> Dict[str, Any]:
    if context.data_contract:
        return context.data_contract

    logger = get_workflow_logger()
    for note in reversed(context.notes):
        stripped = note.strip()
        if not stripped.upper().startswith("DATA CONTRACT"):
            continue
        _, _, payload = stripped.partition(":")
        payload = payload.strip()
        if not payload:
            if config.validation.require_data_contract:
                raise RuntimeError("DATA CONTRACT note is present but empty.")
            else:
                return {}
        try:
            contract = json.loads(payload)
        except json.JSONDecodeError as exc:
            raise RuntimeError("DATA CONTRACT note is not valid JSON.") from exc
        if not isinstance(contract, dict):
            raise RuntimeError("DATA CONTRACT note must decode to an object.")
        context.data_contract = contract
        logger.info("Loaded DATA CONTRACT with keys: %s", ", ".join(contract.keys()))
        return contract
    
    if config.validation.require_data_contract:
        raise RuntimeError("DATA CONTRACT note not found in planner output.")
    return {}


def _validate_database_against_contract(
    context: WorkflowContext,
    config: WorkflowConfig,
    tracker: Optional[ObservabilityTracker] = None,
) -> None:
    logger = get_workflow_logger()
    contract = _load_data_contract(context, config)
    database_path = context.database_json_path
    
    if not database_path.exists():
        error_msg = f"Database JSON not found at {context.relative(database_path)} after database synthesis."
        if tracker:
            tracker.record_validation("database_contract", False, error_msg)
        raise RuntimeError(error_msg)
    
    try:
        database_data = json.loads(database_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        error_msg = f"Database JSON at {context.relative(database_path)} is not valid JSON."
        if tracker:
            tracker.record_validation("database_contract", False, error_msg)
        raise RuntimeError(error_msg) from exc

    expected_keys = contract.get("top_level_keys")
    if not expected_keys:
        logger.warning("DATA CONTRACT does not specify top_level_keys, skipping key validation.")
        if tracker:
            tracker.record_validation("database_contract", True, "No top_level_keys in contract")
        return
    
    if not isinstance(expected_keys, list) or not all(isinstance(item, str) for item in expected_keys):
        error_msg = "DATA CONTRACT must include a string list under `top_level_keys`."
        if tracker:
            tracker.record_validation("database_contract", False, error_msg)
        raise RuntimeError(error_msg)

    missing = sorted(key for key in expected_keys if key not in database_data)
    if missing:
        error_msg = "Database JSON is missing required DATA CONTRACT keys: " + ", ".join(missing)
        if tracker:
            tracker.record_validation("database_contract", False, error_msg, {"missing_keys": missing})
        raise RuntimeError(error_msg)

    if context.sample_database_path and context.sample_database_path.exists() and config.validation.strict_sample_validation:
        try:
            sample_data = json.loads(context.sample_database_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                f"Sample database at {context.relative(context.sample_database_path)} is not valid JSON."
            ) from exc

        for key in expected_keys:
            if key not in sample_data:
                raise RuntimeError(
                    f"Sample database {context.relative(context.sample_database_path)} is missing required key '{key}'."
                )
            generated_value = database_data.get(key)
            sample_value = sample_data.get(key)
            if isinstance(generated_value, list) and isinstance(sample_value, list):
                sample_set = {json.dumps(item, sort_keys=True) for item in sample_value}
                unexpected = [
                    item for item in generated_value if json.dumps(item, sort_keys=True) not in sample_set
                ]
                if unexpected:
                    raise RuntimeError(
                        "Database JSON contains entries not present in the approved sample database for key "
                        f"'{key}'."
                    )

    if tracker:
        tracker.record_validation(
            "database_contract",
            True,
            f"Validated database JSON against DATA CONTRACT ({len(expected_keys)} keys)",
            {"expected_keys": expected_keys},
        )
    
    logger.info(
        "Validated database JSON against DATA CONTRACT (%s top-level keys).",
        len(expected_keys),
    )


def _validate_metadata_against_expected_tools(
    context: WorkflowContext,
    config: WorkflowConfig,
    tracker: Optional[ObservabilityTracker] = None,
) -> None:
    logger = get_workflow_logger()
    metadata_path = context.metadata_json_path
    
    if not metadata_path.exists():
        error_msg = f"Metadata JSON not found at {context.relative(metadata_path)} after server generation."
        if tracker:
            tracker.record_validation("metadata_tools", False, error_msg)
        raise RuntimeError(error_msg)

    try:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        error_msg = f"Metadata JSON at {context.relative(metadata_path)} is not valid JSON."
        if tracker:
            tracker.record_validation("metadata_tools", False, error_msg)
        raise RuntimeError(error_msg) from exc

    allowed_top_keys = set(config.validation.metadata_top_level_keys)
    unexpected_top = sorted(set(metadata.keys()) - allowed_top_keys)
    if unexpected_top:
        raise RuntimeError(
            "Metadata JSON contains unexpected top-level fields: " + ", ".join(unexpected_top)
        )

    name_value = metadata.get("name")
    if not isinstance(name_value, str):
        raise RuntimeError("Metadata JSON `name` must be a string.")
    if name_value != context.server_name:
        raise RuntimeError(
            f"Metadata JSON `name` must match the server name '{context.server_name}', but found '{name_value}'."
        )

    tools = metadata.get("tools")
    if not isinstance(tools, list):
        raise RuntimeError("Metadata JSON must contain a `tools` list.")

    observed_tool_names: Set[str] = set()
    expected_tool_names = {name for name in context.expected_tool_names if name}

    for index, tool in enumerate(tools):
        if not isinstance(tool, dict):
            raise RuntimeError(f"Metadata tool entry #{index + 1} must be an object.")
        if "inputSchema" in tool or "outputSchema" in tool:
            raise RuntimeError(
                "Metadata tool entries must use snake_case keys `input_schema` and `output_schema`."
            )
        required_tool_fields = {"name", "description", "input_schema", "output_schema"}
        missing_fields = sorted(required_tool_fields - set(tool.keys()))
        if missing_fields:
            raise RuntimeError(
                f"Metadata tool entry #{index + 1} is missing required fields: " + ", ".join(missing_fields)
            )

        tool_name = tool["name"]
        if not isinstance(tool_name, str) or not tool_name:
            raise RuntimeError(f"Metadata tool entry #{index + 1} must include a non-empty string `name`.")
        observed_tool_names.add(tool_name)

        description = tool["description"]
        if not isinstance(description, str) or not description.strip():
            raise RuntimeError(f"Metadata tool '{tool_name}' must include a non-empty string `description`.")

        input_schema = tool["input_schema"]
        if not isinstance(input_schema, dict):
            raise RuntimeError(f"Metadata tool '{tool_name}' `input_schema` must be an object.")
        if input_schema.get("type") != "object":
            raise RuntimeError(f"Metadata tool '{tool_name}' `input_schema.type` must be 'object'.")
        input_properties = input_schema.get("properties")
        if not isinstance(input_properties, dict):
            raise RuntimeError(f"Metadata tool '{tool_name}' `input_schema.properties` must be an object.")
        required_inputs = input_schema.get("required", [])
        if not isinstance(required_inputs, list) or not all(isinstance(item, str) for item in required_inputs):
            raise RuntimeError(
                f"Metadata tool '{tool_name}' `input_schema.required` must be a list of strings."
            )
        missing_required_props = sorted(name for name in required_inputs if name not in input_properties)
        if missing_required_props:
            raise RuntimeError(
                f"Metadata tool '{tool_name}' marks missing properties as required: "
                + ", ".join(missing_required_props)
            )

        output_schema = tool["output_schema"]
        if not isinstance(output_schema, dict):
            raise RuntimeError(f"Metadata tool '{tool_name}' `output_schema` must be an object.")
        if output_schema.get("type") != "object":
            raise RuntimeError(f"Metadata tool '{tool_name}' `output_schema.type` must be 'object'.")
        output_properties = output_schema.get("properties")
        if not isinstance(output_properties, dict):
            raise RuntimeError(f"Metadata tool '{tool_name}' `output_schema.properties` must be an object.")

    missing = sorted(expected_tool_names - observed_tool_names)
    if missing:
        raise RuntimeError(
            "Metadata JSON is missing expected tool definitions: " + ", ".join(missing)
        )

    unexpected = sorted(observed_tool_names - expected_tool_names)
    if unexpected:
        logger.warning(
            "Metadata JSON includes unexpected tool entries: %s",
            ", ".join(unexpected),
        )

    if tracker:
        tracker.record_validation(
            "metadata_tools",
            True,
            f"Validated metadata tool coverage ({len(observed_tool_names)} tools)",
            {
                "expected_tools": list(expected_tool_names),
                "observed_tools": list(observed_tool_names),
            },
        )
    
    logger.info(
        "Validated metadata tool coverage (%s tools).",
        len(observed_tool_names),
    )


def _detect_unexpected_artifacts(context: WorkflowContext, before_snapshot: Set[Path]) -> None:
    parent_dir = context.database_module_path.parent
    if not parent_dir.exists():
        return

    after_snapshot = {path.resolve() for path in parent_dir.iterdir()}
    new_entries = after_snapshot - before_snapshot
    allowed_outputs = {
        context.database_module_path.resolve(),
        context.database_json_path.resolve(),
    }

    unexpected = [
        path for path in new_entries
        if path not in allowed_outputs
    ]

    if not unexpected:
        return

    # Auto-cleanup: delete unexpected files (files only) and notify via shared notes
    deleted: list[str] = []
    skipped: list[str] = []
    for path in unexpected:
        try:
            if path.is_file():
                path.unlink(missing_ok=True)
                deleted.append(context.relative(path))
            else:
                skipped.append(context.relative(path))
        except Exception:
            skipped.append(context.relative(path))

    if deleted:
        note = (
            "ARTIFACT_CLEANUP: Deleted unexpected files created during database generation: "
            + ", ".join(sorted(deleted))
        )
        if note not in context.notes:
            context.notes.append(note)

    if skipped:
        note = (
            "ARTIFACT_CLEANUP: Detected unexpected non-file entries (left untouched): "
            + ", ".join(sorted(skipped))
        )
        if note not in context.notes:
            context.notes.append(note)

    # Do not fail the workflow; proceed after cleanup


def _purge_output_dir_unexpected(
    context: WorkflowContext,
    *,
    allowed: Set[Path],
    note_label: str = "PURGE",
) -> None:
    """Delete any files in the output directory that are not in the allowed set.

    - Only deletes files (not directories).
    - Records a coordination note describing deletions and any items skipped.
    """
    parent_dir = context.database_module_path.parent
    if not parent_dir.exists():
        return

    deleted: list[str] = []
    skipped: list[str] = []
    for entry in parent_dir.iterdir():
        resolved = entry.resolve()
        if resolved in allowed:
            continue
        try:
            if entry.is_file():
                entry.unlink(missing_ok=True)
                deleted.append(context.relative(resolved))
            else:
                skipped.append(context.relative(resolved))
        except Exception:
            skipped.append(context.relative(resolved))

    if deleted:
        note = (
            f"ARTIFACT_CLEANUP[{note_label}]: Deleted unexpected files: "
            + ", ".join(sorted(deleted))
        )
        if note not in context.notes:
            context.notes.append(note)

    if skipped:
        note = (
            f"ARTIFACT_CLEANUP[{note_label}]: Detected non-file entries (left untouched): "
            + ", ".join(sorted(skipped))
        )
        if note not in context.notes:
            context.notes.append(note)


def _ensure_recommended_paths_note(context: WorkflowContext) -> None:
    marker = "RECOMMENDED_PATHS:"
    if any(note.startswith(marker) for note in context.notes):
        return
    lines = [f"{key}: {context.relative(path)}" for key, path in sorted(context.recommended_paths.items())]
    payload = marker + "\n" + "\n".join(lines)
    context.notes.append(payload)


def _ensure_update_database_function(context: WorkflowContext) -> bool:
    module_path = context.database_module_path
    if not module_path.exists():
        _record_update_database_feedback(
            context,
            "Database module was not created; ensure the generator writes the module before proceeding.",
        )
        return False

    source = module_path.read_text(encoding="utf-8")

    try:
        tree = ast.parse(source, filename=str(module_path))
    except SyntaxError as exc:
        _record_update_database_feedback(
            context,
            "Database module contains syntax errors; fix them and add the required update_database helper.",
        )
        return False

    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == "update_database":
            if not node.args.args:
                _record_update_database_feedback(
                    context,
                    "update_database must accept an 'updates' argument describing the new records.",
                )
                return False

            first_arg = node.args.args[0].arg
            if first_arg != "updates":
                _record_update_database_feedback(
                    context,
                    "update_database must use 'updates' as its first parameter to match the documented contract.",
                )
                return False

            return True

    _record_update_database_feedback(
        context,
        "Database module must define an update_database(updates, ...) helper for manual data updates.",
    )
    return False


def _record_update_database_feedback(context: WorkflowContext, message: str) -> None:
    note = f"REVIEW_FEEDBACK: {message}"
    if note not in context.notes:
        context.notes.append(note)


def _record_model_behavior_warning(context: WorkflowContext, step_name: str, message: str) -> None:
    note = f"MODEL_WARNING[{step_name}]: {message}"
    if note not in context.notes:
        context.notes.append(note)


