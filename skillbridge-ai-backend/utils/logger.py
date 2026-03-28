"""Simple logger wrapper used across backend modules."""

import logging

def get_logger(name: str = __name__):
    """Return a configured logger instance.

    Adds a StreamHandler only if no handlers are present to avoid duplicate
    log lines when modules call this repeatedly.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s %(levelname)s %(name)s: %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger
