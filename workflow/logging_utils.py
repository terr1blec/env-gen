from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from .utils import ensure_directory


_LOGGER_NAME = "workflow"


def init_workflow_logger(log_file: Path, level: int = logging.INFO) -> logging.Logger:
    """
    Initialize the workflow logger with both console and file handlers.
    Reconfigures existing handlers on repeated calls.
    """
    ensure_directory(log_file.parent)

    logger = logging.getLogger(_LOGGER_NAME)
    logger.setLevel(level)

    # Clear existing handlers to avoid duplicate logs when running multiple times.
    logger.handlers.clear()

    formatter = logging.Formatter(
        fmt="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(level)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


def get_workflow_logger() -> logging.Logger:
    """Return the shared workflow logger."""
    return logging.getLogger(_LOGGER_NAME)

