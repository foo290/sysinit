from typing import Optional, Dict
from pathlib import Path
from sysinit.core.command import Command
import os


class Unit:
    def __init__(
        self,
        name: str,
        description: str = "",
        exec_start: Command = None,
        exec_stop: Optional[Command] = None,
        working_directory: Optional[str] = None,
        restart: Optional[str] = None,
        user: Optional[str] = None,
        environment: Optional[Dict[str, str]] = None,
        wanted_by: str = "multi-user.target",
        after: Optional[str] = None,
        requires: Optional[str] = None,

        verbose: bool = False,
        dry_run: bool = True
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

        self.verbose = verbose
        self.dry_run = dry_run

    def generate_service_file(self) -> str:
        lines = [
            "[Unit]",
            f"Description={self.description or self.name}",
            f"After={self.after}" if self.after else "",
            f"Requires={self.requires}" if self.requires else "",
            "",
            "[Service]",
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

    def write_service_file(self, directory="/etc/systemd/system"):
        path = Path(directory) / f"{self.name}.service"
        
        # Check if file already exists
        if os.path.exists(path):
            raise Exception(f'File: {self.name}, already exists at: {directory}')
        
        # Use subprocess to run the echo command with sudo to write the service file
        service_content = self.generate_service_file()
        command_str = f"echo '{service_content}' > {path}"
        command = Command(command_str=command_str, sudo=True, description=f"writing file for {self.name} service to: {directory}")
        command.execute()
    
    def link(self):
        self.write_service_file()

    def start(self):
        Command(f"systemctl daemon-reload", sudo=True, description=f"Reloading systemd daemon", verbose=self.verbose, dry_run=self.dry_run).execute()

    def start(self):
        Command(f"systemctl start {self.name}.service", sudo=True, description=f"Starting: {self.name} service", verbose=self.verbose, dry_run=self.dry_run).execute()

    def stop(self):
        Command(f"systemctl stop {self.name}.service", sudo=True, description=f"Stopping: {self.name} service", verbose=self.verbose, dry_run=self.dry_run).execute()

    def restart_unit(self):
        Command(f"systemctl restart {self.name}.service", sudo=True, description=f"Restarting: {self.name} service", verbose=self.verbose, dry_run=self.dry_run).execute()

    def status(self):
        Command(f"systemctl status {self.name}.service", sudo=True, description=f"Show status: {self.name} service", verbose=self.verbose, dry_run=self.dry_run).execute()

    def enable(self):
        Command(f"systemctl enable {self.name}.service", sudo=True, description=f"Enable: {self.name} service", verbose=self.verbose, dry_run=self.dry_run).execute()

    def reload(self):
        Command(f"systemctl daemon-reload", sudo=True, description=f"Reloading: {self.name} service", verbose=self.verbose, dry_run=self.dry_run).execute()

    @classmethod
    def from_config(cls, config: dict):
        # todo: fix this for commands
        start_cmd = config.get("exec_start")
        end_cmd = config.get("exec_stop")

        return cls(
            name=config["name"],
            description=config.get("description", ""),
            exec_start=Command(start_cmd) if start_cmd else None,
            exec_stop=Command(end_cmd) if end_cmd else None,
            working_directory=config.get("working_directory"),
            restart=config.get("restart"),
            user=config.get("user"),
            environment=config.get("environment"),
            wanted_by=config.get("wanted_by", "multi-user.target"),
            after=config.get("after"),
            requires=config.get("requires"),
        )

    @classmethod
    def from_service_file(cls, filepath: str):
        config = {}
        with open(filepath) as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    key, value = line.strip().split("=", 1)
                    config[key.lower()] = value

        return cls(
            name=Path(filepath).stem,
            description=config.get("description", ""),
            exec_start=config.get("execstart", ""),
            exec_stop=config.get("execstop", ""),
            working_directory=config.get("workingdirectory"),
            restart=config.get("restart"),
            user=config.get("user"),
            environment={},  # could add logic here to parse
            wanted_by=config.get("wantedby", "multi-user.target"),
            after=config.get("after"),
            requires=config.get("requires"),
        )
