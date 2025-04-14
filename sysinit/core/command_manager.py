"""
command_manager.py

This module defines the CommandEngine class, which serves as the central
point of execution for running system shell commands. It includes support
for verbose logging, dry-run mode, sudo execution, and output capture.

Useful for managing system-level commands in a structured, logged, and safe manner
without directly relying on subprocess scattered across your codebase.

Author: Nitin Sharma
Docs by ChatGPT
"""

import subprocess
import logging
from pathlib import Path

from sysinit.core.logger import Logger


class CommandEngine:
    """
    Central command execution engine responsible for running shell commands
    with optional sudo, dry-run support, and rich logging.

    Attributes:
        title (str): A name or label for the engine, useful in logs.
        verbose (bool): Whether to print verbose logs.
        dry_run (bool): If True, skips execution and only logs the command.
        log_level (int): Logging level (e.g., logging.DEBUG).
        logger (logging.Logger): The logger instance used for output.
    """

    def __init__(
        self,
        verbose: bool = True,
        dry_run: bool = False,
        log_file: str | None = None,
        title: str | None = None,
        log_level: int = logging.INFO,
    ):
        """
        Initializes the CommandEngine.

        Args:
            verbose (bool, optional): Enables verbose logging. Defaults to True.
            dry_run (bool, optional): If True, commands will not be executed. Defaults to False.
            log_file (str, optional): Unused currently, placeholder for future file logging. Defaults to None.
            title (str, optional): Optional name for the engine instance. Defaults to 'GenericCommandEngine'.
            log_level (int, optional): Logging level. Defaults to logging.DEBUG.
        """
        self.title = title or "GenericCommandEngine"
        self.verbose = verbose
        self.dry_run = dry_run
        self.log_level = log_level

        self.logger = Logger(name=self.__class__.__name__, level=log_level).get()

    def run(self, cmd: str, sudo: bool = False) -> subprocess.CompletedProcess | None:
        """
        Executes a shell command using subprocess.

        Args:
            cmd (str): The command string to execute.
            sudo (bool, optional): If True, prepends 'sudo' to the command. Defaults to False.

        Returns:
            subprocess.CompletedProcess | None: The result of subprocess.run(), or None if dry_run is enabled.

        Logs:
            - The command being executed
            - Command output (stdout or stderr)
            - Success/failure indicators
        """
        if sudo:
            cmd = f"sudo {cmd}"

        self.logger.debug(f"Running command: {cmd}")
        if self.dry_run:
            self.logger.warning("[SKIP]: Dry run: skipped execution.")
            return None

        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        if result.returncode != 0 and result.stderr:
            self.logger.error("🔴 Command failed")
            cmd_op = result.stderr.strip()
            self.logger.debug(f"Command OP: {cmd_op}" if cmd_op else "... : [NO OUTPUT]")
        else:
            cmd_op = result.stdout.strip()
            self.logger.debug(f"Command OP: {cmd_op}" if cmd_op else "... : [NO OUTPUT]")
            self.logger.debug("🟢 Command execution successful ...OK")

        return result
