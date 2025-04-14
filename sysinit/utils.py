"""
Utility functions for common filesystem operations.

This module includes lightweight helper functions used across the unit management system.

Author: Nitin Sharma
Docs Author: ChatGPT
"""

import os

# Join multiple path components into a single path
join_path = lambda *args: os.path.join(*args)

# Check if a given path exists in the filesystem
path_exists = lambda abs_path: os.path.exists(abs_path)


VALID_SYSTEMD_KEYS = {
    "name",
    "unit",
    "autostart",
    "description",
    "working_directory",
    "RemainAfterExit",
    "exec_start",
    "exec_stop",
    "Type",
    "User",
    "Group",
    "Restart",
    "RestartSec",
    "Environment",
    "StandardOutput",
    "StandardError",
    "TimeoutStartSec",
    "TimeoutStopSec",
    "WantedBy",
}


def validate_yaml_config(config: dict):
    errors = []

    services = config.get("services", [])
    if not isinstance(services, list):
        raise ValueError("'services' should be a list")

    for idx, service in enumerate(services):
        if not isinstance(service, dict):
            errors.append(f"Service at index {idx} should be a dict")
            continue

        service_name = next(iter(service.keys()))
        service_conf = service[service_name]

        unit_conf = service_conf.get("unit_config")
        cmd_conf = service_conf.get("command_config") or service_conf.get("command_conf")

        if not unit_conf:
            errors.append(f"No 'unit_config' found in '{service_name}'")
        else:
            unknown_keys = set(unit_conf.keys()) - VALID_SYSTEMD_KEYS
            if unknown_keys:
                errors.append(f"Unknown systemd keys in '{service_name}': {unknown_keys}")

        if not cmd_conf:
            errors.append(f"No 'command_config' found in '{service_name}'")
        elif not isinstance(cmd_conf.get("dry_run", None), bool):
            errors.append(f"'dry_run' must be a boolean in '{service_name}'")

    if errors:
        raise ValueError("Validation failed:\n" + "\n".join(errors))
    else:
        print("✅ YAML configuration is valid.")
