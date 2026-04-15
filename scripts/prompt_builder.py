from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def read_text(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}")
    return path.read_text(encoding="utf-8")


def collect_context_files(context_dir: Path) -> list[Path]:
    if not context_dir.exists():
        return []
    return sorted([p for p in context_dir.glob("*.md") if p.is_file()])


def build_prompt(task_file: Path) -> str:
    agents_file = ROOT / "AGENTS.md"
    context_dir = ROOT / "CONTEXT"

    agents_text = read_text(agents_file)
    task_text = read_text(task_file)

    context_blocks = []
    for ctx_file in collect_context_files(context_dir):
        context_blocks.append(
            f"\n--- FILE: CONTEXT/{ctx_file.name} ---\n{read_text(ctx_file)}\n"
        )

    context_text = "\n".join(context_blocks) if context_blocks else "(No context files found)"

    prompt = f"""
You are working inside the EPICS AI harness workspace.

Read and follow the agent instructions, task, and context below.

=== AGENTS.md ===
{agents_text}

=== TASK FILE: {task_file.name} ===
{task_text}

=== CONTEXT FILES ===
{context_text}

Generate exactly these output files when applicable:
- OUTPUTS/code/phytron.proto
- OUTPUTS/code/phytron.db
- OUTPUTS/code/st.cmd

Rules:
1. Return JSON only.
2. Do not wrap output in markdown code fences.
3. Put each generated file into the JSON "files" array.
4. Each item must contain:
   - "path": relative file path
   - "content": full file contents
5. Keep the code modular and commented.
6. Use StreamDevice-style EPICS file separation.
7. Generate only files that are explicitly requested.
8. Overwrite existing files if needed.
9. Do not include explanations outside JSON.
10. JSON must be valid for json.loads().
""".strip()

    return prompt