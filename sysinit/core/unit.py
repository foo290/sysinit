from typing import Optional, Dict
from pathlib import Path
from sysinit.core.command import Command
from sysinit.utils import path_exists, join_path
import os
import json


class Unit:
    def __init__(
        self,
        name: str,
        description: str = "",
        exec_start: Command = None,
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
        return join_path(self.systemd_dir, self.service_file_name)

    @property
    def is_loaded(self) -> bool:
        return path_exists(self.unit_abs_path)

    @property
    def is_enabled(self):
        res = Command(
            f"systemctl is-enabled {self.service_file_name}",
            sudo=False,
            description=f"checking enabled: {self.name}",
            verbose=self.verbose,
            dry_run=self.dry_run,
        ).execute()
        return res.stdout.strip() == 'enabled'

    @property
    def is_active(self):
        res = Command(
            f"systemctl is-active {self.service_file_name}",
            sudo=False,
            description=f"checking is-active: {self.name}",
            verbose=self.verbose,
            dry_run=self.dry_run,
        ).execute()
        return res.stdout.strip() == 'active'

    def load(self):
        if self.is_loaded:
            raise Exception(f"File: {self.name}, already loaded and exists at: {self.unit_abs_path}")
        self.to_file(directory=self.systemd_dir)

    def unload(self):
        if not self.is_loaded:
            raise Exception(f"Service: {self.name} is not loaded")

        Command(
            f"rm {self.systemd_dir}/{self.service_file_name}",
            sudo=True,
            description=f"Removing service: {self.name}",
            verbose=self.verbose,
            dry_run=self.dry_run,
        ).execute()

    def start(self):
        self.setup()
        Command(
            f"systemctl start {self.service_file_name}",
            sudo=True,
            description=f"Starting: {self.name} service",
            verbose=self.verbose,
            dry_run=self.dry_run,
        ).execute()

    def reload_unit(self):
        self.unload()
        self.load()
        self.reload_daemon()

    def stop(self):
        Command(
            f"systemctl stop {self.service_file_name}",
            sudo=True,
            description=f"Stopping: {self.name} service",
            verbose=self.verbose,
            dry_run=self.dry_run,
        ).execute()

    def restart_unit(self):
        Command(
            f"systemctl restart {self.service_file_name}",
            sudo=True,
            description=f"Restarting: {self.name} service",
            verbose=self.verbose,
            dry_run=self.dry_run,
        ).execute()

    def status(self):
        Command(
            f"systemctl status {self.service_file_name}",
            sudo=True,
            description=f"Show status: {self.name} service",
            verbose=self.verbose,
            dry_run=self.dry_run,
        ).execute()

    def enable(self):
        Command(
            f"systemctl enable {self.service_file_name}",
            sudo=True,
            description=f"Enable: {self.name} service",
            verbose=self.verbose,
            dry_run=self.dry_run,
        ).execute()

    def disable(self):
        Command(
            f"systemctl disable {self.service_file_name}",
            sudo=True,
            description=f"Disable: {self.name} service",
            verbose=self.verbose,
            dry_run=self.dry_run,
        ).execute()

    def reload_daemon(self):
        Command(
            f"systemctl daemon-reload",
            sudo=True,
            description=f"Reloading daemon",
            verbose=self.verbose,
            dry_run=self.dry_run,
        ).execute()

    def setup(self):
        if not os.path.exists(f"{self.systemd_dir}/{self.name}.service"):
            self.load()

        self.reload_daemon()

    def info(self):
        info = vars(self)
        info.update({"is_enabled": self.is_enabled, "is_loaded": self.is_loaded})
        return info

    @classmethod
    def from_dict(cls, config: dict, *_, **kwargs):
        # todo: fix this for commands
        start_cmd = config.get("exec_start")
        end_cmd = config.get("exec_stop")

        return cls(
            name=config["name"],
            description=config.get("description", ""),
            exec_start=Command(start_cmd) if start_cmd else "",
            exec_stop=Command(end_cmd) if end_cmd else "",
            working_directory=config.get("working_directory"),
            restart=config.get("restart"),
            user=config.get("user"),
            environment=config.get("environment"),
            wanted_by=config.get("wanted_by", "multi-user.target"),
            after=config.get("after"),
            requires=config.get("requires"),
            service_type=config.get("type"),

            **kwargs
        )

    @classmethod
    def from_service_file(cls, filepath: str, *_, **kwargs):
        config = {}
        with open(filepath) as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    key, value = line.strip().split("=", 1)
                    config[key.lower()] = value

        if not config:
            raise ValueError(f"empty unit file: {filepath}")

        start_cmd = config.get("execstart")
        stop_cmd = config.get("execstop")

        return cls(
            name=Path(filepath).stem,
            description=config.get("description", ""),
            exec_start=Command(command_str=start_cmd) if start_cmd else "",
            exec_stop=Command(command_str=stop_cmd) if stop_cmd else "",
            working_directory=config.get("workingdirectory"),
            restart=config.get("restart"),
            user=config.get("user"),
            environment={},  # could add logic here to parse
            wanted_by=config.get("wantedby", "multi-user.target"),
            after=config.get("after"),
            requires=config.get("requires"),
            service_type=config.get("type"),
            
            # additional shit goes here
            **kwargs
        )

    def generate_service_file_data(self) -> str:
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
        ]
        for k, v in self.environment.items():
            lines.append(f"Environment={k}={v}")
        lines += [
            "",
            "[Install]",
            f"WantedBy={self.wanted_by}",
        ]
        return "\n".join(filter(None, lines))

    def to_file(self, directory: str = None):
        directory = directory or self.systemd_dir
        if not path_exists(directory):
            raise ValueError(f"path: {directory} does not exists to write service file")
        
        path = join_path(directory, self.service_file_name)

        # Use subprocess to run the echo command with sudo to write the service file
        service_content = self.generate_service_file_data()
        command_str = f"echo '{service_content}' | sudo tee {path} > /dev/null"
        command = Command(
            command_str=command_str,
            sudo=True,
            description=f"writing file for {self.name} service to: {directory}",
            dry_run=self.dry_run,
        )
        command.execute()
