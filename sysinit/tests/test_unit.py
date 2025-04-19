# sysinit/tests/test_unit.py

import pytest
import subprocess
from unittest.mock import MagicMock, call
from pathlib import Path
from sysinit.core.unit import Unit
from sysinit.core.command import Command

# --- Fixtures ---

@pytest.fixture
def mock_subprocess_run(mocker):
    """Mocks subprocess.run globally for tests in this module."""
    mock = mocker.patch('subprocess.run', autospec=True)
    # Default to success
    mock.return_value = MagicMock(spec=subprocess.CompletedProcess, returncode=0, stdout="mock stdout", stderr="")
    return mock

@pytest.fixture
def mock_path_exists(mocker):
    """Mocks os.path.exists."""
    return mocker.patch('os.path.exists', autospec=True)

@pytest.fixture
def system_unit():
    """Unit configured for system mode (the only mode now)."""
    return Unit(
        name="sys-test",
        description="System Test Service",
        exec_start=Command("echo start-sys"),
        exec_stop=Command("echo stop-sys"),
        working_directory="/opt/sys",
        # manage_as_user=False, # Removed - system mode is implicit/default
        dry_run=False, # Assume not dry run for command execution tests
        verbose=False,
        systemd_dir="/etc/systemd/system" # Explicitly state default if desired
    )

# --- Test Cases ---

def test_unit_init(system_unit):
    assert system_unit.name == "sys-test"
    # assert system_unit.manage_as_user is False # Removed
    assert system_unit.systemd_dir == "/etc/systemd/system"
    assert system_unit.wanted_by == "multi-user.target"
    assert system_unit.service_file_name == "sys-test.service"

def test_unit_abs_path(system_unit):
    assert system_unit.unit_abs_path == "/etc/systemd/system/sys-test.service"

def test_is_loaded(system_unit, mock_path_exists):
    mock_path_exists.return_value = True
    assert system_unit.is_loaded is True
    mock_path_exists.assert_called_once_with(system_unit.unit_abs_path)

    mock_path_exists.reset_mock()
    mock_path_exists.return_value = False
    assert system_unit.is_loaded is False
    mock_path_exists.assert_called_once_with(system_unit.unit_abs_path)

def test_systemctl_commands(system_unit, mock_subprocess_run):
    # All commands should now use 'sudo systemctl'
    expected_cmd_base = "sudo systemctl"
    unit = system_unit # Using the system_unit fixture
    service_file = unit.service_file_name

    # Test start
    mock_subprocess_run.reset_mock()
    unit._start()
    mock_subprocess_run.assert_called_once_with(f"{expected_cmd_base} start {service_file}", shell=True, capture_output=True, text=True)

    # Test stop
    mock_subprocess_run.reset_mock()
    unit.stop()
    mock_subprocess_run.assert_called_once_with(f"{expected_cmd_base} stop {service_file}", shell=True, capture_output=True, text=True)

    # Test restart
    mock_subprocess_run.reset_mock()
    unit.restart_unit()
    mock_subprocess_run.assert_called_once_with(f"{expected_cmd_base} restart {service_file}", shell=True, capture_output=True, text=True)

    # Test enable
    mock_subprocess_run.reset_mock()
    unit.enable()
    mock_subprocess_run.assert_called_once_with(f"{expected_cmd_base} enable {service_file}", shell=True, capture_output=True, text=True)

    # Test disable
    mock_subprocess_run.reset_mock()
    unit.disable()
    mock_subprocess_run.assert_called_once_with(f"{expected_cmd_base} disable {service_file}", shell=True, capture_output=True, text=True)

    # Test daemon-reload
    mock_subprocess_run.reset_mock()
    unit.reload_daemon()
    # Note: reload_daemon Command takes sudo=True, resulting command includes sudo
    mock_subprocess_run.assert_called_once_with(f"sudo systemctl daemon-reload", shell=True, capture_output=True, text=True)


@pytest.mark.parametrize("stdout_val, expected_status", [
    ("enabled", True),
    ("disabled", False),
    ("static", False),
    (" enabled ", True), # Test stripping
    ("", False),
])
def test_is_enabled(system_unit, mock_subprocess_run, stdout_val, expected_status):
    # Use system_unit fixture
    unit = system_unit
    unit.dry_run = False # Make sure commands execute for properties

    mock_subprocess_run.return_value.stdout = stdout_val
    mock_subprocess_run.return_value.returncode = 0

    assert unit.is_enabled is expected_status
    # is_enabled Command takes sudo=False, uses systemctl directly
    expected_cmd = f"systemctl is-enabled {unit.service_file_name}"
    mock_subprocess_run.assert_called_with(expected_cmd, shell=True, capture_output=True, text=True)


