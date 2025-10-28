"""Configuration management for the workflow system."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


@dataclass
class AgentPrompts:
    """Container for agent prompt templates."""
    
    schema_planner: str = ""
    dataset_builder: str = ""
    server_builder: str = ""
    reviewer: str = ""
    dataset_executor: str = ""
    test_agent: str = ""
    
    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> AgentPrompts:
        """Create prompts from a dictionary."""
        return cls(
            schema_planner=data.get("schema_planner", ""),
            dataset_builder=data.get("dataset_builder", ""),
            server_builder=data.get("server_builder", ""),
            reviewer=data.get("reviewer", ""),
            dataset_executor=data.get("dataset_executor", ""),
            test_agent=data.get("test_agent", ""),
        )
    
    @classmethod
    def from_yaml(cls, path: Path | str) -> AgentPrompts:
        """Load prompts from a YAML file."""
        if not YAML_AVAILABLE:
            raise ImportError("PyYAML is required. Install with: pip install pyyaml")
        
        path = Path(path)
        if not path.exists():
            return cls()  # Return empty prompts if file doesn't exist
        
        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f) or {}
        
        return cls.from_dict(data)


@dataclass
class ExecutionConfig:
    """Configuration for code execution."""
    
    python_timeout_seconds: float = 180.0
    """Default timeout for Python script execution."""
    
    allowed_modules: List[str] = field(default_factory=lambda: ["pytest"])
    """Modules allowed to run in module mode (python -m)."""
    
    max_turns_per_agent: int = 20
    """Maximum turns allowed for each agent step."""


@dataclass
class ReviewConfig:
    """Configuration for the code review process."""
    
    max_review_cycles: int = 3
    """Maximum number of review cycles before failure."""
    
    database_keywords: List[str] = field(default_factory=lambda: [
        "database", "dataset", "data contract"
    ])
    """Keywords that indicate database-related issues."""
    
    negative_indicators: List[str] = field(default_factory=lambda: [
        "mismatch", "issue", "problem", "needs", "fix", "update",
        "incorrect", "missing", "violation", "inconsistent", "error"
    ])
    """Keywords that indicate problems requiring revision."""


@dataclass
class DirectoryConfig:
    """Configuration for directory structure."""
    
    output_dir_name: str = "generated"
    """Name of the root directory for generated code."""
    
    tests_dir_name: str = "tests"
    """Name of the root directory for tests."""
    
    transcripts_dir_name: str = "transcripts"
    """Name of the root directory for transcripts."""
    
    logs_dir_name: str = "logs"
    """Name of the root directory for logs."""
    
    sample_data_dir_name: str = "sample_data"
    """Name of the directory containing sample databases."""


@dataclass
class FileNamingConfig:
    """Configuration for file naming patterns."""
    
    server_suffix: str = "_server.py"
    """Suffix for server module files."""
    
    database_suffix: str = "_database.py"
    """Suffix for database module files."""
    
    database_json_suffix: str = "_database.json"
    """Suffix for database JSON files."""
    
    metadata_suffix: str = "_metadata.json"
    """Suffix for metadata JSON files."""
    
    log_file_pattern: str = "workflow_{timestamp}.log"
    """Pattern for log file names. {timestamp} will be replaced."""


@dataclass
class LoggingConfig:
    """Configuration for logging."""
    
    level: str = "INFO"
    """Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)."""
    
    format: str = "%(asctime)s - %(levelname)s - %(message)s"
    """Log message format."""
    
    date_format: str = "%Y-%m-%d %H:%M:%S"
    """Date format in log messages."""
    
    console_enabled: bool = True
    """Whether to output logs to console."""
    
    file_enabled: bool = True
    """Whether to output logs to file."""


@dataclass
class ModelConfig:
    """Configuration for the LLM model."""
    
    default_model: str = "deepseek/deepseek-chat"
    """Default model to use."""
    
    default_base_url: str = "https://api.deepseek.com"
    """Default base URL for the API."""
    
    api_key_env_vars: List[str] = field(default_factory=lambda: [
        "DEEPSEEK_API_KEY", "LITELLM_API_KEY", "API_KEY"
    ])
    """Environment variables to check for API key (in order)."""
    
    base_url_env_vars: List[str] = field(default_factory=lambda: [
        "DEEPSEEK_BASE_URL", "LITELLM_BASE_URL", "BASE_URL"
    ])
    """Environment variables to check for base URL (in order)."""


@dataclass
class ValidationConfig:
    """Configuration for validation rules."""
    
    strict_sample_validation: bool = True
    """Whether to strictly validate against sample database."""
    
    allow_extra_fields: bool = False
    """Whether to allow extra fields not in DATA CONTRACT."""
    
    require_data_contract: bool = True
    """Whether DATA CONTRACT is mandatory."""
    
    metadata_top_level_keys: List[str] = field(default_factory=lambda: [
        "name", "description", "tools"
    ])
    """Allowed top-level keys in metadata JSON."""
    
    # Validation strategy settings
    on_validation_failure: str = "feedback"
    """What to do when validation fails: 'fail' (raise error immediately), 
    'feedback' (convert to review feedback), 'warning' (log warning only)."""
    
    allow_missing_tools: bool = True
    """Whether to allow metadata to be missing some expected tools (will be flagged in review)."""
    
    allow_extra_tools: bool = True
    """Whether to allow metadata to contain extra tools not in schema."""
    
    max_validation_feedback_items: int = 10
    """Maximum number of validation issues to include in review feedback."""


@dataclass
class WorkflowConfig:
    """Main configuration for the workflow system."""
    
    execution: ExecutionConfig = field(default_factory=ExecutionConfig)
    review: ReviewConfig = field(default_factory=ReviewConfig)
    directories: DirectoryConfig = field(default_factory=DirectoryConfig)
    file_naming: FileNamingConfig = field(default_factory=FileNamingConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    validation: ValidationConfig = field(default_factory=ValidationConfig)
    prompts: AgentPrompts = field(default_factory=AgentPrompts)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], prompts: Optional[AgentPrompts] = None) -> WorkflowConfig:
        """Create configuration from a dictionary."""
        return cls(
            execution=ExecutionConfig(**data.get("execution", {})),
            review=ReviewConfig(**data.get("review", {})),
            directories=DirectoryConfig(**data.get("directories", {})),
            file_naming=FileNamingConfig(**data.get("file_naming", {})),
            logging=LoggingConfig(**data.get("logging", {})),
            model=ModelConfig(**data.get("model", {})),
            validation=ValidationConfig(**data.get("validation", {})),
            prompts=prompts or AgentPrompts(),
        )
    
    @classmethod
    def from_yaml(cls, path: Path | str, prompts_path: Optional[Path | str] = None) -> WorkflowConfig:
        """Load configuration from a YAML file.
        
        Args:
            path: Path to the main config file
            prompts_path: Optional path to prompts file. If None, looks for prompts.yaml in same directory.
        """
        if not YAML_AVAILABLE:
            raise ImportError("PyYAML is required to load YAML config files. Install with: pip install pyyaml")
        
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f) or {}
        
        # Load prompts
        if prompts_path is None:
            prompts_path = path.parent / "prompts.yaml"
        else:
            prompts_path = Path(prompts_path)
        
        prompts = AgentPrompts.from_yaml(prompts_path)
        
        return cls.from_dict(data, prompts=prompts)
    
    @classmethod
    def from_yaml_optional(cls, path: Path | str) -> WorkflowConfig:
        """Load configuration from YAML if it exists, otherwise return defaults."""
        path = Path(path)
        if path.exists() and YAML_AVAILABLE:
            try:
                return cls.from_yaml(path)
            except Exception:
                # Fall back to defaults if loading fails
                pass
        return cls()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to a dictionary."""
        return {
            "execution": {
                "python_timeout_seconds": self.execution.python_timeout_seconds,
                "allowed_modules": self.execution.allowed_modules,
                "max_turns_per_agent": self.execution.max_turns_per_agent,
            },
            "review": {
                "max_review_cycles": self.review.max_review_cycles,
                "database_keywords": self.review.database_keywords,
                "negative_indicators": self.review.negative_indicators,
            },
            "directories": {
                "output_dir_name": self.directories.output_dir_name,
                "tests_dir_name": self.directories.tests_dir_name,
                "transcripts_dir_name": self.directories.transcripts_dir_name,
                "logs_dir_name": self.directories.logs_dir_name,
                "sample_data_dir_name": self.directories.sample_data_dir_name,
            },
            "file_naming": {
                "server_suffix": self.file_naming.server_suffix,
                "database_suffix": self.file_naming.database_suffix,
                "database_json_suffix": self.file_naming.database_json_suffix,
                "metadata_suffix": self.file_naming.metadata_suffix,
                "log_file_pattern": self.file_naming.log_file_pattern,
            },
            "logging": {
                "level": self.logging.level,
                "format": self.logging.format,
                "date_format": self.logging.date_format,
                "console_enabled": self.logging.console_enabled,
                "file_enabled": self.logging.file_enabled,
            },
            "model": {
                "default_model": self.model.default_model,
                "default_base_url": self.model.default_base_url,
                "api_key_env_vars": self.model.api_key_env_vars,
                "base_url_env_vars": self.model.base_url_env_vars,
            },
            "validation": {
                "strict_sample_validation": self.validation.strict_sample_validation,
                "allow_extra_fields": self.validation.allow_extra_fields,
                "require_data_contract": self.validation.require_data_contract,
                "metadata_top_level_keys": self.validation.metadata_top_level_keys,
                "on_validation_failure": self.validation.on_validation_failure,
                "allow_missing_tools": self.validation.allow_missing_tools,
                "allow_extra_tools": self.validation.allow_extra_tools,
                "max_validation_feedback_items": self.validation.max_validation_feedback_items,
            },
        }
    
    def to_yaml(self, path: Path | str) -> None:
        """Save configuration to a YAML file."""
        if not YAML_AVAILABLE:
            raise ImportError("PyYAML is required to save YAML config files. Install with: pip install pyyaml")
        
        path = Path(path)
        with open(path, 'w', encoding='utf-8') as f:
            yaml.dump(self.to_dict(), f, default_flow_style=False, sort_keys=False)
    
    def apply_env_overrides(self) -> None:
        """Apply environment variable overrides to configuration."""
        # Execution overrides
        if timeout := os.getenv("WORKFLOW_PYTHON_TIMEOUT"):
            try:
                self.execution.python_timeout_seconds = float(timeout)
            except ValueError:
                pass
        
        if max_turns := os.getenv("WORKFLOW_MAX_TURNS"):
            try:
                self.execution.max_turns_per_agent = int(max_turns)
            except ValueError:
                pass
        
        # Review overrides
        if max_cycles := os.getenv("WORKFLOW_MAX_REVIEW_CYCLES"):
            try:
                self.review.max_review_cycles = int(max_cycles)
            except ValueError:
                pass
        
        # Logging overrides
        if log_level := os.getenv("WORKFLOW_LOG_LEVEL"):
            self.logging.level = log_level.upper()
        
        if console_enabled := os.getenv("WORKFLOW_CONSOLE_LOGS"):
            self.logging.console_enabled = console_enabled.lower() in ("true", "1", "yes")
        
        # Model overrides
        if model := os.getenv("WORKFLOW_MODEL"):
            self.model.default_model = model


