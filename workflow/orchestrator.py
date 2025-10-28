from __future__ import annotations

import json
import re
from dataclasses import dataclass
from textwrap import dedent
from typing import Any, Dict, List

from agents import Runner
from agents.items import ToolCallItem, ToolCallOutputItem
from agents.run import RunConfig

from .agents import AgentSuite
from .context import WorkflowContext
from .logging_utils import get_workflow_logger


@dataclass
class StepResult:
    name: str
    description: str
    output: str

async def _run_agent_step(
    *,
    name: str,
    agent,
    prompt: str,
    context: WorkflowContext,
    max_turns: int,
    workflow_slug: str,
) -> StepResult:
    logger = get_workflow_logger()
    run_config = RunConfig(workflow_name=f"offline-mcp::{workflow_slug}::{name}")

    logger.info(
        "[%s] starting (max_turns=%s). Prompt: %s",
        name,
        max_turns,
        prompt.strip(),
    )
    try:
        result = await Runner.run(
            agent,
            prompt,
            context=context,
            run_config=run_config,
            max_turns=max_turns,
        )
    except Exception as exc:
        logger.exception("[%s] failed with error", name)
        raise

    output_text = result.final_output if result.final_output is not None else "(no final output)"
    logger.info(
        "[%s] completed. Output: %s",
        name,
        output_text,
    )
    _log_tool_activity(name, result)
    return StepResult(name=name, description=prompt, output=output_text.strip())


async def execute_workflow(
    *,
    context: WorkflowContext,
    agents: AgentSuite,
    goal_prompt: str,
    max_turns: int,
) -> List[StepResult]:
    logger = get_workflow_logger()
    step_results: List[StepResult] = []

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
        Document the required metadata JSON schema (tool name, description, input_schema, output_schema with `type`, `properties`, and `required`) so builders align on structure.
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
        )
    )

    if not any(note.strip().upper().startswith("DATA CONTRACT") for note in context.notes):
        raise RuntimeError(
            "Schema planning must record a DATA CONTRACT note detailing the offline database structure before continuing."
        )
    context.data_contract = _load_data_contract(context)

    review_feedback: str | None = None
    max_review_cycles = 3
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
                )
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
                )
            )
            _validate_database_against_contract(context)
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
        step_results.append(
            await _run_agent_step(
                name=f"server_generation_cycle_{cycle + 1}",
                agent=agents.server_builder,
                prompt=server_prompt,
                context=context,
                max_turns=max_turns,
                workflow_slug=context.slug,
            )
        )
        _validate_metadata_against_expected_tools(context)

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
        )
        step_results.append(review_result)

        verdict_text = review_result.output
        if _is_approved(verdict_text):
            review_feedback = None
            logger.info("[code_review_cycle_%s] Review approved, proceeding.", cycle + 1)
            break

        review_feedback = verdict_text
        new_feedback_items = _extract_review_feedback_items(verdict_text)
        _record_review_feedback_notes(context, new_feedback_items, verdict_text)
        needs_database_update = _database_revision_requested(review_feedback)
        logger.info(
            "[code_review_cycle_%s] Review requested revisions; iterating...",
            cycle + 1,
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
        )
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
        return "\n\n最新的审查反馈，请逐项处理：\n" + bullet_lines + "\n"
    cleaned = raw_feedback.strip()
    if cleaned:
        return "\n\n审查反馈：\n" + cleaned + "\n"
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


def _database_revision_requested(feedback: str) -> bool:
    lowered = feedback.lower()
    if not any(term in lowered for term in ("database", "dataset", "data contract")):
        return False
    negative_indicators = [
        "mismatch",
        "issue",
        "problem",
        "needs",
        "fix",
        "update",
        "incorrect",
        "missing",
        "violation",
        "inconsistent",
        "error",
    ]
    return any(indicator in lowered for indicator in negative_indicators)


