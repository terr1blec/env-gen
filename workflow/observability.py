"""Observability and tracing for the workflow system."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .context import WorkflowContext


class EventType(Enum):
    """Types of observable events."""
    AGENT_START = "agent_start"
    AGENT_END = "agent_end"
    AGENT_TURN = "agent_turn"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    DECISION_POINT = "decision_point"
    VALIDATION = "validation"
    ERROR = "error"
    NOTE = "note"


@dataclass
class ObservabilityEvent:
    """A single observable event in the workflow."""
    
    timestamp: float
    event_type: EventType
    agent_name: Optional[str] = None
    step_name: Optional[str] = None
    cycle: Optional[int] = None
    turn: Optional[int] = None
    
    # Tool-related
    tool_name: Optional[str] = None
    tool_args: Optional[Dict[str, Any]] = None
    tool_result: Optional[Any] = None
    tool_duration: Optional[float] = None
    
    # Decision-related
    decision: Optional[str] = None
    reasoning: Optional[str] = None
    
    # General
    message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Convert EventType string to enum if needed."""
        if isinstance(self.event_type, str):
            self.event_type = EventType(self.event_type)
    
    @property
    def formatted_timestamp(self) -> str:
        """Return human-readable timestamp."""
        return datetime.fromtimestamp(self.timestamp).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return {
            "timestamp": self.timestamp,
            "formatted_timestamp": self.formatted_timestamp,
            "event_type": self.event_type.value,
            "agent_name": self.agent_name,
            "step_name": self.step_name,
            "cycle": self.cycle,
            "turn": self.turn,
            "tool_name": self.tool_name,
            "tool_args": self.tool_args,
            "tool_result": self.tool_result,
            "tool_duration": self.tool_duration,
            "decision": self.decision,
            "reasoning": self.reasoning,
            "message": self.message,
            "metadata": self.metadata,
        }
    
    def to_json(self) -> str:
        """Convert event to JSON string."""
        return json.dumps(self.to_dict(), indent=2, default=str)


