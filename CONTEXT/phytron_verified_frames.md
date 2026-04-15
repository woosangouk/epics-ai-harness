# Phytron MCC-1 Verified Frames

## Purpose

This file stores ONLY protocol data that has been directly verified
from packet captures or confirmed working communication.

Do NOT include guesses here.
Do NOT include placeholders here.

---

## Verified Communication Properties

### Framing

* STX = 0x02
* ETX = 0x03

### Communication Style

* MCC-1 uses framed byte-oriented communication
* It must NOT be treated as a generic ASCII device

### TCP Port

* Verified: 22222

---

## Verified Address Behavior

* Non-working case: address = 1
* Working case: address = 0

Conclusion:

* Address is critical
* Address = 0 is currently the only confirmed working value

---

## Verified Command Frames

### 1. getPosition

#### TX Frame (verified)

* Hex:
  02 30 58 50 32 30 52 03
* ASCII inside frame:
  "0XP20R"

#### RX Frame (verified)

* Hex:
  02 06 31 30 03

#### Interpretation

* 0x02 = STX
* 0x06 = control/status byte (meaning not fully confirmed)
* 31 30 = ASCII "10"
* 0x03 = ETX

#### Parser Candidate

* StreamDevice:
  in "\x02%*c%d\x03";

#### Status

* Framing: verified
* Payload: partially verified
* Semantic meaning: not fully confirmed

---

## Known Good Pattern

All confirmed communication follows:

STX + address + command + ETX

Example:
02 30 58 50 32 30 52 03

---

## Engineering Rules Derived

When generating protocol:

* MUST use framed format:
  \x02 ... \x03

* MUST include address byte inside payload

* MUST NOT use generic ASCII commands:

  * POS?
  * SPEED?
  * MOVE_PLUS
  * MOVE_MINUS
  * STOP

* MUST preserve verified payloads exactly as captured

---

## Not Yet Verified

The following are still unknown and must be captured:

* getSpeed
* movePlus
* moveMinus
* stopMotion

---

## Update Procedure

When new capture is obtained:

1. Add TX/RX hex here
2. Move corresponding command from "unverified" → "verified"
3. Update phytron.proto
4. Run validator
5. Confirm warnings are reduced
