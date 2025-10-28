from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from agents import Agent
from agents.models.interface import Model

from .context import WorkflowContext
from .tools import (
    describe_schema,
    ensure_dir,
    get_notes,
    get_recommended_paths,
    list_directory,
    read_text,
    record_note,
    run_python,
    write_text,
    write_json,
)


@dataclass
class AgentSuite:
    schema_planner: Agent[Any]
    dataset_builder: Agent[Any]
    server_builder: Agent[Any]
    reviewer: Agent[Any]
    dataset_executor: Agent[Any]
    test_agent: Agent[Any]


def build_agent_suite(context: WorkflowContext, model: Model) -> AgentSuite:
    # Get prompts from context config
    prompts = context.config.prompts if context.config else None
    if prompts is None:
        from .config import load_config
        prompts = load_config().prompts
    
    schema_planner = Agent(
        name="Schema Planner",
        instructions=prompts.schema_planner,
        tools=[describe_schema, get_recommended_paths, record_note, get_notes],
        model=model,
    )

    dataset_builder = Agent(
        name="Database Synthesizer",
        instructions=prompts.dataset_builder,
        tools=[get_recommended_paths, ensure_dir, write_text, read_text, list_directory, get_notes, record_note],
        model=model,
    )

    server_builder = Agent(
        name="Server Builder",
        instructions=prompts.server_builder,
        tools=[get_notes, get_recommended_paths, ensure_dir, write_text, write_json, read_text, list_directory],
        model=model,
    )

    reviewer = Agent(
        name="Code Reviewer",
        instructions=prompts.reviewer,
        tools=[read_text, get_recommended_paths, get_notes, record_note],
        model=model,
    )

    dataset_executor = Agent(
        name="Database Executor",
        instructions=prompts.dataset_executor,
        tools=[run_python, read_text, get_recommended_paths, record_note, get_notes, list_directory],
        model=model,
    )

    test_agent = Agent(
        name="Test Agent",
        instructions=prompts.test_agent,
        tools=[ensure_dir, write_text, read_text, run_python, get_recommended_paths, get_notes],
        model=model,
    )

    return AgentSuite(
        schema_planner=schema_planner,
        dataset_builder=dataset_builder,
        server_builder=server_builder,
        reviewer=reviewer,
        dataset_executor=dataset_executor,
        test_agent=test_agent,
    )


__all__ = ["AgentSuite", "build_agent_suite"]




