from __future__ import annotations
import subprocess
import json
import os
import sys
from datetime import datetime
from pathlib import Path

from openai import OpenAI
from prompt_builder import build_prompt


ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DOCS = ROOT / "OUTPUTS" / "docs"
OUTPUT_LOGS = ROOT / "OUTPUTS" / "logs"


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def save_generated_files(files: list[dict]) -> list[Path]:
    saved_paths: list[Path] = []

    for item in files:
        rel_path = item["path"]
        content = item["content"]

        out_path = ROOT / rel_path
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(content, encoding="utf-8")
        saved_paths.append(out_path)

    return saved_paths


def call_openai(prompt: str) -> str:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set.")

    client = OpenAI(api_key=api_key)

    schema = {
        "type": "object",
        "properties": {
            "files": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"},
                        "content": {"type": "string"}
                    },
                    "required": ["path", "content"],
                    "additionalProperties": False
                }
            }
        },
        "required": ["files"],
        "additionalProperties": False
    }

    response = client.responses.create(
        model="gpt-5.4",
        instructions=(
            "You are an EPICS control-system code generator. "
            "Return only valid JSON matching the schema. "
            "Generate exactly the requested files. "
            "Do not include markdown fences."
        ),
        input=prompt,
        text={
            "format": {
                "type": "json_schema",
                "name": "generated_files",
                "schema": schema,
                "strict": True
            }
        }
    )

    return response.output_text


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("Usage: python scripts/run_task.py TASKS/task_xxx.md")

    task_file = Path(sys.argv[1]).resolve()
    if not task_file.exists():
        raise FileNotFoundError(f"Task file not found: {task_file}")

    prompt = build_prompt(task_file)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    prompt_out = OUTPUT_DOCS / f"{task_file.stem}_prompt_{timestamp}.md"
    log_out = OUTPUT_LOGS / f"{task_file.stem}_run_{timestamp}.log"
    raw_out = OUTPUT_DOCS / f"{task_file.stem}_response_{timestamp}.json"

    write_text(prompt_out, prompt)

    try:
        raw_json = call_openai(prompt)
        write_text(raw_out, raw_json)

        data = json.loads(raw_json)
        files = data.get("files", [])
        saved_paths = save_generated_files(files)

        log_lines = [
            f"[INFO] Task processed: {task_file.name}",
            f"[INFO] Prompt written to: {prompt_out}",
            f"[INFO] Raw response written to: {raw_out}",
            "[INFO] Saved files:"
        ]
        log_lines.extend([f"  - {p}" for p in saved_paths])

        write_text(log_out, "\n".join(log_lines) + "\n")

        print(f"[RUN_TASK] Prompt written: {prompt_out}")
        print(f"[RUN_TASK] Raw response written: {raw_out}")
        print("[RUN_TASK] Saved files:")
        for path in saved_paths:
            print(f"  - {path}")

                    # Run validation automatically after generation
        validator = ROOT / "scripts" / "validate_epics.py"
        print(f"[RUN_TASK] Running validator: {validator}")
        subprocess.run(
            [sys.executable, str(validator)],
            check=True,
            cwd=str(ROOT),
        )

    except Exception as exc:
        write_text(
            log_out,
            f"[ERROR] Task failed: {task_file.name}\n"
            f"[ERROR] {exc}\n"
            f"[INFO] Prompt written to: {prompt_out}\n",
        )
        print(f"[RUN_TASK] Failed: {exc}")
        raise


if __name__ == "__main__":
    main()