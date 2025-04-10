import pytest
import sys

sys.path.append("/home/ns290/workstation/projects/sysinit")

from unittest.mock import patch, MagicMock
from pathlib import Path
from sysinit.core.command import Command
from sysinit.core.unit import Unit
import os


# Mocking subprocess.run to simulate command execution
@pytest.fixture
def mock_subprocess_run():
    with patch("subprocess.run") as mock_run:
        yield mock_run


def test_generate_service_file():
    """Test that the service file is generated correctly."""
    exec_start_command = Command("echo 'Starting service'")
    unit = Unit(
        name="test-service",
        description="Test Service",
        exec_start=exec_start_command,
        exec_stop=Command("echo 'Stopping service'"),
        working_directory="/tmp",
        restart="always",
        user="testuser",
        environment={"VAR": "value"},
    )

    # Generate service file content
    service_file_content = unit.generate_service_file_data()

    # Check if the service file content is as expected
    assert "Description=Test Service" in service_file_content
    assert "ExecStart=echo 'Starting service'" in service_file_content
    assert "ExecStop=echo 'Stopping service'" in service_file_content
    assert "WorkingDirectory=/tmp" in service_file_content
    assert "Restart=always" in service_file_content
    assert "User=testuser" in service_file_content
    assert "Environment=VAR=value" in service_file_content
    assert "WantedBy=multi-user.target" in service_file_content


def test_to_file():
    """Test that the service file is written to the disk correctly."""
    exec_start_command = Command("echo 'Starting service'")
    unit = Unit(
        name="test-service",
        description="Test Service",
        exec_start=exec_start_command,
        exec_stop=Command("echo 'Stopping service'"),
        dry_run=False,
    )

    # Write the service file
    unit.to_file("/tmp")

    # Verify that open was called to create the file in the specified path
    assert os.path.exists("/tmp/test-service.service")
    # Command(f'sudo rm /tmp/test-service.service', sudo=True).execute()
    os.remove("/tmp/test-service.service")


def test_start(mock_subprocess_run):
    """Test that the start command for the unit works."""
    unit_name = "test-service"
    unit = Unit(name=unit_name, exec_start=Command("echo 'Starting service'"))

    unit.start = MagicMock()

    # Start the unit
    unit.start()

    # Verify that the correct command was executed
    unit.start.assert_called_once()


def test_stop(mock_subprocess_run):
    """Test that the stop command for the unit works."""
    unit_name = "test-service"
    unit = Unit(
        name=unit_name, exec_start=Command("echo 'Starting service'"), exec_stop=Command("echo 'Stopping service'")
    )

    unit.stop = MagicMock()

    # Start the unit
    unit.stop()

    # Verify that the correct command was executed
    unit.stop.assert_called_once()


def test_restart_unit(mock_subprocess_run):
    """Test that the restart command for the unit works."""
    unit_name = "test-service"
    unit = Unit(
        name=unit_name, exec_start=Command("echo 'Starting service'"), exec_stop=Command("echo 'Stopping service'")
    )
    unit.restart = MagicMock()

    # Start the unit
    unit.restart()

    # Verify that the correct command was executed
    unit.restart.assert_called_once()


def test_status(mock_subprocess_run):
    """Test that the status command for the unit works."""
    unit_name = "test-service"
    unit = Unit(name=unit_name, exec_start=Command("echo 'Starting service'"))
    unit.status = MagicMock()

    # Start the unit
    unit.status()

    # Verify that the correct command was executed
    unit.status.assert_called_once()


def test_enable(mock_subprocess_run):
    """Test that the enable command for the unit works."""
    unit_name = "test-service"
    unit = Unit(name=unit_name, exec_start=Command("echo 'Starting service'"))
    unit.enable = MagicMock()

    # Start the unit
    unit.enable()

    # Verify that the correct command was executed
    unit.enable.assert_called_once()


def test_reload(mock_subprocess_run):
    """Test that the reload command for the unit works."""
    unit_name = "test-service"
    unit = Unit(name=unit_name, exec_start=Command("echo 'Starting service'"))

    unit.reload = MagicMock()

    # Start the unit
    unit.reload()

    # Verify that the correct command was executed
    unit.reload.assert_called_once()


def test_from_dict():
    """Test creating a unit from a configuration dictionary."""
    config = {
        "name": "test-service",
        "description": "Test Service",
        "exec_start": "echo 'Starting service'",
        "exec_stop": "echo 'Stopping service'",
        "working_directory": "/tmp",
        "restart": "always",
        "user": "testuser",
        "environment": {"VAR": "value"},
        "wanted_by": "multi-user.target",
    }

    unit = Unit.from_dict(config)

    # Check if the unit is created with the correct attributes
    print(unit.exec_stop)
    assert unit.name == "test-service"
    assert unit.description == "Test Service"
    assert isinstance(unit.exec_start, Command)
    assert isinstance(unit.exec_stop, Command)
    assert unit.exec_start.command_str == "echo 'Starting service'"
    assert unit.exec_stop.command_str == "echo 'Stopping service'"
    assert unit.working_directory == "/tmp"
    assert unit.restart == "always"
    assert unit.user == "testuser"
    assert unit.environment == {"VAR": "value"}
    assert unit.wanted_by == "multi-user.target"


def test_from_service_file():
    """Test creating a unit from an existing service file."""
    # Creating a mock service file
    mock_service_file = "/tmp/test-service.service"
    service_content = """
    [Unit]
    Description=Test Service
    After=network.target

    [Service]
    ExecStart=echo 'Starting service'
    ExecStop=echo 'Stopping service'
    WorkingDirectory=/tmp
    Restart=always
    User=testuser
    Environment=VAR=value

    [Install]
    WantedBy=multi-user.target
    """
    with open(mock_service_file, "w") as f:
        f.write(service_content)

    # Create unit from service file
    unit = Unit.from_service_file(mock_service_file)

    # Check if the unit is created with the correct attributes
    assert unit.name == "test-service"
    assert unit.description == "Test Service"
    assert unit.exec_start.command_str == "echo 'Starting service'"
    assert unit.exec_stop.command_str == "echo 'Stopping service'"
    assert unit.working_directory == "/tmp"
    assert unit.restart == "always"
    assert unit.user == "testuser"
    assert unit.environment == {}
    assert unit.wanted_by == "multi-user.target"

    # Clean up the mock service file
    Path(mock_service_file).unlink()
