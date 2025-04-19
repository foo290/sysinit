# SysInit - Lightweight Python Service Unit Manager

[![PyPI version](https://badge.fury.io/py/sysinit.svg)](https://badge.fury.io/py/sysinit) <!-- Replace 'sysinit' if needed -->
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
<!-- Add other badges like build status if you have CI -->

`sysinit` is a Python library for defining, managing, and interacting with systemd-like service units using simple YAML configurations. It allows you to programmatically control the lifecycle (start, stop, enable, disable, reload) of background processes or tasks.

---

## ⚠️ Important Prerequisites & Warnings

*   **Operating System:** This library **only works on Linux distributions that use systemd**. It fundamentally relies on the `systemctl` command and the systemd directory structure. It will **not** work on macOS, Windows, or non-systemd Linux systems.
*   **System Mode (`sudo` Required):** By default, or when `manage_as_user: false` is set for a service, `sysinit` interacts with the **system-wide systemd instance**. This requires **`sudo` (root) privileges** for most operations:
    *   Placing/removing service files in `/etc/systemd/system/`.
    *   Running `systemctl start/stop/enable/disable/restart/daemon-reload` for system services.
    *   **Security Risk:** Granting `sudo` access to any script carries inherent security risks. Understand the commands being run (primarily `systemctl` and file operations in system directories) before using this mode. `sysinit` attempts to use `sudo` only when necessary for system-level interaction.

---

## ✨ Features

*   Define services declaratively in YAML.
*   Manage systemd **system** services (requires `sudo`).
*   Manage systemd **user** services (`sudo`-free).
*   Control service lifecycle: `start`, `stop`, `restart`, `reload`.
*   Enable/disable services for boot/login start.
*   Load/unload service definition files.
*   Pythonic API for programmatic control (`Unit`, `UnitManager`).
*   Dry-run mode for safe testing.
*   Basic logging of operations.

---

## 💾 Installation

```bash
# Install from PyPI
pip install sysinit # <-- Replace 'sysinit' with your actual package name if different

# For development (includes testing and formatting tools)
pip install "sysinit[dev]"
# Or: pip install black pytest pyyaml
```

## 🚀 Quick Start (CLI / Terminal)

The primary way to interact via the command line is through the `sysinit-term` command, which provides an interactive shell.

1.  **Ensure `ipython` is installed** (see Installation section above).
2.  **(Optional) Create `config.yaml`:** Define your services as described in the sections below. If `config.yaml` doesn't exist in the current directory, the shell will start with an empty manager.
3.  **Launch the Interactive Shell:**
    ```bash
    # Use default config.yaml (if it exists)
    sysinit-term shell

    # Specify a different configuration file
    sysinit-term --config /path/to/your/config.yaml shell

    # Get help
    sysinit-term --help
    sysinit-term shell --help
    ```
4.  **Inside the Shell:** You'll get an IPython prompt. Use the available objects and helper functions (like `manager`, `Unit`, `Command`, `start()`, `stop()`, `status()`, `services()`, `add_unit()`) to manage your services interactively. Type `exit()` or press `Ctrl+D` to quit.

    ```ipython
    # Example session inside the shell:
    In [1]: services() # List services loaded from config (or 'No services...')
    Managed services:
    - my-web-server
    - my-dev-tool

    In [2]: status('my-dev-tool')
    # Status output...

    In [3]: stop('my-web-server') # May require sudo password if not run as root
    Stopping 'my-web-server'...
    Service 'my-web-server' stopped.

    In [4]: u = Unit(name='temp-ls', exec_start='ls -l /tmp', manage_as_user=True)

    In [5]: add_unit(u)
    Unit 'temp-ls' added to manager.

    In [6]: start('temp-ls')
    Starting 'temp-ls'...
    # Output...
    Service 'temp-ls' started.
    ```

*(Note: While the interactive shell is the primary focus of `sysinit-term`, you could extend `sysinit/term.py` to include direct, non-interactive commands like `sysinit-term start <service>` if desired.)*


# 🚀 Usage

### 1. Define Services (config.yaml)
Create a YAML file (e.g., config.yaml) to define your services. Specify whether each service should be managed at the system level or user level.

```yaml
services:
  # Example 1: A system-wide service (requires sudo)
  - my-web-server:
      unit_config:
        name: my-web-server              # Base name for service file (my-web-server.service)
        description: My Sample Web Server
        exec_start: "/usr/bin/python -m http.server 8000" # Command to start
        working_directory: "/opt/my-web-app"     # Optional: Directory to run in
        user: "www-data"                  # Optional: Run as specific user
        Type: "simple"                    # Systemd service type
        Restart: "on-failure"             # Optional: Restart policy
        # WantedBy: "multi-user.target"   # Default for system services
      command_config:
        dry_run: false                    # Set to true to just print commands
        verbose: true                     # More detailed logging
        manage_as_user: false             # Explicitly system mode (default)
        enable_service: true              # Attempt to enable on first start

  # Example 2: A user-specific service (sudo-free)
  - my-dev-tool:
      unit_config:
        name: my-dev-tool                 # my-dev-tool.service
        description: My Development Helper Tool
        exec_start: "/home/user/scripts/my_dev_tool.py" # MUST be accessible by the user
        working_directory: "/home/user/dev/my-tool"
        Type: "oneshot"
        RemainAfterExit: yes
        # WantedBy: "default.target"       # Default for user services
      command_config:
        dry_run: false
        verbose: true
        manage_as_user: true              # CRITICAL: Run as systemd --user service
        enable_service: true              # Enable for user login start

  # Add more services as needed...
```

### 2. Initialize and Control via Python

```py
from sysinit.core.unit_manager import UnitManager
import logging

# Configure logging level if needed (optional)
# logging.basicConfig(level=logging.DEBUG)

# Initialize the manager, loading services from the config
try:
    manager = UnitManager("config.yaml")
except FileNotFoundError:
    print("Error: config.yaml not found!")
    exit(1)
except ValueError as e:
    print(f"Error loading config: {e}")
    exit(1)

# --- Lifecycle Operations ---

# Start all defined services (respects manage_as_user for each)
print("Starting all services...")
manager.start_all()
# Note: Starting system services will likely prompt for sudo password if not run as root

# Start a specific service
print("\nStarting my-dev-tool...")
try:
    manager.start_service("my-dev-tool")
except Exception as e:
    print(f"Error starting service: {e}")

# Stop a specific service
print("\nStopping my-web-server...")
try:
    manager.stop_service("my-web-server") # This will likely require sudo
except Exception as e:
    print(f"Error stopping service: {e}")

# Check status of all services
print("\nChecking status...")
manager.status_all()

# Restart a specific service
print("\nRestarting my-dev-tool...")
manager.restart_service("my-dev-tool")

# Disable a service (won't start on boot/login)
print("\nDisabling my-web-server...")
manager.disable_service("my-web-server") # Requires sudo

# Enable a service (will start on boot/login)
print("\nEnabling my-web-server...")
manager.enable_service("my-web-server") # Requires sudo

# Reload configuration for a service (rewrites .service file, reloads daemon)
# Use after changing config in code or if the service file needs refreshing
print("\nReloading my-dev-tool definition...")
manager.reload_service("my-dev-tool")

# Stop all services
print("\nStopping all services...")
manager.stop_all()

# Unload all service files (removes from systemd dirs)
print("\nUnloading all services...")
manager.unload_all() # Requires sudo for system services
```

---

## ⚙️ Configuration (`config.yaml` Details)

The `config.yaml` file has a top-level `services` key, which is a list of service definitions. Each service definition is a dictionary with a single key being the **logical service name** used within `sysinit` (e.g., `my-web-server`). The value is another dictionary containing `unit_config` and `command_config`.

### `unit_config`

These parameters map closely to systemd `.service` file options within the `[Unit]` and `[Service]` sections.

*   `name`: (Required) The base name for the service (e.g., `my-app` results in `my-app.service`).
*   `description`: (Optional) Service description (`Description=`).
*   `exec_start`: (Required) The command to run to start the service (`ExecStart=`).
*   `exec_stop`: (Optional) The command to run to stop the service (`ExecStop=`).
*   `working_directory`: (Optional) The working directory for the service (`WorkingDirectory=`).
*   `user`: (Optional) System user to run the service as (`User=`). Only effective in system mode.
*   `group`: (Optional) System group to run the service as (`Group=`). Only effective in system mode.
*   `Type`: (Optional) Service type (`simple`, `forking`, `oneshot`, etc.). Defaults to `oneshot`. (`Type=`).
*   `Restart`: (Optional) Restart policy (`no`, `on-success`, `on-failure`, `always`, etc.) (`Restart=`).
*   `RemainAfterExit`: (Optional, boolean) Useful for `oneshot` services. Defaults to `false`. (`RemainAfterExit=`).
*   `Environment`: (Optional, dict) Environment variables (`Environment="KEY=value"`).
*   `After`: (Optional, string) Run after specified units (`After=`).
*   `Requires`: (Optional, string) Depends on specified units (`Requires=`).
*   `WantedBy`: (Optional) Install target. Defaults to `multi-user.target` (system) or `default.target` (user). (`WantedBy=`).
*   `unit`: (Optional) Explicitly set the service filename (e.g., `my-custom-name.service`). Overrides `name`.

### `command_config`

These parameters control how `sysinit` itself behaves when managing the unit.


*   `dry_run`: (Optional, boolean) If `true`, print commands instead of executing them. Defaults to `false`.
*   `verbose`: (Optional, boolean) Enable more detailed logging output. Defaults to `false`.
*   `enable_service`: (Optional, boolean) If `true`, `sysinit` will attempt to `enable` the service during the first `start` operation if it's not already enabled. Defaults to `false`.

---