@pytest.mark.parametrize("stdout_val, expected_status", [
    ("active", True),
    ("inactive", False),
    ("failed", False),
    (" activating ", False), # Must be exactly 'active'
    (" active ", True),
    ("", False),
])
def test_is_active(system_unit, mock_subprocess_run, stdout_val, expected_status):
    # Use system_unit fixture
    unit = system_unit
    unit.dry_run = False # Make sure commands execute for properties

    mock_subprocess_run.return_value.stdout = stdout_val
    mock_subprocess_run.return_value.returncode = 0

    assert unit.is_active is expected_status
    # is_active Command takes sudo=False, uses systemctl directly
    expected_cmd = f"systemctl is-active {unit.service_file_name}"
    mock_subprocess_run.assert_called_with(expected_cmd, shell=True, capture_output=True, text=True)


def test_generate_service_file_data(system_unit):
    system_unit.environment = {"VAR": "value"}
    system_unit.after = "network.target"
    system_unit.remain_after_exit = True
    system_unit.service_type = "simple"

    content = system_unit.generate_service_file_data()

    assert "[Unit]" in content
    assert f"Description={system_unit.description}" in content
    assert "After=network.target" in content
    assert "[Service]" in content
    assert "Type=simple" in content
    assert "RemainAfterExit=yes" in content
    assert f"WorkingDirectory={system_unit.working_directory}" in content
    assert f"ExecStart={system_unit.exec_start.command_str}" in content
    assert f"ExecStop={system_unit.exec_stop.command_str}" in content
    assert "Environment=VAR=value" in content
    assert "[Install]" in content
    assert f"WantedBy={system_unit.wanted_by}" in content # Should be multi-user.target

def test_unload(system_unit, mock_subprocess_run, mock_path_exists):
    mock_path_exists.return_value = True # Pretend file exists
    system_unit.dry_run = False
    expected_cmd = f"sudo rm {system_unit.unit_abs_path}"

    system_unit.unload()

    mock_subprocess_run.assert_called_with(expected_cmd, shell=True, capture_output=True, text=True)


def test_unload_not_loaded(system_unit, mock_path_exists):
    mock_path_exists.return_value = False # Pretend file doesn't exist
    with pytest.raises(FileNotFoundError):
        system_unit.unload()


def test_from_dict():
    config = {
        "name": "dict-svc",
        "description": "From Dict",
        "exec_start": "cmd start",
        "exec_stop": "cmd stop",
        "working_directory": "/dict/dir",
        "type": "forking",
        "RemainAfterExit": True,
        "environment": {"K": "V"},
    }
    # Command config kwargs (manage_as_user removed)
    kwargs = {"dry_run": True, "verbose": True}

    unit = Unit.from_dict(config, **kwargs)

    assert unit.name == "dict-svc"
    assert unit.description == "From Dict"
    assert isinstance(unit.exec_start, Command)
    assert unit.exec_start.command_str == "cmd start"
    assert isinstance(unit.exec_stop, Command)
    assert unit.exec_stop.command_str == "cmd stop"
    assert unit.working_directory == "/dict/dir"
    assert unit.service_type == "forking"
    assert unit.remain_after_exit is True
    assert unit.environment == {"K": "V"}
    assert unit.dry_run is True
    assert unit.verbose is True
    # assert unit.manage_as_user is False # Removed check


def test_from_service_file(tmp_path):
    service_content = """
[Unit]
Description=Test Service from File
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/run-this --arg
WorkingDirectory=/srv/data
RemainAfterExit=yes
User=filesvc

[Install]
WantedBy=graphical.target
    """
    filepath = tmp_path / "file-test.service"
    filepath.write_text(service_content)

    unit = Unit.from_service_file(str(filepath), dry_run=True) # Pass kwargs

    assert unit.name == "file-test"
    assert unit.description == "Test Service from File"
    assert unit.after == "network.target"
    assert unit.service_type == "simple"
    assert isinstance(unit.exec_start, Command)
    assert unit.exec_start.command_str == "/usr/bin/run-this --arg"
    assert unit.exec_stop is None # Not defined in file
    assert unit.working_directory == "/srv/data"
    assert unit.remain_after_exit == True # Should parse 'yes'
    assert unit.user == "filesvc"
    assert unit.wanted_by == "graphical.target"
    assert unit.dry_run is True # Kwarg passed through

# You should still add more tests for the Unit.start() method's logic,
# Unit.reload_unit(), and Unit.disarm_service() to ensure they call
# the correct sequence of mocked actions (_start, stop, enable, disable, unload, etc.)
# based on the mocked state (is_loaded, is_enabled, is_active).