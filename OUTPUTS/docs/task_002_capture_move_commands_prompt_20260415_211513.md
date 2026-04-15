You are working inside the EPICS AI harness workspace.

Read and follow the agent instructions, task, and context below.

=== AGENTS.md ===
# AI Harness Engineering Agent

## Role

You are an EPICS + Control System Engineering Assistant.

## Objective

* Generate EPICS IOC configurations
* Create .db, .proto, st.cmd files
* Assist with debugging communication (TCP/Serial)
* Support Phoebus GUI design
* Help with LLRF and RF system integration

## Rules

1. Always generate working, executable code
2. Keep structure modular
3. Separate logic, config, and interface
4. Prefer clarity over complexity
5. Include comments in all generated code

## Workflow

1. Read task from /TASKS
2. Read system context from /CONTEXT
3. Generate output into /OUTPUTS
4. Use /workspace for temporary files

## Output Format

* Code → /OUTPUTS/code/
* Docs → /OUTPUTS/docs/
* Test logs → /OUTPUTS/logs/

## Specialization

* EPICS IOC
* Phytron Motor Control
* Modbus / TCP Communication
* RF / LLRF Systems


=== TASK FILE: task_002_capture_move_commands.md ===


=== CONTEXT FILES ===

--- FILE: CONTEXT/phytron_context.md ---
# Phytron MCC-1 Context

## Device
- Model: Phytron MCC-1 MINI-W-ETH
- Communication: TCP/IP
- Port: 22222

## Goal
Generate EPICS StreamDevice files for Phytron MCC-1 motor communication.

## Important Protocol Note
This device must NOT be treated as a plain ASCII-command controller.
Do NOT assume commands like:
- POS?
- SPEED?
- MOVE_PLUS
- MOVE_MINUS
- STOP

Those are only generic scaffold placeholders and may be invalid for real MCC-1 communication.

## Verified Communication Observation
Based on Wireshark / previous successful communication traces, the controller uses framed command packets.

Example TX frame:
- 02 30 58 50 32 30 52 03

Example RX frame:
- 02 06 31 30 30 03

## Frame Structure
- 0x02 = STX
- 0x03 = ETX
- middle bytes = command + address + payload

## Address Handling
MCC-1 address is important.
Wrong address causes no response.
Observed case:
- Existing old code used MCC-1 address 1 and failed
- Updated code used MCC-1 address 0 and worked

This means the protocol generation must consider the controller address explicitly.

## Known Practical Constraint
The AI must prefer actual framed hex-based StreamDevice definitions over guessed ASCII commands.

## Expected EPICS PVs
- POS_RBV
- MOVE_PLUS
- MOVE_MINUS
- STOP
- SPEED_RBV

## StreamDevice Naming Rule
Use these exact protocol block names:
- getPosition
- getSpeed
- movePlus
- moveMinus
- stopMotion

## Generation Rules
- Use StreamDevice style separation
- Keep protocol and database separate
- Make generated files easy to debug
- Prefer framed byte commands using \\x02 ... \\x03 format if protocol details are available
- If exact command bytes are not fully known, preserve scaffold structure but add clear comments saying real command bytes must be verified

## Deployment Notes
- st.cmd should configure TCP host/port
- dbLoadRecords should use a configurable prefix macro
- asyn trace settings may remain enabled for debugging during bring-up


--- FILE: CONTEXT/phytron_unverified_commands.md ---
# Phytron MCC-1 Unverified Commands

## Purpose

This file tracks protocol payloads and parsing rules that are still placeholders or only partially inferred.

These items must NOT be treated as confirmed MCC-1 commands.
They are scaffolds for bring-up, testing, and future refinement.

Use this file together with:

* `phytron_context.md`
* `phytron_verified_frames.md`

Verified evidence must always take priority over anything listed here.

---

## Current Validation Warnings Reflected Here

The current validator reports:

* `phytron.proto` uses hardcoded address `'0'` in command payloads
* placeholder payloads are still present for:

  * `0XV20R`
  * `0XP21R`
  * `0XP22R`
  * `0XH`

This means the current scaffold is structurally valid, but some protocol details remain unverified.

---

## Address Handling Status

### Current State

* `phytron.proto` currently hardcodes controller address `0`
* `phytron.db` does not currently pass `$(ADDR)` into protocol calls
* `st.cmd` does not currently pass `ADDR` into `dbLoadRecords()`
* This is acceptable for the current scaffold because the protocol file is explicitly using address `0`

### Evidence

* Previous non-working setup used address `1`
* Observed working case used address `0`

### Engineering Interpretation

* Address handling is clearly important
* Address `0` is currently the best working candidate
* Full address parameterization is deferred until actual command bytes are better verified

### Action Later

When more protocol evidence is available, consider migrating from:

* hardcoded address in `phytron.proto`

to:

* configurable address passed through `st.cmd` → `phytron.db` → `phytron.proto`

---

## Verified / Partially Verified / Unverified Status

### 1. getPosition

Current payload:

* `0XP20R`

Current parser:

* `in "\x02%*c%d\x03";`

Status:

* **Partially verified**

Reason:

* The observed working TX example matches this frame style:

  * `02 30 58 50 32 30 52 03`
  * ASCII payload: `0XP20R`
* The response style is also partially grounded by observed traffic:

  * `02 06 31 30 30 03`

What is still not fully proven:

* whether the semantic meaning is definitely “position readback”
* whether `%d` is always the correct parser
* whether the control/status byte is always exactly one byte

