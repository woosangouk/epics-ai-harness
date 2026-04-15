# Task 001: Phytron MCC-1 Motor IOC

## Goal
Create EPICS IOC scaffold for Phytron MCC-1 MINI-W-ETH using StreamDevice over TCP/IP.

## Required Outputs
- OUTPUTS/code/phytron.proto
- OUTPUTS/code/phytron.db
- OUTPUTS/code/st.cmd

## Required PVs
- POS_RBV
- MOVE_PLUS
- MOVE_MINUS
- STOP
- SPEED_RBV

## Critical Requirements
- Use TCP communication on port 22222
- Use StreamDevice file separation
- Use these exact protocol block names:
  - getPosition
  - getSpeed
  - movePlus
  - moveMinus
  - stopMotion

## Important Constraint
Do NOT invent generic ASCII commands such as:
- POS?
- SPEED?
- MOVE_PLUS
- MOVE_MINUS
- STOP

unless they are explicitly justified by the provided protocol evidence.

## Protocol Requirement
Prefer framed byte-based protocol definitions using:
- STX = \\x02
- ETX = \\x03

The generated .proto should reflect real MCC-1 frame style whenever enough context is available.

## Address Requirement
The MCC-1 address matters.
The task must consider that previous non-working code used one address and the working case used another.
If the exact address handling is still not fully specified, add comments in the generated files showing where the address must be inserted or adjusted.

## Debug Requirement
Generated files must include comments indicating:
- which command bytes are verified
- which command bytes are placeholders
- where address handling must be checked during commissioning

## Output Quality
- Keep code modular
- Keep comments clear
- Make validation and debugging easy