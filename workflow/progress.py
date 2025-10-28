"""Real-time progress visualization for the workflow."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, TYPE_CHECKING

try:
    from rich.console import Console
    from rich.live import Live
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskID, TimeElapsedColumn
    from rich.layout import Layout
    from rich.text import Text
    from rich.tree import Tree
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

if TYPE_CHECKING:
    from .observability import ObservabilityTracker


class StageStatus(Enum):
    """Status of a workflow stage."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class StageInfo:
    """Information about a workflow stage."""
    name: str
    display_name: str
    status: StageStatus = StageStatus.PENDING
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    turns: int = 0
    tool_calls: int = 0
    cycle: Optional[int] = None
    message: str = ""
    
    @property
    def duration(self) -> Optional[float]:
        """Calculate duration in seconds."""
        if self.start_time is None:
            return None
        end = self.end_time or time.time()
        return end - self.start_time
    
    @property
    def formatted_duration(self) -> str:
        """Return human-readable duration."""
        if self.duration is None:
            return "-"
        
        duration = self.duration
        if duration < 60:
            return f"{duration:.1f}s"
        elif duration < 3600:
            minutes = int(duration // 60)
            seconds = int(duration % 60)
            return f"{minutes}m {seconds}s"
        else:
            hours = int(duration // 3600)
            minutes = int((duration % 3600) // 60)
            return f"{hours}h {minutes}m"


class ProgressVisualizer:
    """Real-time progress visualization using Rich."""
    
    def __init__(self, enabled: bool = True):
        self.enabled = enabled and RICH_AVAILABLE
        self.console = Console() if RICH_AVAILABLE else None
        self.live: Optional[Live] = None
        self.progress: Optional[Progress] = None
        self.task_id: Optional[TaskID] = None
        
        # Workflow state
        self.stages: Dict[str, StageInfo] = {}
        self.stage_order: List[str] = []
        self.current_stage: Optional[str] = None
        self.start_time = time.time()
        
        # Tool call history (last 10)
        self.recent_tool_calls: List[Dict[str, str]] = []
        self.max_recent_calls = 10
        
        # Refresh control (防抖)
        self._last_refresh = 0.0
        self._min_refresh_interval = 0.2  # 最小刷新间隔（秒）
        
        # Define stage structure
        self._init_stages()
    
    def _init_stages(self) -> None:
        """Initialize workflow stages."""
        stages = [
            ("planning", "📋 Schema Planning"),
            ("database_gen", "🗄️ Database Generation"),
            ("database_exec", "▶️ Database Execution"),
            ("server_gen", "⚙️ Server Implementation"),
            ("review", "👀 Code Review"),
            ("testing", "🧪 Integration Testing"),
        ]
        
        for stage_id, display_name in stages:
            self.stages[stage_id] = StageInfo(
                name=stage_id,
                display_name=display_name,
            )
            self.stage_order.append(stage_id)
    
    def start(self) -> None:
        """Start the progress visualization."""
        if not self.enabled:
            return
        
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=self.console,
        )
        
        self.task_id = self.progress.add_task(
            "[cyan]Workflow Progress",
            total=len(self.stage_order),
        )
        
        self.live = Live(
            self._build_layout(),
            console=self.console,
            refresh_per_second=2,  # 降低刷新频率避免闪烁
            transient=False,  # 保持显示不清除
        )
        self._last_refresh = time.time()  # 初始化刷新时间
        self.live.start()
    
    def stop(self) -> None:
        """Stop the progress visualization."""
        if self.live:
            self.live.stop()
            self.live = None
    
    def update_stage(
        self,
        stage_id: str,
        status: Optional[StageStatus] = None,
        message: Optional[str] = None,
        turns: Optional[int] = None,
        cycle: Optional[int] = None,
    ) -> None:
        """Update stage information."""
        if not self.enabled or stage_id not in self.stages:
            return
        
        stage = self.stages[stage_id]
        force_refresh = False  # 是否强制刷新
        
        if status is not None:
            old_status = stage.status
            stage.status = status
            
            if status == StageStatus.IN_PROGRESS and old_status != StageStatus.IN_PROGRESS:
                stage.start_time = time.time()
                self.current_stage = stage_id
                force_refresh = True  # 状态变化时强制刷新
            elif status in (StageStatus.COMPLETED, StageStatus.FAILED, StageStatus.SKIPPED):
                stage.end_time = time.time()
                if self.current_stage == stage_id:
                    self.current_stage = None
                
                # Update progress bar
                if self.progress and self.task_id is not None:
                    completed = sum(
                        1 for s in self.stages.values()
                        if s.status in (StageStatus.COMPLETED, StageStatus.SKIPPED)
                    )
                    self.progress.update(self.task_id, completed=completed)
                force_refresh = True  # 状态变化时强制刷新
        
        if message is not None:
            stage.message = message
        
        if turns is not None:
            stage.turns = turns
        
        if cycle is not None:
            stage.cycle = cycle
        
        self._refresh(force=force_refresh)
    
    def record_tool_call(self, agent_name: str, tool_name: str, stage_id: Optional[str] = None) -> None:
        """Record a tool call."""
        if not self.enabled:
            return
        
        # Update stage tool call count
        if stage_id and stage_id in self.stages:
            self.stages[stage_id].tool_calls += 1
        
        # Add to recent calls
        self.recent_tool_calls.append({
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "agent": agent_name,
            "tool": tool_name,
        })
        
        # Keep only last N calls
        if len(self.recent_tool_calls) > self.max_recent_calls:
            self.recent_tool_calls.pop(0)
        
        # 工具调用很频繁，使用防抖刷新（不强制）
        self._refresh(force=False)
    
    def _build_layout(self) -> Layout:
        """Build the rich layout."""
        layout = Layout()
        
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body"),
            Layout(name="footer", size=3),
        )
        
        # Header
        elapsed = time.time() - self.start_time
        elapsed_str = self._format_duration(elapsed)
        header_text = Text(f"🚀 MCP Workflow Execution  |  Elapsed: {elapsed_str}", style="bold cyan")
        layout["header"].update(Panel(header_text, border_style="cyan"))
        
        # Body
        body_layout = Layout()
        body_layout.split_row(
            Layout(name="stages", ratio=2),
            Layout(name="tools", ratio=1),
        )
        
        # Stages table
        stages_table = self._build_stages_table()
        body_layout["stages"].update(Panel(stages_table, title="Workflow Stages", border_style="blue"))
        
        # Recent tool calls
        tools_tree = self._build_tools_tree()
        body_layout["tools"].update(Panel(tools_tree, title="Recent Tool Calls", border_style="green"))
        
        layout["body"].update(body_layout)
        
        # Footer with progress bar
        if self.progress:
            layout["footer"].update(self.progress)
        
        return layout
    
    def _build_stages_table(self) -> Table:
        """Build the stages status table."""
        table = Table(show_header=True, header_style="bold magenta", box=None)
        table.add_column("Stage", style="cyan", width=25)
        table.add_column("Status", width=12)
        table.add_column("Duration", width=10)
        table.add_column("Turns", justify="right", width=6)
        table.add_column("Tools", justify="right", width=6)
        table.add_column("Info", style="dim")
        
        for stage_id in self.stage_order:
            stage = self.stages[stage_id]
            
            # Status with icon
            status_icons = {
                StageStatus.PENDING: "⏳",
                StageStatus.IN_PROGRESS: "▶️",
                StageStatus.COMPLETED: "✅",
                StageStatus.FAILED: "❌",
                StageStatus.SKIPPED: "⏭️",
            }
            status_colors = {
                StageStatus.PENDING: "dim",
                StageStatus.IN_PROGRESS: "yellow",
                StageStatus.COMPLETED: "green",
                StageStatus.FAILED: "red",
                StageStatus.SKIPPED: "blue",
            }
            
            icon = status_icons[stage.status]
            color = status_colors[stage.status]
            status_text = f"[{color}]{icon} {stage.status.value}[/{color}]"
            
            # Build info message
            info_parts = []
            if stage.cycle is not None:
                info_parts.append(f"Cycle {stage.cycle}")
            if stage.message:
                info_parts.append(stage.message[:30])
            info = " | ".join(info_parts) if info_parts else ""
            
            table.add_row(
                stage.display_name,
                status_text,
                stage.formatted_duration,
                str(stage.turns) if stage.turns > 0 else "-",
                str(stage.tool_calls) if stage.tool_calls > 0 else "-",
                info,
            )
        
        return table
    
    def _build_tools_tree(self) -> Tree:
        """Build recent tool calls tree."""
        tree = Tree("🔧 Tool Activity")
        
        if not self.recent_tool_calls:
            tree.add("[dim]No tool calls yet[/dim]")
            return tree
        
        # Show most recent first
        for call in reversed(self.recent_tool_calls[-5:]):
            node_text = f"[cyan]{call['timestamp']}[/cyan] [{call['agent']}] → [green]{call['tool']}[/green]"
            tree.add(node_text)
        
        return tree
    
    def _refresh(self, force: bool = False) -> None:
        """Refresh the display with debouncing.
        
        Args:
            force: Force refresh regardless of interval
        """
        if not self.live or not self.enabled:
            return
        
        current_time = time.time()
        
        # 防抖：只有距离上次刷新超过最小间隔才刷新
        if not force and (current_time - self._last_refresh) < self._min_refresh_interval:
            return
        
        self._last_refresh = current_time
        self.live.update(self._build_layout())
    
    def _format_duration(self, duration: float) -> str:
        """Format duration in human-readable form."""
        if duration < 60:
            return f"{int(duration)}s"
        elif duration < 3600:
            minutes = int(duration // 60)
            seconds = int(duration % 60)
            return f"{minutes}m {seconds}s"
        else:
            hours = int(duration // 3600)
            minutes = int((duration % 3600) // 60)
            return f"{hours}h {minutes}m"
    
    def print_summary(self) -> None:
        """Print final summary."""
        if not self.enabled:
            return
        
        self.console.print("\n" + "="*80, style="cyan")
        self.console.print("📊 Workflow Summary", style="bold cyan", justify="center")
        self.console.print("="*80 + "\n", style="cyan")
        
        # Summary table
        summary_table = Table(show_header=True, header_style="bold magenta")
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value", justify="right")
        
        total_duration = time.time() - self.start_time
        completed = sum(1 for s in self.stages.values() if s.status == StageStatus.COMPLETED)
        failed = sum(1 for s in self.stages.values() if s.status == StageStatus.FAILED)
        total_tool_calls = sum(s.tool_calls for s in self.stages.values())
        
        summary_table.add_row("Total Duration", self._format_duration(total_duration))
        summary_table.add_row("Completed Stages", f"{completed}/{len(self.stages)}")
        summary_table.add_row("Failed Stages", str(failed))
        summary_table.add_row("Total Tool Calls", str(total_tool_calls))
        
        self.console.print(summary_table)
        self.console.print()


class SimpleProgressTracker:
    """Simple text-based progress tracker (fallback when rich is not available)."""
    
    def __init__(self):
        self.start_time = time.time()
        self.current_stage: Optional[str] = None
    
    def start(self) -> None:
        """Start tracking."""
        print("="*60)
        print("🚀 MCP Workflow Execution Started")
        print("="*60)
    
    def stop(self) -> None:
        """Stop tracking."""
        elapsed = time.time() - self.start_time
        print("\n" + "="*60)
        print(f"✅ Workflow Completed in {elapsed:.1f}s")
        print("="*60)
    
    def update_stage(
        self,
        stage_id: str,
        status: Optional[StageStatus] = None,
        message: Optional[str] = None,
        **kwargs,
    ) -> None:
        """Update stage."""
        if status == StageStatus.IN_PROGRESS:
            print(f"\n▶️  {stage_id}: {message or 'Starting...'}")
            self.current_stage = stage_id
        elif status == StageStatus.COMPLETED:
            print(f"✅ {stage_id}: Completed")
        elif status == StageStatus.FAILED:
            print(f"❌ {stage_id}: Failed")
    
    def record_tool_call(self, agent_name: str, tool_name: str, **kwargs) -> None:
        """Record tool call."""
        print(f"   🔧 [{agent_name}] {tool_name}")
    
    def print_summary(self) -> None:
        """Print summary."""
        pass  # Already printed in stop()


def create_progress_tracker(enabled: bool = True) -> ProgressVisualizer | SimpleProgressTracker:
    """Create appropriate progress tracker based on availability."""
    if enabled and RICH_AVAILABLE:
        return ProgressVisualizer(enabled=True)
    else:
        return SimpleProgressTracker()


__all__ = [
    "ProgressVisualizer",
    "SimpleProgressTracker",
    "StageStatus",
    "StageInfo",
    "create_progress_tracker",
    "RICH_AVAILABLE",
]