def _is_approved(feedback: str) -> bool:
    for line in feedback.splitlines():
        clean = line.strip()
        if not clean:
            continue
        while clean and clean[0] in "*_`-:> ":
            clean = clean[1:]
        if not clean:
            continue
        return clean.upper().startswith("APPROVED")
    return False


def _log_tool_activity(step_name: str, result) -> None:
    logger = get_workflow_logger()
    tool_calls: list[str] = []
    tool_outputs: list[str] = []

    for item in getattr(result, "new_items", []):
        if isinstance(item, ToolCallItem):
            function = getattr(item.raw_item, "function", None)
            name = getattr(function, "name", None)
            if not name and hasattr(item.raw_item, "name"):
                name = getattr(item.raw_item, "name", None)
            if not name:
                name = getattr(item.raw_item, "type", "unknown")
            tool_calls.append(str(name))
        elif isinstance(item, ToolCallOutputItem):
            tool_name = getattr(item.raw_item, "call_id", None)
            summary = item.output
            if isinstance(summary, dict):
                summary = summary.get("result") or summary.get("message") or "dict"
            tool_outputs.append(f"{tool_name or 'tool'} -> {summary}")

    if tool_calls:
        logger.info("[%s] tool calls: %s", step_name, ", ".join(tool_calls))
    else:
        logger.info("[%s] tool calls: (none)", step_name)

    if tool_outputs:
        logger.info("[%s] tool outputs: %s", step_name, "; ".join(tool_outputs))


def _load_data_contract(context: WorkflowContext) -> Dict[str, Any]:
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
            raise RuntimeError("DATA CONTRACT note is present but empty.")
        try:
            contract = json.loads(payload)
        except json.JSONDecodeError as exc:
            raise RuntimeError("DATA CONTRACT note is not valid JSON.") from exc
        if not isinstance(contract, dict):
            raise RuntimeError("DATA CONTRACT note must decode to an object.")
        context.data_contract = contract
        logger.info("Loaded DATA CONTRACT with keys: %s", ", ".join(contract.keys()))
        return contract
    raise RuntimeError("DATA CONTRACT note not found in planner output.")


def _validate_database_against_contract(context: WorkflowContext) -> None:
    logger = get_workflow_logger()
    contract = _load_data_contract(context)
    database_path = context.database_json_path
    if not database_path.exists():
        raise RuntimeError(
            f"Database JSON not found at {context.relative(database_path)} after database synthesis."
        )
    try:
        database_data = json.loads(database_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"Database JSON at {context.relative(database_path)} is not valid JSON."
        ) from exc

    expected_keys = contract.get("top_level_keys")
    if not isinstance(expected_keys, list) or not all(isinstance(item, str) for item in expected_keys):
        raise RuntimeError("DATA CONTRACT must include a string list under `top_level_keys`.")

    missing = sorted(key for key in expected_keys if key not in database_data)
    if missing:
        raise RuntimeError(
            "Database JSON is missing required DATA CONTRACT keys: " + ", ".join(missing)
        )

    if context.sample_database_path and context.sample_database_path.exists():
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

    logger.info(
        "Validated database JSON against DATA CONTRACT (%s top-level keys).",
        len(expected_keys),
    )


def _validate_metadata_against_expected_tools(context: WorkflowContext) -> None:
    logger = get_workflow_logger()
    metadata_path = context.metadata_json_path
    if not metadata_path.exists():
        raise RuntimeError(
            f"Metadata JSON not found at {context.relative(metadata_path)} after server generation."
        )

    try:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"Metadata JSON at {context.relative(metadata_path)} is not valid JSON."
        ) from exc

    tools = metadata.get("tools")
    if not isinstance(tools, list):
        raise RuntimeError("Metadata JSON must contain a `tools` list.")

    observed_tool_names = {
        tool.get("name")
        for tool in tools
        if isinstance(tool, dict) and tool.get("name")
    }
    expected_tool_names = {name for name in context.expected_tool_names if name}

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

    logger.info(
        "Validated metadata tool coverage (%s tools).",
        len(observed_tool_names),
    )


