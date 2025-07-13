# Chronicler

**A lightweight, dependency-free logging library for Python.**

Chronicler is a minimalistic yet powerful logging solution for Python projects. It provides all the essential features you need, with a focus on simplicity, readability, and ease of integration. It supports multiple log levels, caller tracing, log file rotation, and automatic cleanup to keep your logs organized without manual maintenance.

---

## ☝️🤓 Features

- **Five Standard Logging Levels**  
  DEBUG, INFO, WARNING, ERROR, and CRITICAL.

- **Effortless Setup**  
  Initialize and use Chronicler with a single line of code.

- **Caller Tracing**  
  Automatically includes the filename and line number of each log message, aiding quick debugging.

- **Colorized Console Output**  
  Makes logs easy to read by giving each level its own color in the terminal.

- **File Logging Support**  
  Seamlessly log output to files alongside console output.

- **Automatic Log Rotation**  
  Start a new log file daily or on each execution to keep logs concise.

- **Automatic Cleanup**  
  Keeps your environment tidy by deleting old log files once exceeding a defined limit.

- **Zero Dependencies**  
  Runs out of the box on any standard Python installation.

---

## 📦 Installation

Chronicler does not require installation from PyPI. Simply include it in your project structure:

```
your_project/
├── chronicler/
│   ├── __init__.py
│   └── chronicler.py
└── your_main_script.py
```

---

## 🧪 Running the Tests

Tests use **pytest** and **freezegun** (for testing log rotation by date).

1. Install the test dependencies:

```
pip install pytest freezegun
```

2. Place your tests in a `tests/` directory. For example:

```
your_project/
├── tests/
│   └── test_chronicler.py
```

3. Run the tests:

```
pytest
```

---

## ⚡ Quick Start

### Basic Usage

```python
from chronicler import Chronicler

# Create a logger (default level is INFO).
log = Chronicler()

log.info("This is an info message.")
log.warning("This is a warning.")
log.error("Uh oh, an error occurred.", error_code=500)

# This debug message won't show by default.
log.debug("This is a debug message.")
```

### Using the Default Logger

```python
from chronicler import log

log.info("This uses the default logger!")
```

---

### Changing the Log Level

```python
debug_logger = Chronicler(level='DEBUG')
debug_logger.debug("Now you see me!")
```

---

### Saving Logs to a File

```python
file_logger = Chronicler(log_file='my_app.log')
file_logger.info("This will appear in both console and my_app.log.")
```

---

### Setting Up Log Rotation

#### Daily Rotation

```python
daily_logger = Chronicler(
    log_file='app.log',
    rotation_policy='daily',
    max_files=7  # Keeps logs for the last 7 days
)

daily_logger.info("This goes into 'app_YYYY-MM-DD.log'.")
```

#### Per Execution Rotation

```python
exec_logger = Chronicler(
    log_file='script.log',
    rotation_policy='execution',
    max_files=5  # Keeps logs from the last 5 runs
)

exec_logger.info("A new log file is created every run.")
```

---

## ⚙️ Configuration Options

| Parameter         | Type  | Description                                                                  | Default  |
| ----------------- | ----- | ---------------------------------------------------------------------------- | -------- |
| `level`           | str   | Minimum logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`).     | `'INFO'` |
| `show_caller`     | bool  | Show file and line number of log calls.                                      | `True`   |
| `log_file`        | str   | File to save logs to (optional).                                             | `None`   |
| `rotation_policy` | str   | Log rotation strategy (`daily`, `execution`).                                | `None`   |
| `max_files`       | int   | Maximum number of old log files to retain.                                   | `5`      |
| `use_colors`      | bool  | Enable colored console output. Automatically disabled if piping output to a file. | `True`   |
| `batch_interval`  | float | If set, enables batch writing at this interval in seconds.                   | `None`   |

---

## 📄 License

This project is licensed under the MIT License.

```
MIT License

Copyright (c) 2025 JW Drummond (MD Wade)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## ✉️ Contact

For questions, suggestions, or contributions, please open an issue or reach out directly.

---

**Your project is a journey; make sure to chronicle it.**