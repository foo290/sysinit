"""
command.py

This module provides a simple wrapper around shell commands to be executed
using the CommandEngine, allowing optional sudo execution, verbosity, dry-run
mode, and logging. Acts as an interface for interacting with shell via Python.

Author: Nitin Sharma
Docs by ChatGPT
"""

import logging

from sysinit.core.command_manager import CommandEngine


class Command:
    """
    Wrapper for executing shell commands via the CommandEngine.

    Attributes:
        command_str (str): The shell command to execute.
        sudo (bool): Whether to prepend 'sudo' to the command.
        description (str): A human-readable description of the command.
        verbose (bool): If True, prints verbose output.
        dry_run (bool): If True, skips execution and prints the command instead.
        engine (CommandEngine): The execution engine used to run the command.
    """

    def __init__(
        self,
        command_str: str,
        sudo: bool = False,
        description: str | None = None,
        verbose: bool = True,
        dry_run: bool = False,
        log_file: str | None = None,
        log_level: str = logging.INFO,
    ):
        """
        Initializes a Command instance.

        Args:
            command_str (str): The shell command to execute.
            sudo (bool, optional): Whether to run the command with 'sudo'. Defaults to False.
            description (str, optional): Description for the command. Defaults to command_str.
            verbose (bool, optional): Enables verbose output. Defaults to True.
            dry_run (bool, optional): If True, skips actual execution. Defaults to False.
            log_file (str, optional): Path to log file (currently unused).
        """
        self.command_str = command_str
        self.sudo = sudo
        self.description = description or command_str
        self.verbose = verbose
        self.dry_run = dry_run
        self.log_level = log_level

        self.engine = CommandEngine(verbose=self.verbose, dry_run=self.dry_run, log_level=self.log_level)

    def attach_engine(self, engine: CommandEngine) -> None:
        """
        Attaches a new CommandEngine to this command.

        Args:
            engine (CommandEngine): The engine used to execute the command.
        """
        self.engine = engine

    def execute(self):
        """
        Executes the command using the attached CommandEngine.

        Returns:
            Any: The output or result from the CommandEngine's run method.

        Raises:
            RuntimeError: If no engine is attached to the command.
        """
        if not self.engine:
            raise RuntimeError("CommandEngine not attached.")

        return self.engine.run(self.command_str, sudo=self.sudo)
