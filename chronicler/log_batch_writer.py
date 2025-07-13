import threading
import queue
from typing import Union

class LogBatchWriter(threading.Thread):
    """A thread that writes log entries to a file in batches."""
    def __init__(self, log_file_path: str, interval: Union[int, float]):
        super().__init__(daemon=True)
        self.log_file_path = log_file_path
        self.interval = interval
        self.log_queue: "queue.Queue[str]" = queue.Queue()
        self._stop_event = threading.Event()

    def run(self) -> None:
        """Periodically write logs from the queue to the file."""
        while not self._stop_event.is_set():
            self._stop_event.wait(self.interval)  # Wait for the interval or a stop signal
            self.flush()

    def add(self, log_entry: str) -> None:
        """Add a log entry to the queue."""
        self.log_queue.put(log_entry)

    def flush(self) -> None:
        """Write all pending logs from the queue to the file."""
        if self.log_queue.empty():
            return
            
        # Use a list to avoid holding the lock for the whole write duration
        entries_to_write = []
        while not self.log_queue.empty():
            try:
                entries_to_write.append(self.log_queue.get_nowait())
            except queue.Empty:
                break
        
        if entries_to_write:
            try:
                with open(self.log_file_path, 'a') as f:
                    f.writelines(entries_to_write)
            except IOError as e:
                print(f"\033[91m[ERROR] (chronicler.py): Batch write failed for {self.log_file_path}. Error: {e}\033[0m", file=sys.stderr)

    def stop(self) -> None:
        """Signal the thread to stop and flush any remaining logs."""
        self.flush() # Final flush
        self._stop_event.set()