import os, pathlib
import sys; sys.path.append(os.getcwd())

import subprocess
import logging
import pytest
from unittest.mock import MagicMock, call # Use call for checking multiple calls if needed
from sysinit.core.command_manager import CommandEngine

# Fixture for the CommandEngine instance
@pytest.fixture
def engine():
    # Initialize with default verbose=True, dry_run=False for most tests
    return CommandEngine(verbose=True, dry_run=False)

@pytest.fixture
def engine_dry_run():
    return CommandEngine(verbose=True, dry_run=True)

# Mock subprocess.run
@pytest.fixture
def mock_run(mocker):
    mock = mocker.patch('subprocess.run', autospec=True)
    # Default successful return
    mock.return_value = MagicMock(spec=subprocess.CompletedProcess, returncode=0, stdout="Success Output", stderr="")
    return mock

# --- Test Cases ---

def test_engine_init_defaults():
    eng = CommandEngine()
    assert eng.verbose is True
    assert eng.dry_run is False
    assert eng.log_level == logging.INFO
    assert eng.title == "GenericCommandEngine"

def test_engine_init_custom():
    eng = CommandEngine(verbose=False, dry_run=True, log_level=logging.DEBUG, title="TestEngine")
    assert eng.verbose is False
    assert eng.dry_run is True
    assert eng.log_level == logging.DEBUG
    assert eng.title == "TestEngine"

def test_run_basic_command(engine, mock_run):
    cmd_str = "echo 'hello'"
    result = engine.run(cmd_str)

    mock_run.assert_called_once_with(cmd_str, shell=True, capture_output=True, text=True)
    assert result.returncode == 0
    assert result.stdout == "Success Output"

def test_run_with_sudo(engine, mock_run):
    cmd_str = "apt update"
    expected_cmd = "sudo apt update"
    engine.run(cmd_str, sudo=True)

    mock_run.assert_called_once_with(expected_cmd, shell=True, capture_output=True, text=True)

def test_run_dry_run(engine_dry_run, mock_run, caplog):
    cmd_str = "dangerous command"
    result = engine_dry_run.run(cmd_str, sudo=True)

    assert not mock_run.called # subprocess.run should NOT be called
    assert result is None # Should return None in dry_run
    # Check logs for the skipped command warning

def test_run_command_failure(engine, mock_run, caplog):
    cmd_str = "failing command"
    mock_run.return_value = MagicMock(
        spec=subprocess.CompletedProcess,
        returncode=1,
        stdout="",
        stderr="Command failed miserably"
    )

    result = engine.run(cmd_str)

    mock_run.assert_called_once_with(cmd_str, shell=True, capture_output=True, text=True)
    assert result.returncode == 1

def test_run_command_no_output(engine, mock_run, caplog):
    cmd_str = "silent command"
    mock_run.return_value = MagicMock(
        spec=subprocess.CompletedProcess, returncode=0, stdout="", stderr=""
    )

    result = engine.run(cmd_str)

    mock_run.assert_called_once_with(cmd_str, shell=True, capture_output=True, text=True)
    assert result.returncode == 0