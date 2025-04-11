"""
logger.py

This module provides a configurable logging utility class to standardize
logging across the sysinit package. It supports console and optional file-based logging,
with custom formats and logging levels.

Useful for consistent and readable logs across modules, and to help in debugging
and monitoring execution of system commands or services.

Author: Nitin Sharma
Docs by ChatGPT
"""

import logging
from pathlib import Path


class Logger:
    """
    A wrapper around Python's built-in logging module that sets up
    console and optional file logging with custom formatting.

    Attributes:
        logger (logging.Logger): The configured logger instance.
    """

    def __init__(
        self,
        name: str = "AppLogger",
        level: int = logging.INFO,
        log_to_file: bool = False,
        log_file: str = "logs/app.log"
    ):
        """
        Initializes the Logger instance with console and optional file handler.

        Args:
            name (str, optional): Name of the logger. Defaults to "AppLogger".
            level (int, optional): Logging level (e.g., logging.INFO, logging.DEBUG). Defaults to logging.INFO.
            log_to_file (bool, optional): If True, logs will be written to a file. Defaults to False.
            log_file (str, optional): File path for logging if log_to_file is True. Defaults to "logs/app.log".

        Notes:
            - Ensures no duplicate handlers are attached if already present.
            - Automatically creates log file directory if it doesn't exist.
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.logger.propagate = False  # avoid duplicate logs in some environments

        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

        # Console handler
        if not any(isinstance(h, logging.StreamHandler) for h in self.logger.handlers):
            ch = logging.StreamHandler()
            ch.setFormatter(formatter)
            self.logger.addHandler(ch)

        # File handler (optional)
        if log_to_file and not any(isinstance(h, logging.FileHandler) for h in self.logger.handlers):
            Path(log_file).parent.mkdir(parents=True, exist_ok=True)
            fh = logging.FileHandler(log_file)
            fh.setFormatter(formatter)
            self.logger.addHandler(fh)

    def get(self) -> logging.Logger:
        """
        Returns the configured logger instance.

        Returns:
            logging.Logger: The internal logger object with attached handlers.
        """
        return self.logger
