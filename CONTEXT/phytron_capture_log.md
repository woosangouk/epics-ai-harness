# Phytron MCC-1 Capture Log

## Format

* Time:
* Operation:
* Address:
* TX Hex:
* RX Hex:
* Result:
* Notes:

---

## Entry Template

* Time: 2026-04-15 21:25
* Operation: getPosition
* Address: 0
* TX Hex: 02 30 58 50 32 30 52 03
* RX Hex: 02 06 31 30 03
* Result: success
* Notes: Wireshark capture shows framed request/reply. TX payload decodes to "0XP20R". RX appears to be STX + status/control byte + ASCII "10" + ETX.

