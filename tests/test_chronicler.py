# tests/test_chronicler.py

import os
import re
import time
from datetime import datetime
from freezegun import freeze_time

# Make the 'chronicler' package available for testing
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from chronicler import Chronicler

# --- Test Cases ---

def test_initialization_defaults():
    """Test that the logger initializes with default values."""
    log = Chronicler()
    assert log.level == log.levels['INFO']
    assert log.show_caller is True
    assert log.log_file_path is None
    assert log.rotation_policy is None
    log.shutdown()

def test_initialization_custom():
    """Test that the logger initializes with custom values."""
    log = Chronicler(level='DEBUG', show_caller=False, log_file='test.log', rotation_policy='daily', max_files=10)
    assert log.level == log.levels['DEBUG']
    assert log.show_caller is False
    assert log.log_file_path == 'test.log'
    assert log.rotation_policy == 'daily'
    assert log.max_files == 10
    log.shutdown()

def test_set_level():
    """Test the set_level method."""
    log = Chronicler()
    log.set_level('WARNING')
    assert log.level == log.levels['WARNING']
    log.set_level('invalid_level') # Should default to INFO
    assert log.level == log.levels['INFO']
    log.shutdown()

def test_logging_level_filtering(capsys):
    """Test that messages are filtered based on the log level."""
    log = Chronicler(level='WARNING', show_caller=False, use_colors=False)
    log.debug("This is a debug message.")
    log.info("This is an info message.")
    log.warning("This is a warning message.")
    log.error("This is an error message.")
    captured = capsys.readouterr()
    assert "This is a debug message." not in captured.out
    assert "This is an info message." not in captured.out
    assert "This is a warning message." in captured.out
    assert "This is an error message." in captured.err
    log.shutdown()

def test_log_format_no_caller(capsys):
    """Test the log message format without caller info."""
    log = Chronicler(show_caller=False, use_colors=False)
    log.info("Test message")
    captured = capsys.readouterr()
    log_pattern = r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} \[INFO\]: Test message"
    assert re.search(log_pattern, captured.out)
    log.shutdown()

def test_log_format_with_caller(capsys):
    """Test the log message format with caller info."""
    log = Chronicler(show_caller=True, use_colors=False)
    log.info("Caller test")
    captured = capsys.readouterr()
    log_pattern = r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} \[INFO\] \(test_chronicler\.py:\d+\): Caller test"
    assert re.search(log_pattern, captured.out.strip())
    log.shutdown()

def test_file_logging(tmp_path):
    """Test that logs are written to a file."""
    log_file = tmp_path / "test.log"
    log = Chronicler(log_file=str(log_file), use_colors=False)
    message = "This should be in the file."
    log.info(message)
    assert log_file.exists()
    with open(log_file, 'r') as f:
        content = f.read()
        assert message in content
    log.shutdown()

@freeze_time("2023-01-10")
def test_daily_rotation(tmp_path):
    """Test daily log rotation."""
    log_dir = tmp_path
    base_name = "daily_app.log"
    log_file_path = log_dir / base_name
    (log_dir / "daily_app_2023-01-08.log").touch()
    (log_dir / "daily_app_2023-01-09.log").touch()
    log = Chronicler(log_file=str(log_file_path), rotation_policy='daily', max_files=2)
    log.info("Test daily rotation.")
    assert (log_dir / "daily_app_2023-01-10.log").exists()
    assert not (log_dir / "daily_app_2023-01-08.log").exists()
    assert (log_dir / "daily_app_2023-01-09.log").exists()
    log.shutdown()

def test_execution_rotation(tmp_path):
    """Test execution-based log rotation."""
    log_dir = tmp_path
    base_name = "exec.log"
    log_file_path = log_dir / base_name
    # First run
    log_file_path.write_text("first run log")
    log1 = Chronicler(log_file=str(log_file_path), rotation_policy='execution', max_files=3)
    log1.info("Second run.")
    log1.shutdown() # Ensure batch is flushed if active
    assert "Second run" in (log_dir / "exec.log").read_text()
    assert (log_dir / "exec.1.log").read_text() == "first run log"
    # Second run
    log2 = Chronicler(log_file=str(log_file_path), rotation_policy='execution', max_files=3)
    log2.info("Third run.")
    log2.shutdown()
    assert "Third run" in (log_dir / "exec.log").read_text()
    assert "Second run" in (log_dir / "exec.1.log").read_text()
    assert (log_dir / "exec.2.log").read_text() == "first run log"
    # Third run
    log3 = Chronicler(log_file=str(log_file_path), rotation_policy='execution', max_files=3)
    log3.info("Fourth run.")
    log3.shutdown()
    assert "Fourth run" in (log_dir / "exec.log").read_text()
    assert "Third run" in (log_dir / "exec.1.log").read_text()
    assert "Second run" in (log_dir / "exec.2.log").read_text()
    assert not (log_dir / "exec.3.log").exists()

# --- NEW TESTS FOR BATCHING ---

def test_batch_writing(tmp_path):
    """Test that logs are written in batches after the interval."""
    log_file = tmp_path / "batch_test.log"
    # Use a very short interval for testing
    log = Chronicler(log_file=str(log_file), batch_interval=0.1)
    
    log.info("Message 1")
    log.info("Message 2")
    
    # File should not exist immediately
    assert not log_file.exists()
    
    # Wait for the batch interval to pass
    time.sleep(0.15)
    
    # Now the file should exist and have content
    assert log_file.exists()
    content = log_file.read_text()
    assert "Message 1" in content
    assert "Message 2" in content
    
    log.shutdown()

def test_batch_writing_shutdown_flush(tmp_path):
    """Test that logs are flushed on shutdown, even before the interval."""
    log_file = tmp_path / "shutdown_test.log"
    log = Chronicler(log_file=str(log_file), batch_interval=10) # Long interval
    
    log.info("Shutdown message")
    
    # File should not exist yet
    assert not log_file.exists()
    
    # Manually call shutdown (simulates atexit)
    log.shutdown()
    
    # File should exist immediately after shutdown
    assert log_file.exists()
    assert "Shutdown message" in log_file.read_text()

@freeze_time("2023-01-10 23:59:59")
def test_daily_rotation_with_batching(tmp_path):
    """Test that the batch writer handles daily rotation correctly."""
    log_file = tmp_path / "daily_batch.log"
    log = Chronicler(log_file=str(log_file), rotation_policy='daily', batch_interval=0.1)
    
    log.info("Message before midnight")
    
    # Move time past midnight
    freezer = freeze_time("2023-01-11 00:00:01")
    freezer.start()
    
    log.info("Message after midnight")
    
    log.shutdown()
    freezer.stop()
    
    # Check both log files
    log_before = tmp_path / "daily_batch_2023-01-10.log"
    log_after = tmp_path / "daily_batch_2023-01-11.log"
    
    assert log_before.exists()
    assert "Message before midnight" in log_before.read_text()
    
    assert log_after.exists()
    assert "Message after midnight" in log_after.read_text()
