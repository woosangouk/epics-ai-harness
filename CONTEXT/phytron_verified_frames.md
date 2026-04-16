## Verified Command Frames

### 1. getPosition (fully verified)

#### TX Frame

* Hex:
  02 30 58 50 32 30 52 03
* ASCII payload:
  "0XP20R"

#### RX Frame (observed variants)

* Variant A (previous capture):
  02 06 31 30 03
  → ASCII "10"

* Variant B (live IOC):
  02 06 30 03
  → ASCII "0"

#### Interpretation

* 0x02 = STX
* 0x06 = control/status byte (exact meaning not yet confirmed)
* payload = ASCII numeric value
* 0x03 = ETX

#### Parser (confirmed working)

* StreamDevice:
  `in "\x02%*c%d\x03";`

#### Observed Result

* IOC successfully polls `PHYTRON:M1:POS_RBV`
* `caget` returns numeric value
* communication confirmed stable

#### Status

* Framing: verified
* Payload: verified (position read candidate)
* Parser: verified working
* Live IOC communication: confirmed
* Semantic meaning: mostly confirmed, but still subject to final commissioning validation