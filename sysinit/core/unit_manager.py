from pathlib import Path
from typing import Dict, Optional, List
import yaml
from sysinit.core.unit import Unit


class UnitManager:
    def __init__(self, config_path: Optional[str] = None):
        self.units: Dict[str, Unit] = {}
        if config_path:
            self._load_from_config(config_path)

    def _load_from_config(self, path: str):
        with open(path) as f:
            config = yaml.safe_load(f)

        for svc_data in config.get("services", []):
            unit = Unit.from_dict(svc_data)
            self.add_unit(unit)

    def add_unit(self, unit: Unit):
        self.units[unit.name] = unit

    def get(self, name: str) -> Optional[Unit]:
        return self.units.get(name)

    @property
    def all_units(self) -> List[Unit]:
        return list(self.units.values())

    def kill_switch(self):
        for unit in self.units.values():
            unit.stop()

    def start_service(self, service_name: str):
        unit = self.units.get(service_name)
        if not unit:
            raise Exception(f"No unit found with the name: {service_name}")

        unit.start()

    def stop_service(self, service_name: str):
        unit = self.units.get(service_name)
        if not unit:
            raise Exception(f"No unit found with the name: {service_name}")

        unit.stop()

    def enable_service(self, service_name: str):
        unit = self.units.get(service_name)
        if not unit:
            raise Exception(f"No unit found with the name: {service_name}")

        unit.enable()

    def disable_service(self, service_name: str):
        unit = self.units.get(service_name)
        if not unit:
            raise Exception(f"No unit found with the name: {service_name}")

        unit.disable()

    def reload_service(self, service_name: str):
        unit = self.units.get(service_name)
        if not unit:
            raise Exception(f"No unit found with the name: {service_name}")
        unit.reload_unit()

    def load_service(self, service_name: str):
        unit = self.units.get(service_name)
        if not unit:
            raise Exception(f"No unit found with the name: {service_name}")
        unit.load()

    def unload_service(self, service_name: str):
        unit = self.units.get(service_name)
        if not unit:
            raise Exception(f"No unit found with the name: {service_name}")
        unit.unload()

    def restart_service(self, service_name: str):
        unit = self.units.get(service_name)
        if not unit:
            raise Exception(f"No unit found with the name: {service_name}")
        unit.restart_unit()

    def start_all(self):
        for unit in self.units.values():
            unit.start()

    def stop_all(self):
        for unit in self.units.values():
            unit.stop()

    def reload_all(self):
        for unit in self.units.values():
            unit.reload_unit()

    def load_all(self):
        for unit in self.units.values():
            unit.load()

    def unload_all(self):
        for unit in self.units.values():
            unit.unload()

    def enable_all(self):
        for unit in self.units.values():
            unit.enable()

    def disable_all(self):
        for unit in self.units.values():
            unit.disable()
