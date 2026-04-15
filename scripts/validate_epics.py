from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CODE_DIR = ROOT / "OUTPUTS" / "code"
LOG_DIR = ROOT / "OUTPUTS" / "logs"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def extract_proto_blocks(proto_text: str) -> set[str]:
    pattern = re.compile(r'^\s*([A-Za-z_]\w*)\s*\{', re.MULTILINE)
    return set(pattern.findall(proto_text))


def extract_db_protocol_refs(db_text: str) -> list[tuple[str, str]]:
    """
    Finds protocol references like:
      @phytron.proto getPosition($(ADDR)) $(PORT)
      @phytron.proto movePlus($(ADDR)) $(PORT)
    Returns:
      [(full_ref, block_name), ...]
    """
    pattern = re.compile(r'@phytron\.proto\s+([A-Za-z_]\w*)')
    refs = []
    for match in pattern.finditer(db_text):
        block_name = match.group(1)
        refs.append((match.group(0), block_name))
    return refs


def check_contains(text: str, keyword: str) -> tuple[bool, str]:
    if keyword in text:
        return True, f"[OK] Found: {keyword}"
    return False, f"[FAIL] Missing: {keyword}"


def add_result(results: list[str], level: str, message: str) -> None:
    results.append(f"[{level}] {message}")


def main() -> None:
    proto_file = CODE_DIR / "phytron.proto"
    db_file = CODE_DIR / "phytron.db"
    stcmd_file = CODE_DIR / "st.cmd"

    results: list[str] = []
    failed = False
    warned = False

    # 1) File existence
    for f in [proto_file, db_file, stcmd_file]:
        if f.exists():
            add_result(results, "OK", f"File exists: {f}")
        else:
            add_result(results, "FAIL", f"File missing: {f}")
            failed = True

    proto_text = read_text(proto_file) if proto_file.exists() else ""
    db_text = read_text(db_file) if db_file.exists() else ""
    stcmd_text = read_text(stcmd_file) if stcmd_file.exists() else ""

    # 2) Required PV checks in DB
    db_keywords = [
        "POS_RBV",
        "MOVE_PLUS",
        "MOVE_MINUS",
        "STOP",
        "SPEED_RBV",
    ]
    for kw in db_keywords:
        ok, msg = check_contains(db_text, kw)
        results.append(msg)
        if not ok:
            failed = True

    # 3) Required st.cmd checks
    stcmd_keywords = [
        "drvAsynIPPortConfigure",
        "dbLoadRecords",
        "22222",
    ]
    for kw in stcmd_keywords:
        ok, msg = check_contains(stcmd_text, kw)
        results.append(msg)
        if not ok:
            failed = True

    # 4) Required proto block existence
    required_proto_blocks = [
        "getPosition",
        "getSpeed",
        "movePlus",
        "moveMinus",
        "stopMotion",
    ]
    proto_blocks = extract_proto_blocks(proto_text)

    for block in required_proto_blocks:
        if block in proto_blocks:
            add_result(results, "OK", f"Found protocol block: {block}")
        else:
            add_result(results, "FAIL", f"Missing protocol block: {block}")
            failed = True

    # 5) DB -> proto reference consistency
    db_refs = extract_db_protocol_refs(db_text)
    if not db_refs:
        add_result(results, "FAIL", "No @phytron.proto references found in phytron.db")
        failed = True
    else:
        for full_ref, block_name in db_refs:
            if block_name in proto_blocks:
                add_result(results, "OK", f"DB reference matches proto block: {block_name}")
            else:
                add_result(results, "FAIL", f"DB references missing proto block: {block_name}")
                failed = True

        # 6) DB macro expectations
    db_uses_addr = "$(ADDR)" in db_text
    db_uses_port = "$(PORT)" in db_text

    if db_uses_addr:
        add_result(results, "OK", "DB uses $(ADDR) macro")
    else:
        add_result(results, "OK", "DB does not use $(ADDR) macro (address handled elsewhere or hardcoded)")

    if db_uses_port:
        add_result(results, "OK", "DB uses $(PORT) macro")
    else:
        add_result(results, "FAIL", "DB does not use $(PORT) macro")
        failed = True

    # 7) st.cmd macro delivery checks
    stcmd_has_addr_macro = "ADDR=" in stcmd_text
    stcmd_has_port_macro = "PORT=" in stcmd_text

    if stcmd_has_addr_macro:
        add_result(results, "OK", "st.cmd passes ADDR macro")
    else:
        if db_uses_addr:
            add_result(results, "FAIL", "DB expects $(ADDR) but st.cmd does not pass ADDR=")
            failed = True
        else:
            add_result(results, "OK", "st.cmd does not pass ADDR macro because DB does not require it")

    if stcmd_has_port_macro:
        add_result(results, "OK", "st.cmd passes PORT macro")
    else:
        if db_uses_port:
            add_result(results, "FAIL", "DB expects $(PORT) but st.cmd does not pass PORT=")
            failed = True
        else:
            add_result(results, "WARN", "st.cmd does not pass PORT macro")
            warned = True

    # 8) Framed protocol checks in proto
    has_stx = r'\x02' in proto_text
    has_etx = r'\x03' in proto_text

    if has_stx:
        add_result(results, "OK", r"Protocol uses STX (\x02)")
    else:
        add_result(results, "FAIL", r"Protocol missing STX (\x02)")
        failed = True

    if has_etx:
        add_result(results, "OK", r"Protocol uses ETX (\x03)")
    else:
        add_result(results, "FAIL", r"Protocol missing ETX (\x03)")
        failed = True

    # 9) Hardcoded address detection in proto
    # Detect common hardcoded address patterns like "0XP20R", "0XV20R", etc.
    hardcoded_addr_patterns = [
        r'"0[A-Z]',
        r"'0[A-Z]",
    ]
    hardcoded_found = any(re.search(pat, proto_text) for pat in hardcoded_addr_patterns)

    if hardcoded_found:
        add_result(
            results,
            "WARN",
            "phytron.proto appears to use hardcoded address '0' in command payloads"
        )
        warned = True
    else:
        add_result(results, "OK", "No obvious hardcoded address '0' detected in proto payloads")

         # 10) Placeholder payload detection
    placeholder_payloads = [
        "0XV20R",   # getSpeed placeholder
        "0XP21R",   # movePlus placeholder
        "0XP22R",   # moveMinus placeholder
        "0XH",      # stopMotion placeholder
    ]

    found_placeholders = []
    for payload in placeholder_payloads:
        if payload in proto_text:
            found_placeholders.append(payload)

    if found_placeholders:
        add_result(
            results,
            "WARN",
            "Placeholder command payloads detected in phytron.proto: "
            + ", ".join(found_placeholders)
        )
        warned = True
    else:
        add_result(results, "OK", "No known placeholder command payloads detected")

    # 11) Summary
    if failed:
        summary = "[RESULT] FAIL"
    elif warned:
        summary = "[RESULT] PASS WITH WARNINGS"
    else:
        summary = "[RESULT] PASS"

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = LOG_DIR / f"validate_epics_{timestamp}.log"

    content = summary + "\n" + "\n".join(results) + "\n"

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_file.write_text(content, encoding="utf-8")

    print(content)
    print(f"[INFO] Validation log written: {log_file}")


if __name__ == "__main__":
    main()