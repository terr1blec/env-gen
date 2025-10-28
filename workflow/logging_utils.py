from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Optional, Union

from .utils import ensure_directory

if TYPE_CHECKING:
    from .config import WorkflowConfig


_LOGGER_NAME = "workflow"


def init_workflow_logger(
    log_file: Path,
    config: Optional[Union[WorkflowConfig, object]] = None,
    level: Optional[int] = None,
) -> logging.Logger:
    """
    Initialize the workflow logger with both console and file handlers.
    Reconfigures existing handlers on repeated calls.
    
    Args:
        log_file: Path to the log file
        config: Optional WorkflowConfig instance. If provided, uses config settings.
        level: Optional logging level. If not provided, uses config or defaults to INFO.
    
    Returns:
        Configured logger instance
    """
    ensure_directory(log_file.parent)

    logger = logging.getLogger(_LOGGER_NAME)
    
    # Determine logging level
    if level is None:
        if config is not None and hasattr(config, 'logging'):
            level_name = config.logging.level
            level = getattr(logging, level_name.upper(), logging.INFO)
        else:
            level = logging.INFO
    
    logger.setLevel(level)

    # Clear existing handlers to avoid duplicate logs when running multiple times.
    logger.handlers.clear()

    # Get format strings from config
    if config is not None and hasattr(config, 'logging'):
        fmt = config.logging.format
        datefmt = config.logging.date_format
        console_enabled = config.logging.console_enabled
        file_enabled = config.logging.file_enabled
    else:
        fmt = "%(asctime)s - %(levelname)s - %(message)s"
        datefmt = "%Y-%m-%d %H:%M:%S"
        console_enabled = True
        file_enabled = True

    formatter = logging.Formatter(fmt=fmt, datefmt=datefmt)

    # Add file handler if enabled
    if file_enabled:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        file_handler.setLevel(level)
        logger.addHandler(file_handler)

    # Add console handler if enabled
    if console_enabled:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(level)
        logger.addHandler(console_handler)

    return logger


def get_workflow_logger() -> logging.Logger:
    """Return the shared workflow logger."""
    return logging.getLogger(_LOGGER_NAME)

