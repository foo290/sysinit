import pytest
from unittest.mock import MagicMock
from sysinit.core.command import Command
from sysinit.core.command_manager import CommandEngine

# Fixture for a mock CommandEngine
@pytest.fixture
def mock_engine(mocker):
    engine = MagicMock(spec=CommandEngine)
    engine.run = MagicMock(return_value="Mock Result") # Mock the run method specifically
    # Attach the mock run method to the instance for assertion checking if needed
    engine.instance_run_mock = engine.run
    return engine

# --- Test Cases ---

def test_command_init_defaults():
    cmd_str = "ls -l"
    cmd = Command(cmd_str)
    assert cmd.command_str == cmd_str
    assert cmd.sudo is False
    assert cmd.description == cmd_str
    assert cmd.verbose is True
    assert cmd.dry_run is False
    assert isinstance(cmd.engine, CommandEngine) # Default engine is created

def test_command_init_custom():
    cmd_str = "pwd"
    cmd = Command(cmd_str, sudo=True, description="Show dir", verbose=False, dry_run=True)
    assert cmd.command_str == cmd_str
    assert cmd.sudo is True
    assert cmd.description == "Show dir"
    assert cmd.verbose is False
    assert cmd.dry_run is True
    # Check if engine reflects dry_run setting
    assert cmd.engine.dry_run is True

def test_command_execute_uses_engine(mock_engine):
    cmd_str = "my_command"
    cmd = Command(cmd_str, sudo=True)
    # Replace default engine with mock engine
    cmd.attach_engine(mock_engine)

    result = cmd.execute()

    # Assert that the mock engine's run method was called correctly
    mock_engine.instance_run_mock.assert_called_once_with(cmd_str, sudo=True)
    assert result == "Mock Result" # Check that the result from engine.run is returned

def test_command_execute_no_engine():
    cmd_str = "test"
    cmd = Command(cmd_str)
    cmd.engine = None # Simulate no engine attached
    with pytest.raises(RuntimeError, match="CommandEngine not attached."):
        cmd.execute()

def test_command_attach_engine(mock_engine):
    cmd_str = "test"
    cmd = Command(cmd_str)
    original_engine = cmd.engine
    cmd.attach_engine(mock_engine)
    assert cmd.engine is mock_engine
    assert cmd.engine is not original_engine