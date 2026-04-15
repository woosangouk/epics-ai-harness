from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


ROOT = Path(__file__).resolve().parent.parent
TASKS_DIR = ROOT / "TASKS"
RUNNER = ROOT / "scripts" / "run_task.py"


class TaskChangeHandler(FileSystemEventHandler):
    def __init__(self) -> None:
        super().__init__()
        self._last_run: dict[str, float] = {}

    def _should_handle(self, path: Path) -> bool:
        if path.suffix.lower() != ".md":
            return False
        if not path.name.startswith("task_"):
            return False

        now = time.time()
        last = self._last_run.get(str(path), 0.0)

        if now - last < 2.0:
            return False

        self._last_run[str(path)] = now
        return True

    def _run_task(self, task_path: Path) -> None:
        print(f"[WATCHER] Task detected: {task_path.name}")
        try:
            subprocess.run(
                [sys.executable, str(RUNNER), str(task_path)],
                check=True,
                cwd=str(ROOT),
            )
        except subprocess.CalledProcessError as exc:
            print(f"[WATCHER] Failed to run task: {exc}")

    def on_created(self, event) -> None:
        if event.is_directory:
            return
        path = Path(event.src_path)
        if self._should_handle(path):
            self._run_task(path)

    def on_modified(self, event) -> None:
        if event.is_directory:
            return
        path = Path(event.src_path)
        if self._should_handle(path):
            self._run_task(path)


def main() -> None:
    if not TASKS_DIR.exists():
        raise FileNotFoundError(f"TASKS directory not found: {TASKS_DIR}")

    print(f"[WATCHER] Watching: {TASKS_DIR}")
    print("[WATCHER] Press Ctrl+C to stop.")

    event_handler = TaskChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, str(TASKS_DIR), recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[WATCHER] Stopping...")
        observer.stop()

    observer.join()


if __name__ == "__main__":
    main()