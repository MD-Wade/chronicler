# chronicler.py
# A simple, lightweight, and configurable logging library for Python.

import os
import sys
import inspect
import atexit

from datetime import datetime
from typing import Optional, Dict, Any, Union

from .log_batch_writer import LogBatchWriter

class Chronicler:
    """A simple and configurable logging class."""
    COLORS: Dict[str, str] = {
        'DEBUG': '\033[94m', 'INFO': '\033[92m', 'WARNING': '\033[93m',
        'ERROR': '\033[91m', 'CRITICAL': '\033[95m', 'ENDC': '\033[0m',
    }
    levels: Dict[str, int]
    level: int
    show_caller: bool
    log_file_path: Optional[str]
    rotation_policy: Optional[str]
    max_files: int
    use_colors: bool
    _batch_writer: Optional[LogBatchWriter] = None

    def __init__(
        self,
        level: str = 'INFO',
        show_caller: bool = True,
        log_file: Optional[str] = None,
        rotation_policy: Optional[str] = None,
        max_files: int = 5,
        use_colors: bool = True,
        batch_interval: Optional[Union[int, float]] = None
    ) -> None:
        """
        Initializes the logger.

        Args:
            level (str): The minimum logging level.
            show_caller (bool): If True, shows the calling script and line number.
            log_file (str, optional): Path to the log file.
            rotation_policy (str, optional): 'daily' or 'execution'.
            max_files (int): The maximum number of log files to keep.
            use_colors (bool): If True, uses colors for console output.
            batch_interval (float, optional): If set, enables batch writing at this interval in seconds.
        """
        self.levels = {'DEBUG': 0, 'INFO': 1, 'WARNING': 2, 'ERROR': 3, 'CRITICAL': 4}
        self.set_level(level)
        self.show_caller = show_caller
        self.log_file_path = log_file
        self.rotation_policy = rotation_policy
        self.max_files = max_files
        self.use_colors = use_colors and sys.stdout.isatty()

        if self.log_file_path and self.rotation_policy == 'execution':
            self._rotate_execution_logs()
        
        # Setup batch writing if an interval is provided
        if self.log_file_path and batch_interval is not None and batch_interval > 0:
            self._batch_writer = LogBatchWriter(self.log_file_path, batch_interval)
            self._batch_writer.start()
            atexit.register(self.shutdown)

    def shutdown(self) -> None:
        """Gracefully shuts down the batch writer if it exists."""
        if self._batch_writer:
            self._batch_writer.stop()
            self._batch_writer.join() # Wait for the thread to finish
            self._batch_writer = None

    def set_level(self, level: str) -> None:
        self.level = self.levels.get(level.upper(), 1)

    def _get_caller_info(self) -> str:
        frame = inspect.currentframe()
        for _ in range(20):
            if not frame: break
            if frame.f_globals.get('__name__') != __name__:
                caller_info = inspect.getframeinfo(frame)
                return f"{os.path.basename(caller_info.filename)}:{caller_info.lineno}"
            frame = frame.f_back
        return "unknown:0"

    def _log(self, level_name: str, *args: Any, **kwargs: Any) -> None:
        level_num = self.levels[level_name]
        if level_num < self.level:
            return

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        level_str = f"[{level_name}]"
        caller_info = f" ({self._get_caller_info()})" if self.show_caller else ""
        message_parts = [str(arg) for arg in args]
        message_parts.extend([f"{k}={v}" for k, v in kwargs.items()])
        message = " ".join(message_parts)

        console_log_entry = f"{timestamp} {level_str}{caller_info}: {message}"
        if self.use_colors:
            console_log_entry = f"{self.COLORS.get(level_name, '')}{console_log_entry}{self.COLORS['ENDC']}"
        print(console_log_entry, file=sys.stderr if level_num >= self.levels['ERROR'] else sys.stdout)
        
        if self.log_file_path:
            file_log_entry = f"{timestamp} {level_str}{caller_info}: {message}\n"
            self._write_to_file(file_log_entry)

    def _write_to_file(self, log_entry: str) -> None:
        # Determine the correct file path, especially for daily rotation
        filepath = self.log_file_path
        if self.rotation_policy == 'daily' and filepath:
            base, ext = os.path.splitext(filepath)
            datestamp = datetime.now().strftime('%Y-%m-%d')
            filepath = f"{base}_{datestamp}{ext}"
            self._rotate_daily_logs(base, ext)

        # If batch writer is active, add to queue. Otherwise, write directly.
        if self._batch_writer and filepath:
            # For daily rotation with batching, we need to update the writer's target file if the date changes
            if self.rotation_policy == 'daily' and self._batch_writer.log_file_path != filepath:
                self._batch_writer.flush() # Flush old file before changing path
                self._batch_writer.log_file_path = filepath
            self._batch_writer.add(log_entry)
        elif filepath:
            try:
                with open(filepath, 'a') as f:
                    f.write(log_entry)
            except IOError as e:
                print(f"\033[91m[ERROR] (chronicler.py): Could not write to log file {filepath}. Error: {e}\033[0m", file=sys.stderr)

    def _rotate_daily_logs(self, base: str, ext: str) -> None:
        log_dir = os.path.dirname(base) or '.'
        log_files = []
        for f_name in os.listdir(log_dir):
            if f_name.startswith(os.path.basename(base) + '_') and f_name.endswith(ext):
                log_files.append(os.path.join(log_dir, f_name))
        log_files.sort(key=os.path.getmtime)
        if len(log_files) >= self.max_files:
            num_to_delete = len(log_files) - (self.max_files - 1)
            for f_path in log_files[:num_to_delete]:
                try:
                    os.remove(f_path)
                except OSError as e:
                    print(f"\033[91m[ERROR] (chronicler.py): Could not remove old log file {f_path}. Error: {e}\033[0m", file=sys.stderr)

    def _rotate_execution_logs(self) -> None:
        if not self.log_file_path: return
        base, ext = os.path.splitext(self.log_file_path)
        log_dir = os.path.dirname(base) or '.'
        existing_logs = []
        for f_name in os.listdir(log_dir):
            if f_name.startswith(os.path.basename(base)) and f_name.endswith(ext):
                parts = f_name.rsplit('.', 2)
                if len(parts) == 3 and parts[1].isdigit():
                    existing_logs.append(int(parts[1]))
        existing_logs.sort(reverse=True)
        for num in existing_logs:
            new_num = num + 1
            old_path = os.path.join(log_dir, f"{base}.{num}{ext}")
            if new_num >= self.max_files:
                os.remove(old_path)
            else:
                new_path = os.path.join(log_dir, f"{base}.{new_num}{ext}")
                os.rename(old_path, new_path)
        if os.path.exists(self.log_file_path):
            if 1 < self.max_files:
                os.rename(self.log_file_path, f"{base}.1{ext}")

    def debug(self, *args: Any, **kwargs: Any) -> None: self._log('DEBUG', *args, **kwargs)
    def info(self, *args: Any, **kwargs: Any) -> None: self._log('INFO', *args, **kwargs)
    def warning(self, *args: Any, **kwargs: Any) -> None: self._log('WARNING', *args, **kwargs)
    def error(self, *args: Any, **kwargs: Any) -> None: self._log('ERROR', *args, **kwargs)
    def critical(self, *args: Any, **kwargs: Any) -> None: self._log('CRITICAL', *args, **kwargs)

log: "Chronicler" = Chronicler()
