"""Standard logging configuration for Cyber Threat Intelligence."""
import logging
import sys
from pathlib import Path
from typing import Optional

_loggers = {}

def get_logger(name: str = "bda_cyber_threat", log_file: Optional[str] = None) -> logging.Logger:
    """Return a configured logger with consistent formatting."""
    if name in _loggers:
        return _loggers[name]

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if not logger.handlers:
        # Console Handler
        c_handler = logging.StreamHandler(sys.stdout)
        c_handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] [%(name)s]: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        c_handler.setFormatter(formatter)
        logger.addHandler(c_handler)

        # Optional File Handler
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            f_handler = logging.FileHandler(str(log_path), encoding="utf-8")
            f_handler.setLevel(logging.DEBUG)
            f_handler.setFormatter(formatter)
            logger.addHandler(f_handler)

    _loggers[name] = logger
    return logger
