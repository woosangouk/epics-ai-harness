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
