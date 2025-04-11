# SysInit - Lightweight Service Unit Manager

`sysinit` is a simple and extensible unit management system written in Python. It provides functionality similar to basic service managers like `systemd`, allowing you to define, start, stop, enable, disable, and reload services (units) using YAML configurations.

---

## 📁 Project Structure

```
sysinit/
├── core/
│   ├── unit.py          # Defines the Unit class and its lifecycle methods
│   └── manager.py       # UnitManager to manage multiple units
├── utils.py             # Utility functions for filesystem operations
├── config.yaml          # Example configuration for unit services (not included here)
└── README.md            # Project documentation
```

---

## 📦 Features

- Define services in a YAML configuration
- Start, stop, enable, disable, load, and unload individual or all units
- Simple plug-and-play Python classes
- Reload and restart services dynamically
- Easily extendable architecture

---

## 🔧 Usage

### 1. Define Units

Create a `config.yaml` file like so:

```yaml
services:
  - name: example-service
    exec_start: "python example.py"
    working_dir: "/path/to/service"
    enabled: true
```

### 2. Initialize Unit Manager

```python
from sysinit.core.manager import UnitManager

manager = UnitManager("config.yaml")
manager.start_all()
```

### 3. Control Services

```python
manager.start_service("example-service")
manager.stop_service("example-service")
manager.restart_service("example-service")
manager.disable_service("example-service")
```

---

## 🧠 Components

### Unit (`core/unit.py`)
Represents a single service. Provides lifecycle methods:
- `start()`
- `stop()`
- `restart_unit()`
- `enable()`
- `disable()`
- `reload_unit()`
- `load()`
- `unload()`

### UnitManager (`core/manager.py`)
Handles multiple Unit instances. Allows operations across all or individual services, loaded from a YAML config.

### utils.py
Contains:
- `join_path`: Safely joins multiple path segments.
- `path_exists`: Checks if a path exists.

---

## ✅ Requirements

- Python 3.7+
- `pyyaml`

Install dependencies:

```bash
pip install pyyaml
```

---

## ✍️ Author

- **Code Author:** Nitin Sharma  
- **Docs Author:** ChatGPT

---

## 📜 License

This project is open-source and free to use under the MIT License.
