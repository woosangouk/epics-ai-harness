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