@dataclass
class AgentTrace:
    """Trace information for a single agent execution."""
    
    agent_name: str
    step_name: str
    start_time: float
    end_time: Optional[float] = None
    turns: int = 0
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)
    decisions: List[Dict[str, Any]] = field(default_factory=list)
    output: Optional[str] = None
    
    @property
    def duration(self) -> Optional[float]:
        """Calculate duration in seconds."""
        if self.end_time is None:
            return None
        return self.end_time - self.start_time
    
    @property
    def formatted_duration(self) -> str:
        """Return human-readable duration."""
        if self.duration is None:
            return "in progress"
        
        duration = self.duration
        if duration < 60:
            return f"{duration:.2f}s"
        elif duration < 3600:
            minutes = int(duration // 60)
            seconds = duration % 60
            return f"{minutes}m {seconds:.1f}s"
        else:
            hours = int(duration // 3600)
            minutes = int((duration % 3600) // 60)
            return f"{hours}h {minutes}m"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert trace to dictionary."""
        return {
            "agent_name": self.agent_name,
            "step_name": self.step_name,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration,
            "formatted_duration": self.formatted_duration,
            "turns": self.turns,
            "tool_calls_count": len(self.tool_calls),
            "decisions_count": len(self.decisions),
            "tool_calls": self.tool_calls,
            "decisions": self.decisions,
            "output": self.output,
        }


class ObservabilityTracker:
    """Central tracker for workflow observability."""
    
    def __init__(self, context: WorkflowContext):
        self.context = context
        self.events: List[ObservabilityEvent] = []
        self.traces: Dict[str, AgentTrace] = {}
        self.current_trace: Optional[AgentTrace] = None
        self.start_time = time.time()
        self._trace_file: Optional[Path] = None
        
        # Initialize trace file
        if context.logs_dir:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self._trace_file = context.logs_dir / f"trace_{timestamp}.jsonl"
    
    def record_event(self, event: ObservabilityEvent) -> None:
        """Record an observable event."""
        self.events.append(event)
        
        # Write to trace file immediately for real-time monitoring
        if self._trace_file:
            try:
                with open(self._trace_file, 'a', encoding='utf-8') as f:
                    f.write(event.to_json() + '\n')
            except Exception:
                pass  # Don't fail workflow due to tracing issues
    
    def start_agent(
        self,
        agent_name: str,
        step_name: str,
        cycle: Optional[int] = None,
        prompt: Optional[str] = None,
    ) -> None:
        """Record agent start."""
        trace = AgentTrace(
            agent_name=agent_name,
            step_name=step_name,
            start_time=time.time(),
        )
        self.traces[step_name] = trace
        self.current_trace = trace
        
        self.record_event(ObservabilityEvent(
            timestamp=time.time(),
            event_type=EventType.AGENT_START,
            agent_name=agent_name,
            step_name=step_name,
            cycle=cycle,
            message=f"Starting {agent_name} for {step_name}",
            metadata={"prompt": prompt[:200] if prompt else None},
        ))
    
    def end_agent(
        self,
        step_name: str,
        output: Optional[str] = None,
        success: bool = True,
    ) -> None:
        """Record agent completion."""
        trace = self.traces.get(step_name)
        if trace:
            trace.end_time = time.time()
            trace.output = output
        
        self.record_event(ObservabilityEvent(
            timestamp=time.time(),
            event_type=EventType.AGENT_END,
            agent_name=trace.agent_name if trace else None,
            step_name=step_name,
            message=f"Completed {step_name}",
            metadata={
                "success": success,
                "output": output[:200] if output else None,
                "duration": trace.duration if trace else None,
            },
        ))
        
        if self.current_trace and self.current_trace.step_name == step_name:
            self.current_trace = None
    
    def record_turn(self, step_name: str, turn: int) -> None:
        """Record agent turn."""
        trace = self.traces.get(step_name)
        if trace:
            trace.turns = turn
        
        self.record_event(ObservabilityEvent(
            timestamp=time.time(),
            event_type=EventType.AGENT_TURN,
            agent_name=trace.agent_name if trace else None,
            step_name=step_name,
            turn=turn,
            message=f"Turn {turn}",
        ))
    
    def record_tool_call(
        self,
        step_name: str,
        tool_name: str,
        tool_args: Dict[str, Any],
        turn: Optional[int] = None,
    ) -> float:
        """Record tool call start and return start time."""
        start_time = time.time()
        
        self.record_event(ObservabilityEvent(
            timestamp=start_time,
            event_type=EventType.TOOL_CALL,
            agent_name=self.current_trace.agent_name if self.current_trace else None,
            step_name=step_name,
            turn=turn,
            tool_name=tool_name,
            tool_args=tool_args,
            message=f"Calling {tool_name}",
        ))
        
        return start_time
    
    def record_tool_result(
        self,
        step_name: str,
        tool_name: str,
        result: Any,
        start_time: float,
        turn: Optional[int] = None,
    ) -> None:
        """Record tool call result."""
        duration = time.time() - start_time
        
        trace = self.traces.get(step_name)
        if trace:
            trace.tool_calls.append({
                "tool_name": tool_name,
                "duration": duration,
                "timestamp": start_time,
            })
        
        # Truncate large results
        result_preview = str(result)
        if len(result_preview) > 500:
            result_preview = result_preview[:500] + "..."
        
        self.record_event(ObservabilityEvent(
            timestamp=time.time(),
            event_type=EventType.TOOL_RESULT,
            agent_name=self.current_trace.agent_name if self.current_trace else None,
            step_name=step_name,
            turn=turn,
            tool_name=tool_name,
            tool_result=result_preview,
            tool_duration=duration,
            message=f"Completed {tool_name} in {duration:.2f}s",
        ))
    
    def record_decision(
        self,
        step_name: str,
        decision: str,
        reasoning: Optional[str] = None,
    ) -> None:
        """Record an important decision point."""
        trace = self.traces.get(step_name)
        if trace:
            trace.decisions.append({
                "decision": decision,
                "reasoning": reasoning,
                "timestamp": time.time(),
            })
        
        self.record_event(ObservabilityEvent(
            timestamp=time.time(),
            event_type=EventType.DECISION_POINT,
            agent_name=self.current_trace.agent_name if self.current_trace else None,
            step_name=step_name,
            decision=decision,
            reasoning=reasoning,
            message=f"Decision: {decision}",
        ))
    
    def record_validation(
        self,
        validation_type: str,
        success: bool,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Record a validation check."""
        self.record_event(ObservabilityEvent(
            timestamp=time.time(),
            event_type=EventType.VALIDATION,
            message=message,
            metadata={
                "validation_type": validation_type,
                "success": success,
                "details": details,
            },
        ))
    
    def record_error(
        self,
        error: Exception,
        step_name: Optional[str] = None,
    ) -> None:
        """Record an error."""
        self.record_event(ObservabilityEvent(
            timestamp=time.time(),
            event_type=EventType.ERROR,
            agent_name=self.current_trace.agent_name if self.current_trace else None,
            step_name=step_name,
            message=str(error),
            metadata={
                "error_type": type(error).__name__,
                "error_details": str(error),
            },
        ))
    
    def record_note(self, message: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Record a general note."""
        self.record_event(ObservabilityEvent(
            timestamp=time.time(),
            event_type=EventType.NOTE,
            message=message,
            metadata=metadata or {},
        ))
    
    def get_summary(self) -> Dict[str, Any]:
        """Get workflow summary statistics."""
        total_duration = time.time() - self.start_time
        
        tool_calls_by_agent: Dict[str, int] = {}
        for trace in self.traces.values():
            tool_calls_by_agent[trace.agent_name] = len(trace.tool_calls)
        
        return {
            "total_duration": total_duration,
            "formatted_duration": self._format_duration(total_duration),
            "total_events": len(self.events),
            "total_agents": len(self.traces),
            "tool_calls_by_agent": tool_calls_by_agent,
            "traces": {name: trace.to_dict() for name, trace in self.traces.items()},
        }
    
    def _format_duration(self, duration: float) -> str:
        """Format duration in human-readable form."""
        if duration < 60:
            return f"{duration:.2f}s"
        elif duration < 3600:
            minutes = int(duration // 60)
            seconds = duration % 60
            return f"{minutes}m {seconds:.1f}s"
        else:
            hours = int(duration // 3600)
            minutes = int((duration % 3600) // 60)
            return f"{hours}h {minutes}m"
    
    def export_trace(self, output_path: Path) -> None:
        """Export full trace to JSON file."""
        trace_data = {
            "workflow_slug": self.context.slug,
            "start_time": self.start_time,
            "summary": self.get_summary(),
            "events": [event.to_dict() for event in self.events],
        }
        
        output_path.write_text(
            json.dumps(trace_data, indent=2, default=str),
            encoding='utf-8'
        )


__all__ = [
    "ObservabilityTracker",
    "ObservabilityEvent",
    "AgentTrace",
    "EventType",
]

