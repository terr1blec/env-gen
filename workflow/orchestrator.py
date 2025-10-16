from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List

from agents import Runner
from agents.run import RunConfig

from .agents import AgentSuite
from .context import WorkflowContext
from .logging_utils import get_workflow_logger


@dataclass
class StepResult:
    name: str
    description: str
    output: str


def _shorten(text: str, limit: int = 280) -> str:
    clean = " ".join(text.strip().split())
    if len(clean) <= limit:
        return clean
    return clean[: limit - 3] + "..."


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
        "[%s] starting (max_turns=%s). Prompt excerpt: %s",
        name,
        max_turns,
        _shorten(prompt, 180),
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
        "[%s] completed. Output excerpt: %s",
        name,
        _shorten(output_text, 200),
    )
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
    tests_dir_rel = context.relative(context.tests_dir)

    planner_prompt = (
        f"{goal_prompt}\n\n"
        "You are the Schema Planner. Analyze the schema file and produce an actionable plan. "
        "Use `describe_schema` and `get_recommended_paths` for context, and capture concrete tasks for "
        "later agents via `record_note` so they can reference the notes. Return a succinct plan summary."
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

    review_feedback: str | None = None
    max_review_cycles = 3
    for cycle in range(max_review_cycles):
        builder_suffix = (
            ""
            if not review_feedback
            else "\n\nAddress the following review feedback before finalizing:\n"
            f"{review_feedback}\n"
        )

        dataset_prompt = (
            f"Generate or update the dataset synthesis module at `{dataset_module_rel}` and ensure it writes JSON "
            f"to `{dataset_json_rel}`. Rely on planning notes (`get_notes`) and verify the schema expectations. "
            "Implement deterministic data generation when a seed is provided."
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

        server_prompt = (
            f"Implement or refine the FastMCP server module at `{server_module_rel}` backed by the offline dataset. "
            "Ensure the module exposes the tools described in the schema, depends solely on local data, "
            "and stays aligned with any documented notes."
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
            "Thoroughly review the generated dataset and server modules. "
            "Use `read_text` to inspect code, cross-check against schema expectations, and summarize findings. "
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

        verdict = review_result.output.upper()
        if verdict.startswith("APPROVED"):
            review_feedback = None
            logger.info("[code_review_cycle_%s] Review approved, proceeding.", cycle + 1)
            break

        review_feedback = review_result.output
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
        "Use `run_python` on the dataset module, confirm the JSON file exists, and record a summary note."
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
        f"Place tests under `{tests_dir_rel}`, run them with `run_python` (`pytest`), "
        "and summarize the results. Highlight any remaining issues."
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