def load_config(
    config_path: Optional[Path | str] = None,
    prompts_path: Optional[Path | str] = None,
    apply_env: bool = True,
) -> WorkflowConfig:
    """
    Load workflow configuration.
    
    Args:
        config_path: Path to configuration file. If None, looks for default locations.
        prompts_path: Path to prompts file. If None, auto-detects based on config_path.
        apply_env: Whether to apply environment variable overrides.
    
    Returns:
        WorkflowConfig instance.
    """
    if config_path is not None:
        config = WorkflowConfig.from_yaml(config_path, prompts_path=prompts_path)
    else:
        # Try default locations
        default_paths = [
            Path("workflow_config.yaml"),
            Path("config.yaml"),
            Path("workflow/config/default.yaml"),
            Path("workflow/config.yaml"),
        ]
        
        config = None
        for path in default_paths:
            if path.exists() and YAML_AVAILABLE:
                try:
                    config = WorkflowConfig.from_yaml(path, prompts_path=prompts_path)
                    break
                except Exception:
                    continue
        
        if config is None:
            # Load default config from package
            default_config = Path(__file__).parent / "config" / "default.yaml"
            default_prompts = Path(__file__).parent / "config" / "prompts.yaml"
            if default_config.exists() and YAML_AVAILABLE:
                try:
                    config = WorkflowConfig.from_yaml(default_config, prompts_path=default_prompts)
                except Exception:
                    config = WorkflowConfig()
            else:
                config = WorkflowConfig()
    
    if apply_env:
        config.apply_env_overrides()
    
    return config


__all__ = [
    "WorkflowConfig",
    "ExecutionConfig",
    "ReviewConfig",
    "DirectoryConfig",
    "FileNamingConfig",
    "LoggingConfig",
    "ModelConfig",
    "ValidationConfig",
    "AgentPrompts",
    "load_config",
]

