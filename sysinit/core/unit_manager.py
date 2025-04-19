"""
UnitManager handles the orchestration and lifecycle of service units.

It provides methods to load units from a configuration file and perform
various operations like start, stop, enable, disable, reload, and restart
both on individual services and on all services collectively.

Author: Nitin Sharma
Docs by ChatGPT
"""

from pathlib import Path
from typing import Dict, Optional, List
import yaml
from sysinit.core.unit import Unit
from sysinit.utils import validate_yaml_config
from sysinit.core.logger import Logger


class UnitManager:
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the UnitManager and optionally load services from a YAML config.

        Args:
            config_path (Optional[str]): Path to the configuration file.
        """
        self.units: Dict[str, Unit] = {}
        if config_path:
            self._load_from_config(config_path)

        self.logger = Logger(name=self.__class__.__name__).get()

    def _load_from_config(self, path: str):
        """
        Load unit definitions from a YAML configuration file.

        Args:
            path (str): Path to the YAML config file.
        """
        with open(path) as f:
            config: dict = yaml.safe_load(f)

        validate_yaml_config(config)

        for svc_data in config.get("services", []):
            for service_name, service_data in svc_data.items():
                unit_config = service_data.get("unit_config", {})
                command_config = service_data.get("command_config", {})

                unit = Unit.from_dict(unit_config, **command_config)
                self.add_unit(unit)

    def add_unit(self, unit: Unit):
        """
        Add a unit to the manager.

        Args:
            unit (Unit): Unit instance to be added.
        """
        self.units[unit.name] = unit

    def get(self, name: str) -> Optional[Unit]:
        """
        Retrieve a unit by name.

        Args:
            name (str): Name of the unit.

        Returns:
            Optional[Unit]: The unit if found, else None.
        """
        return self.units[name]

    @property
    def all_units(self) -> List[Unit]:
        """
        Get a list of all managed units.

        Returns:
            List[Unit]: All unit instances.
        """
        return list(self.units.values())

    def kill_switch(self):
        """
        Immediately stop all running units.
        """
        for unit in self.units.values():
            unit.stop()

    def start_service(self, service_name: str):
        """
        Start a specific service by name.

        Args:
            service_name (str): Name of the service to start.
        """
        unit = self.units.get(service_name)
        if not unit:
            raise Exception(f"No unit found with the name: {service_name}")
        unit.start()

    def stop_service(self, service_name: str):
        """
        Stop a specific service by name.

        Args:
            service_name (str): Name of the service to stop.
        """
        unit = self.units.get(service_name)
        if not unit:
            raise Exception(f"No unit found with the name: {service_name}")
        unit.stop()

    def enable_service(self, service_name: str):
        """
        Enable a specific service (persistent across restarts).

        Args:
            service_name (str): Name of the service to enable.
        """
        unit = self.units.get(service_name)
        if not unit:
            raise Exception(f"No unit found with the name: {service_name}")
        unit.enable()

    def disable_service(self, service_name: str):
        """
        Disable a specific service.

        Args:
            service_name (str): Name of the service to disable.
        """
        unit = self.units.get(service_name)
        if not unit:
            raise Exception(f"No unit found with the name: {service_name}")
        unit.disable()

    def reload_service(self, service_name: str):
        """
        Reload a specific service.

        Args:
            service_name (str): Name of the service to reload.
        """
        unit = self.units.get(service_name)
        if not unit:
            raise Exception(f"No unit found with the name: {service_name}")
        unit.reload_unit()

    def load_service(self, service_name: str):
        """
        Load a specific service.

        Args:
            service_name (str): Name of the service to load.
        """
        unit = self.units.get(service_name)
        if not unit:
            raise Exception(f"No unit found with the name: {service_name}")
        unit.load()

    def unload_service(self, service_name: str):
        """
        Unload a specific service.

        Args:
            service_name (str): Name of the service to unload.
        """
        unit = self.units.get(service_name)
        if not unit:
            raise Exception(f"No unit found with the name: {service_name}")
        unit.unload()

    def restart_service(self, service_name: str):
        """
        Restart a specific service.

        Args:
            service_name (str): Name of the service to restart.
        """
        unit = self.units.get(service_name)
        if not unit:
            raise Exception(f"No unit found with the name: {service_name}")
        unit.restart_unit()

    def start_all(self):
        """
        Start all managed services.
        """
        for unit in self.units.values():
            unit.start()

    def stop_all(self):
        """
        Stop all managed services.
        """
        for unit in self.units.values():
            unit.stop()

    def reload_all(self):
        """
        Reload all managed services.
        """
        for unit in self.units.values():
            unit.reload_unit()

    def load_all(self):
        """
        Load all managed services.
        """
        for unit in self.units.values():
            unit.load()

    def unload_all(self):
        """
        Unload all managed services.
        """
        for unit in self.units.values():
            unit.unload()

    def enable_all(self):
        """
        Enable all managed services.
        """
        for unit in self.units.values():
            unit.enable()

    def disable_all(self):
        """
        Disable all managed services.
        """
        for unit in self.units.values():
            unit.disable()

    def teardown(self):
        for unit in self.all_units:
            unit.disarm_service()

    def status_service(self, service_name: str):
        unit = self.units.get(service_name)
        if not unit:
            raise Exception(f"No unit found with the name: {service_name}")
        unit.status()

    def status_all(self):
        for unit in self.all_units:
            self.logger.info(unit.status())
