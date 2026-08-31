"""项目日志，给模块解析和 JSON 对比用。"""
from __future__ import annotations

import logging
from pathlib import Path

_LOGGER_NAME = "bqyx_parser"


def get_logger(name: str = _LOGGER_NAME) -> logging.Logger:
    """返回项目 logger。重复调用不会叠加 handler。"""
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
    logger.addHandler(handler)
    logger.propagate = False
    return logger


def add_file_handler(log_path: str | Path, level: int = logging.DEBUG) -> logging.Logger:
    """额外写一份日志文件，方便回头看对比差异。"""
    logger = get_logger()
    log_path = Path(log_path)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    resolved = log_path.resolve()
    for handler in logger.handlers:
        if isinstance(handler, logging.FileHandler) and Path(handler.baseFilename) == resolved:
            return logger

    handler = logging.FileHandler(log_path, encoding="utf-8")
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    logger.addHandler(handler)
    return logger
