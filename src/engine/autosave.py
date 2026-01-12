import threading
import time
from typing import Callable

class AutoSaveService:
    def __init__(self, callback: Callable, interval_seconds: int = 60):
        self.callback = callback
        self.interval = interval_seconds
        self._running = False
        self._thread = None
        self._stop_event = threading.Event()

    def start(self):
        if self._running: return
        self._running = True
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=1.0)

    def _loop(self):
        while self._running and not self._stop_event.is_set():
            # Sleep in small chunks to allow faster stopping
            for _ in range(self.interval):
                if self._stop_event.is_set(): return
                time.sleep(1)
            
            if self._running and not self._stop_event.is_set():
                try:
                    self.callback()
                except Exception as e:
                    print(f"AutoSave Error: {e}")
