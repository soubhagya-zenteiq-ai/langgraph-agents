"""
Configures and manages the application's logging system.
Ensures consistent log formatting and output across all modules.
Provides a unified logger instance for tracking system behavior and errors.
"""
import logging

import sys


def get_logger(name: str = "ai-agent") -> logging.Logger:
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger  # prevent duplicate handlers

    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stdout)

    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s"
    )

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


# Global logger (optional)
logger = get_logger()