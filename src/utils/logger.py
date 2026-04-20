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