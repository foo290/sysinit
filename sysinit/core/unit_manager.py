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
            unit = Unit.from_config(svc_data)
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

    def start_all(self):
        for unit in self.units.values():
            unit.start()

    def stop_all(self):
        for unit in self.units.values():
            unit.stop()

    def reload_all(self):
        for unit in self.units.values():
            unit.reload()