Engineering note:

* Keep this as the strongest current candidate
* Do not treat it as fully verified yet

---

### 2. getSpeed

Current payload:

* `0XV20R`

Status:

* **Unverified placeholder**

Reason:

* No direct packet capture has confirmed this payload
* This command currently exists only as a scaffold

Required evidence:

* actual TX/RX capture for speed readback
* vendor protocol documentation
* previous successful code/logs

Action when evidence appears:

* replace placeholder payload
* verify parser rule separately

---

### 3. movePlus

Current payload:

* `0XP21R`

Status:

* **Unverified placeholder**

Reason:

* No direct capture confirms this command
* Placeholder chosen only to preserve framed MCC-1-style structure

Required evidence:

* actual TX frame during positive move command
* actual RX/ACK behavior
* command meaning confirmation from logs or manual

Action when evidence appears:

* replace payload with real command bytes
* optionally add explicit ACK parser if the device returns a framed acknowledgement

---

### 4. moveMinus

Current payload:

* `0XP22R`

Status:

* **Unverified placeholder**

Reason:

* No direct capture confirms this command
* Placeholder only

Required evidence:

* actual TX frame during negative move command
* actual RX/ACK behavior
* confirmation from working code or vendor command set

Action when evidence appears:

* replace payload with real command bytes
* add reply parsing only if required by actual controller behavior

---

### 5. stopMotion

Current payload:

* `0XH`

Status:

* **Unverified placeholder**

Reason:

* No direct capture confirms this command
* This is only a minimal framed stop scaffold

Required evidence:

* actual TX frame for stop command
* actual RX/ACK behavior
* confirmation from previous working command traces or documentation

Action when evidence appears:

* replace payload with real stop frame
* add acknowledgement parsing if needed

---

## Parsing Rules Still Unverified

### Current readback parser

Used pattern:

* `in "\x02%*c%d\x03";`

Status:

* **Partially plausible, not fully confirmed**

Reason:

* matches the general observed reply shape:

  * STX
  * one control/status byte
  * numeric ASCII body
  * ETX

Risks:

* some replies may contain different control/status structures
* some values may not be integer-only
* some commands may return acknowledgements rather than numeric data

Action later:

* verify parser separately for:

  * position readback
  * speed readback
  * command acknowledgements

---

## Current Engineering Policy

Until more evidence is available:

### Allowed

* keep framed protocol structure
* keep `getPosition` as the strongest current candidate
* keep placeholders clearly labeled
* keep validator warnings enabled

### Not allowed

* claiming placeholder commands are verified
* removing warnings just to get a clean PASS
* replacing framed MCC-1 style with generic ASCII guesses such as:

  * `POS?`
  * `SPEED?`
  * `MOVE_PLUS`
  * `MOVE_MINUS`
  * `STOP`

---

## Evidence Needed Next

Highest priority captures to collect next:

1. speed read command TX/RX
2. move plus TX/RX
3. move minus TX/RX
4. stop command TX/RX

For each new capture, record:

* operation name
* full TX hex
* full RX hex
* ASCII interpretation if any
* whether the address byte is confirmed
* whether the payload replaces an existing placeholder

---

## Update Procedure

When new evidence is found:

1. update `phytron_verified_frames.md` if the frame is directly confirmed
2. remove or revise the matching entry in this file
3. regenerate `phytron.proto`
4. run:

   * `python scripts/run_task.py TASKS/task_001.md`
   * `python scripts/validate_epics.py`
5. confirm whether warnings decreased

---

## Current Bottom Line

Current scaffold quality:

* structure: good
* framing direction: good
* address evidence: partially grounded
* command completeness: incomplete
* placeholder presence: expected
* validator warnings: correct and should remain enabled

This file exists to prevent placeholder commands from being mistaken for verified MCC-1 protocol truth.



--- FILE: CONTEXT/phytron_verified_frames.md ---
# Phytron MCC-1 Verified Frames

## Purpose
This file stores only protocol evidence that has been directly verified
from packet captures, working logs, or confirmed successful communication.

Do NOT put guesses here.
Do NOT put placeholder commands here.

---

## Verified Facts

### Framing
- STX = 0x02
- ETX = 0x03

### Communication Style
- MCC-1 uses framed byte-oriented communication
- It must NOT be treated as a plain generic ASCII controller

### TCP Port
- Verified controller TCP port: 22222

### Address Observation
- Previous non-working case used address 1
- Observed working case used address 0

This does NOT prove all systems always use address 0,
but it proves address handling is critical.

---

## Verified TX/RX Examples

### Example 1: Observed working request/response
TX:
- Hex: 02 30 58 50 32 30 52 03
- ASCII inside frame: 0XP20R

RX:
- Hex: 02 06 31 30 30 03
- Possible interpreted body: 100
- Note: exact semantic meaning of the 0x06 byte still needs confirmation

Status:
- Verified as observed traffic
- Exact command meaning believed related to read/query behavior
- Final semantic interpretation still partially open

---

## Evidence Source Notes
- Source type: Wireshark / packet capture / prior successful communication
- Confidence: medium-high for frame style, medium for exact command meaning

---

## Rules for AI Generation
When generating phytron.proto:
- Prefer verified framing evidence from this file
- Reuse verified byte sequences where confidence is high
- Do not replace verified observations with generic ASCII guesses
- Preserve uncertainty honestly when command semantics are not fully proven


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