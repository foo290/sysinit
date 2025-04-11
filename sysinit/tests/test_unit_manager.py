import pytest
from unittest.mock import MagicMock, patch, mock_open

from sysinit.core.unit_manager import UnitManager
from sysinit.core.unit import Unit, Command


@pytest.fixture
def mock_unit():
    """Fixture to mock the Unit class and its methods."""
    unit = MagicMock(spec=Unit)
    unit.name = "mock_service"
    return unit


@pytest.fixture
def unit_manager(mock_unit):
    """Fixture to initialize the UnitManager with a mocked unit."""
    manager = UnitManager()
    manager.add_unit(mock_unit)
    return manager


def test_add_unit(unit_manager, mock_unit):
    """Test the add_unit method."""
    assert unit_manager.get("mock_service") == mock_unit
    unit_manager.add_unit(mock_unit)
    assert len(unit_manager.units) == 1


def test_get_unit(unit_manager, mock_unit):
    """Test the get method."""
    unit = unit_manager.get("mock_service")
    assert unit == mock_unit


def test_all_units(unit_manager, mock_unit):
    """Test the all_units property."""
    units = unit_manager.all_units
    assert units == [mock_unit]


def test_kill_switch(unit_manager, mock_unit):
    """Test the kill_switch method."""
    unit_manager.kill_switch()
    mock_unit.stop.assert_called_once()


def test_start_all(unit_manager, mock_unit):
    """Test the start_all method."""
    unit_manager.start_all()
    mock_unit.start.assert_called_once()


def test_stop_all(unit_manager, mock_unit):
    """Test the stop_all method."""
    unit_manager.stop_all()
    mock_unit.stop.assert_called_once()


def test_reload_all(unit_manager, mock_unit):
    """Test the reload_all method."""
    unit_manager.reload_all()
    mock_unit.reload_unit.assert_called_once()


def test_load_from_dict(mock_unit, monkeypatch):
    """Test loading units from a YAML configuration with mocked open() function."""
    mock_unit_data = {
        "name": "mock_service",
        "description": "Mock service",
        "exec_start": "mock_exec_start",
    }
    unit = Unit.from_dict(mock_unit_data)

    # Mock the content of the YAML file as a string
    mock_yaml_content = """
    services:
        - name: mock_service
          description: Mock service
          exec_start: mock_exec_start
    """

    # Mock open to simulate reading the YAML file content
    with patch("builtins.open", mock_open(read_data=mock_yaml_content)):
        # Call UnitManager with the mocked YAML file
        manager = UnitManager(config_path="mock_path.yaml")

    # Check if the `from_config` method was called with the correct data
    assert unit.name == mock_unit_data["name"]
    assert isinstance(unit.exec_start, Command)
    assert len(manager.units) == 1
