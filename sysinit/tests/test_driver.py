import pytest
import subprocess
from unittest.mock import patch
from command_manager.command import Command
from unit_manager.unit import Unit, UnitManager


# Mocking subprocess.run to simulate command execution
@pytest.fixture
def mock_subprocess_run():
    with patch("subprocess.run") as mock_run:
        yield mock_run


def test_unit_generation(mock_subprocess_run):
    """Test that a Unit correctly generates a service file."""
    unit_name = "test-service"
    description = "A test service"
    unit = Unit(name=unit_name, description=description)

    # Generate the systemd service file content
    service_file_content = unit.generate_service_file()

    # Check if the service file has the correct content
    assert unit_name in service_file_content
    assert description in service_file_content
    assert "ExecStart" in service_file_content
    assert "ExecStop" in service_file_content

    # Verify that a file was created
    assert unit.service_file_path.exists()  # The file should be generated


def test_unit_start(mock_subprocess_run):
    """Test that the start command for the unit works."""
    unit_name = "test-service"
    unit = Unit(name=unit_name)

    # Simulate the behavior of subprocess.run to always return a successful result
    mock_subprocess_run.return_value.returncode = 0

    # Start the unit
    unit.start()

    # Verify that the correct command was executed
    mock_subprocess_run.assert_called_with("sudo systemctl start test-service.service", shell=True, capture_output=True, text=True)


def test_unit_stop(mock_subprocess_run):
    """Test that the stop command for the unit works."""
    unit_name = "test-service"
    unit = Unit(name=unit_name)

    # Simulate the behavior of subprocess.run to always return a successful result
    mock_subprocess_run.return_value.returncode = 0

    # Stop the unit
    unit.stop()

    # Verify that the correct command was executed
    mock_subprocess_run.assert_called_with("sudo systemctl stop test-service.service", shell=True, capture_output=True, text=True)


def test_unit_enable(mock_subprocess_run):
    """Test that the enable command for the unit works."""
    unit_name = "test-service"
    unit = Unit(name=unit_name)

    # Simulate the behavior of subprocess.run to always return a successful result
    mock_subprocess_run.return_value.returncode = 0

    # Enable the unit
    unit.enable()

    # Verify that the correct command was executed
    mock_subprocess_run.assert_called_with("sudo systemctl enable test-service.service", shell=True, capture_output=True, text=True)


def test_unit_reload(mock_subprocess_run):
    """Test that the reload command for the unit works."""
    unit_name = "test-service"
    unit = Unit(name=unit_name)

    # Simulate the behavior of subprocess.run to always return a successful result
    mock_subprocess_run.return_value.returncode = 0

    # Reload the unit
    unit.reload()

    # Verify that the correct command was executed
    mock_subprocess_run.assert_called_with("sudo systemctl daemon-reload", shell=True, capture_output=True, text=True)


def test_unit_status(mock_subprocess_run):
    """Test that the status command for the unit works."""
    unit_name = "test-service"
    unit = Unit(name=unit_name)

    # Simulate the behavior of subprocess.run to always return a successful result
    mock_subprocess_run.return_value.returncode = 0

    # Get the status of the unit
    unit.status()

    # Verify that the correct command was executed
    mock_subprocess_run.assert_called_with("sudo systemctl status test-service.service", shell=True, capture_output=True, text=True)


def test_unit_manager_add_unit():
    """Test that UnitManager can add and look up units correctly."""
    unit_name = "test-service"
    unit = Unit(name=unit_name)
    
    # Create the UnitManager instance
    manager = UnitManager()

    # Add unit to the manager
    manager.add_unit(unit)

    # Look up the unit by name and ensure it's added correctly
    retrieved_unit = manager.get_unit(unit_name)
    assert retrieved_unit is unit  # The unit should be the same as the one added


def test_unit_manager_kill_all_units(mock_subprocess_run):
    """Test that the kill_switch can stop all units."""
    unit_name_1 = "test-service-1"
    unit_name_2 = "test-service-2"
    unit_1 = Unit(name=unit_name_1)
    unit_2 = Unit(name=unit_name_2)
    
    # Create the UnitManager instance
    manager = UnitManager()

    # Add units to the manager
    manager.add_unit(unit_1)
    manager.add_unit(unit_2)

    # Simulate the behavior of subprocess.run to always return a successful result
    mock_subprocess_run.return_value.returncode = 0

    # Kill all units
    manager.kill_all_units()

    # Verify that all units were stopped by checking the calls to subprocess.run
    mock_subprocess_run.assert_any_call(f"sudo systemctl stop {unit_name_1}.service", shell=True, capture_output=True, text=True)
    mock_subprocess_run.assert_any_call(f"sudo systemctl stop {unit_name_2}.service", shell=True, capture_output=True, text=True)


def test_unit_manager_enable_all_units(mock_subprocess_run):
    """Test that enable_all_units enables all units."""
    unit_name_1 = "test-service-1"
    unit_name_2 = "test-service-2"
    unit_1 = Unit(name=unit_name_1)
    unit_2 = Unit(name=unit_name_2)
    
    # Create the UnitManager instance
    manager = UnitManager()

    # Add units to the manager
    manager.add_unit(unit_1)
    manager.add_unit(unit_2)

    # Simulate the behavior of subprocess.run to always return a successful result
    mock_subprocess_run.return_value.returncode = 0

    # Enable all units
    manager.enable_all_units()

    # Verify that enable commands were executed for all units
    mock_subprocess_run.assert_any_call(f"sudo systemctl enable {unit_name_1}.service", shell=True, capture_output=True, text=True)
    mock_subprocess_run.assert_any_call(f"sudo systemctl enable {unit_name_2}.service", shell=True, capture_output=True, text=True)

