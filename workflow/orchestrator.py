from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List

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

    dataset_module_rel = context.relative(context.dataset_module_path)
    dataset_json_rel = context.relative(context.dataset_json_path)
    server_module_rel = context.relative(context.server_module_path)
    metadata_json_rel = context.relative(context.metadata_json_path)
    tests_dir_rel = context.relative(context.tests_dir)

    planner_prompt = (
        f"{goal_prompt}\n\n"
        "You are the Schema Planner. Analyze the schema file and produce an actionable plan. "
        "Use `describe_schema` and `get_recommended_paths` for context, and capture concrete tasks for "
        "later agents via `record_note` so they can reference the notes. Be explicit about dataset synthesis, "
        "server implementation, metadata JSON production, and testing requirements. You MUST record at least one "
        "`DATA CONTRACT` note that lists the exact dataset structure (top-level keys, important nested fields, and "
        "types) that all agents must follow—do not proceed without writing this note. Record open questions if "
        "expectations are unclear. Return a succinct plan summary after confirming the DATA CONTRACT note exists."
    )
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
            "Schema planning must record a DATA CONTRACT note detailing the dataset structure before continuing."
        )

    review_feedback: str | None = None
    max_review_cycles = 3
    needs_dataset_update = True
    for cycle in range(max_review_cycles):
        builder_suffix = (
            ""
            if not review_feedback
            else "\n\nAddress the following review feedback before finalizing:\n"
            f"{review_feedback}\n"
        )

        if needs_dataset_update:
            dataset_prompt = (
                f"Generate or update the dataset synthesis module at `{dataset_module_rel}` and ensure it writes JSON "
                f"to `{dataset_json_rel}`. Rely on planning notes (`get_notes`) and verify the schema expectations. "
                "Implement deterministic data generation when a seed is provided. Read the DATA CONTRACT note before "
                "coding and ensure the written JSON matches the documented keys precisely. If the contract is missing "
                "details, record a clarifying note before continuing. Limit file writes to the recommended dataset "
                "module and dataset JSON paths—capture any additional context in transcripts or shared notes instead."
                f"{builder_suffix}"
            )
            step_results.append(
                await _run_agent_step(
                    name=f"dataset_generation_cycle_{cycle + 1}",
                    agent=agents.dataset_builder,
                    prompt=dataset_prompt,
                    context=context,
                    max_turns=max_turns,
                    workflow_slug=context.slug,
                )
            )
            needs_dataset_update = False
        else:
            logger.info(
                "[dataset_generation_cycle_%s] Skipping dataset generation; no dataset revisions requested.",
                cycle + 1,
            )

        server_prompt = (
            f"Implement or refine the FastMCP server module at `{server_module_rel}` backed by the offline dataset. "
            "Ensure the module exposes the tools described in the schema, depends solely on local data, "
            "and stays aligned with any documented notes. Always load the generated dataset from `{dataset_json_rel}` "
            "according to the DATA CONTRACT note, validate required keys exist, and only fall back to inline defaults "
            "if the JSON file is missing or malformed. Remove or update any hardcoded structures that diverge from the "
            "shared contract. "
            f"Also produce a metadata JSON file at `{metadata_json_rel}` containing every tool's name, description, "
            "input schema, and output schema so downstream workflows can inspect the server surface area."
            "Do not author extra helper modules or documentation outside the recommended paths; store supplementary "
            "materials in the transcripts directory or notes. "
            f"{builder_suffix}"
        )
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

        review_prompt = (
            "Thoroughly review the generated dataset module, server module, and metadata JSON file. "
            "Use `read_text` to inspect code, cross-check against schema expectations, and confirm the metadata "
            "accurately lists tool name, description, input schema, and output schema. Verify the dataset generator, "
            "produced JSON, and server module all adhere to the shared DATA CONTRACT note, and ensure the server "
            "loads the generated JSON rather than relying on divergent defaults. Inspect the recommended directories "
            "to ensure no stray helper files were created outside the approved paths; note any extras that should be "
            "moved to transcripts. "
            "If everything looks good, respond with `APPROVED:` followed by a short justification. "
            "If revisions are required, respond with `REVISIONS_NEEDED:` and list concrete fixes. "
            "Record essential feedback with `record_note` so builders can iterate."
        )
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
        needs_dataset_update = _dataset_revision_requested(review_feedback)
        logger.info(
            "[code_review_cycle_%s] Review requested revisions; iterating...",
            cycle + 1,
        )
    else:
        raise RuntimeError(
            "Code review did not pass after multiple iterations. Check review feedback notes for details."
        )

    executor_prompt = (
        f"Run the dataset synthesis module `{dataset_module_rel}` so that it writes `{dataset_json_rel}` to disk. "
        "Use `run_python` on the dataset module, confirm the JSON file exists, and compare its top-level structure "
        "against the DATA CONTRACT note. Record a summary note including any mismatches."
    )
    step_results.append(
        await _run_agent_step(
            name="dataset_execution",
            agent=agents.dataset_executor,
            prompt=executor_prompt,
            context=context,
            max_turns=max_turns,
            workflow_slug=context.slug,
        )
    )

    test_prompt = (
        f"Write and execute automated tests ensuring the FastMCP server works with the offline dataset. "
        f"Place tests under `{tests_dir_rel}`, run them with `run_python` (`pytest`) targeting that directory, "
        f"and verify the metadata JSON at `{metadata_json_rel}` remains aligned with the server's exposed tools. "
        "Ensure tests import the server module, load the generated dataset JSON, and assert the DATA CONTRACT keys "
        "exist and are consumed correctly. Keep all test artifacts within the tests directory and record extra "
        "findings via transcripts or notes. "
        "Summarize the results and highlight any remaining issues."
    )
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


def _dataset_revision_requested(feedback: str) -> bool:
    lowered = feedback.lower()
    if not any(term in lowered for term in ("dataset", "data contract")):
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
