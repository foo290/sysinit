"""
unit.py

This module defines the `Unit` class, which represents a systemd unit (service) in Linux.
It provides functionality to create, load, enable, disable, start, stop, and manage systemd service files
programmatically using Python.

Each unit is described by a name, commands to execute, environment variables, dependencies,
user settings, and can be translated into a `.service` file for systemd to use.

Author: Nitin Sharma
Docs by ChatGPT
"""

from typing import Optional, Dict
from pathlib import Path
from sysinit.core.command import Command
from sysinit.utils import path_exists, join_path


class Unit:
    """
    Represents a systemd unit/service and provides methods to manage it.

    Supports generating `.service` files, enabling/disabling, and
    starting/stopping the service via systemctl.

    Attributes:
        name (str): Name of the unit (without `.service`).
        description (str): Description of the service.
        exec_start (Command): Command to execute when starting the service.
        exec_stop (Optional[Command]): Command to execute when stopping the service.
        working_directory (Optional[str]): Working directory for the service.
        restart (Optional[str]): Restart behavior for the service.
        user (Optional[str]): System user to run the service as.
        environment (Dict[str, str]): Environment variables for the service.
        wanted_by (str): systemd target to hook into.
        after (Optional[str]): Service(s) this unit should start after.
        requires (Optional[str]): Service(s) this unit depends on.
        service_type (str): systemd service type (default: oneshot).
        dry_run (bool): If True, commands won't be executed.
        verbose (bool): If True, commands will print debug info.
        systemd_dir (str): Path to systemd unit directory.
    """

    def __init__(
        self,
        name: str,
        description: str = "",
        exec_start: Optional[Command] = None,
        exec_stop: Optional[Command] = None,
        working_directory: Optional[str] = None,
        service_type: Optional[str] = "oneshot",
        restart: Optional[str] = None,
        user: Optional[str] = None,
        environment: Optional[Dict[str, str]] = None,
        wanted_by: str = "multi-user.target",
        after: Optional[str] = None,
        requires: Optional[str] = None,
        verbose: bool = False,
        dry_run: bool = True,
        systemd_dir: str = "/etc/systemd/system",
    ):
        self.name = name
        self.description = description
        self.exec_start = exec_start
        self.exec_stop = exec_stop
        self.working_directory = working_directory
        self.restart = restart
        self.user = user
        self.environment = environment or {}
        self.wanted_by = wanted_by
        self.after = after
        self.requires = requires
        self.service_type = service_type

        self.verbose = verbose
        self.dry_run = dry_run
        self.systemd_dir = systemd_dir

        self.service_file_name = f"{self.name}.service"
        self._systemd_enabled_dir = join_path(self.systemd_dir, f"{self.wanted_by}.wants")

    @property
    def unit_abs_path(self) -> str:
        """Absolute path to the service file."""
        return join_path(self.systemd_dir, self.service_file_name)

    @property
    def is_loaded(self) -> bool:
        """Returns True if the service file exists in systemd directory."""
        return path_exists(self.unit_abs_path)

    @property
    def is_enabled(self) -> bool:
        """Returns True if systemctl reports the service as enabled."""
        res = Command(
            f"systemctl is-enabled {self.service_file_name}",
            sudo=False,
            description=f"Checking enabled: {self.name}",
            verbose=self.verbose,
            dry_run=self.dry_run,
        ).execute()
        return res.stdout.strip() == "enabled"

    @property
    def is_active(self) -> bool:
        """Returns True if systemctl reports the service as active (running)."""
        res = Command(
            f"systemctl is-active {self.service_file_name}",
            sudo=False,
            description=f"Checking is-active: {self.name}",
            verbose=self.verbose,
            dry_run=self.dry_run,
        ).execute()
        return res.stdout.strip() == "active"

    def load(self):
        """Creates and writes the service file to systemd directory."""
        if self.is_loaded:
            raise FileExistsError(f"File already exists: {self.unit_abs_path}")
        self.to_file(directory=self.systemd_dir)

    def unload(self):
        """Deletes the systemd service file."""
        if not self.is_loaded:
            raise FileNotFoundError(f"Service not loaded: {self.name}")

        Command(
            f"rm {self.unit_abs_path}",
            sudo=True,
            description=f"Removing service: {self.name}",
            verbose=self.verbose,
            dry_run=self.dry_run,
        ).execute()

    def start(self):
        """Starts the service using systemctl."""
        self.setup()
        Command(
            f"systemctl start {self.service_file_name}",
            sudo=True,
            description=f"Starting: {self.name} service",
            verbose=self.verbose,
            dry_run=self.dry_run,
        ).execute()

    def stop(self):
        """Stops the service using systemctl."""
        Command(
            f"systemctl stop {self.service_file_name}",
            sudo=True,
            description=f"Stopping: {self.name} service",
            verbose=self.verbose,
            dry_run=self.dry_run,
        ).execute()

    def restart_unit(self):
        """Restarts the service using systemctl."""
        Command(
            f"systemctl restart {self.service_file_name}",
            sudo=True,
            description=f"Restarting: {self.name} service",
            verbose=self.verbose,
            dry_run=self.dry_run,
        ).execute()

    def reload_unit(self):
        """Reloads the unit by unloading and loading it again, followed by daemon reload."""
        self.unload()
        self.load()
        self.reload_daemon()

    def status(self):
        """Prints the status of the service using systemctl."""
        Command(
            f"systemctl status {self.service_file_name}",
            sudo=True,
            description=f"Status: {self.name} service",
            verbose=self.verbose,
            dry_run=self.dry_run,
        ).execute()

    def enable(self):
        """Enables the service to start on boot."""
        Command(
            f"systemctl enable {self.service_file_name}",
            sudo=True,
            description=f"Enable: {self.name} service",
            verbose=self.verbose,
            dry_run=self.dry_run,
        ).execute()

    def disable(self):
        """Disables the service from starting on boot."""
        Command(
            f"systemctl disable {self.service_file_name}",
            sudo=True,
            description=f"Disable: {self.name} service",
            verbose=self.verbose,
            dry_run=self.dry_run,
        ).execute()

    def reload_daemon(self):
        """Reloads the systemd daemon after changes."""
        Command(
            f"systemctl daemon-reload",
            sudo=True,
            description="Reloading systemd daemon",
            verbose=self.verbose,
            dry_run=self.dry_run,
        ).execute()

    def setup(self):
        """Ensures service is loaded and systemd daemon is reloaded."""
        if not self.is_loaded:
            self.load()
        self.reload_daemon()

    def info(self) -> Dict:
        """Returns basic info about the unit and its status."""
        return {
            **vars(self),
            "is_enabled": self.is_enabled,
            "is_loaded": self.is_loaded,
        }

    @classmethod
    def from_dict(cls, config: dict, **kwargs) -> "Unit":
        """Creates a Unit instance from a dictionary config."""
        start_cmd = config.get("exec_start")
        stop_cmd = config.get("exec_stop")

        return cls(
            name=config["name"],
            description=config.get("description", ""),
            exec_start=Command(start_cmd) if start_cmd else None,
            exec_stop=Command(stop_cmd) if stop_cmd else None,
            working_directory=config.get("working_directory"),
            restart=config.get("restart"),
            user=config.get("user"),
            environment=config.get("environment"),
            wanted_by=config.get("wanted_by", "multi-user.target"),
            after=config.get("after"),
            requires=config.get("requires"),
            service_type=config.get("type"),
            **kwargs,
        )

    @classmethod
    def from_service_file(cls, filepath: str, **kwargs) -> "Unit":
        """Creates a Unit instance by parsing an existing .service file."""
        config = {}
        with open(filepath) as f:
            for line in f:
                if "=" in line and not line.strip().startswith("#"):
                    key, value = line.strip().split("=", 1)
                    config[key.lower()] = value

        if not config:
            raise ValueError(f"Empty or invalid unit file: {filepath}")

        return cls(
            name=Path(filepath).stem,
            description=config.get("description", ""),
            exec_start=Command(config.get("execstart")) if config.get("execstart") else None,
            exec_stop=Command(config.get("execstop")) if config.get("execstop") else None,
            working_directory=config.get("workingdirectory"),
            restart=config.get("restart"),
            user=config.get("user"),
            environment={},  # Could parse [Environment] lines here in future
            wanted_by=config.get("wantedby", "multi-user.target"),
            after=config.get("after"),
            requires=config.get("requires"),
            service_type=config.get("type"),
            **kwargs,
        )

    def generate_service_file_data(self) -> str:
        """Generates the content of a systemd .service file."""
        lines = [
            "[Unit]",
            f"Description={self.description or self.name}",
            f"After={self.after}" if self.after else "",
            f"Requires={self.requires}" if self.requires else "",
            "",
            "[Service]",
            f"Type={self.service_type}",
            f"WorkingDirectory={self.working_directory}" if self.working_directory else "",
            f"ExecStart={self.exec_start.command_str}" if self.exec_start else "",
            f"ExecStop={self.exec_stop.command_str}" if self.exec_stop else "",
            f"Restart={self.restart}" if self.restart else "",
            f"User={self.user}" if self.user else "",
        ] + [f"Environment={k}={v}" for k, v in self.environment.items()]

        lines += [
            "",
            "[Install]",
            f"WantedBy={self.wanted_by}",
        ]
        return "\n".join(filter(None, lines))

    def to_file(self, directory: Optional[str] = None):
        """Writes the service file to the given systemd directory."""
        directory = directory or self.systemd_dir
        if not path_exists(directory):
            raise ValueError(f"Path does not exist: {directory}")

        path = join_path(directory, self.service_file_name)
        service_content = self.generate_service_file_data()
        command_str = f"echo '{service_content}' | sudo tee {path} > /dev/null"

        Command(
            command_str=command_str,
            sudo=True,
            description=f"Writing service file for {self.name} to {directory}",
            dry_run=self.dry_run,
        ).execute()
