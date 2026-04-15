# Task 002: Capture MCC-1 Motion Command Frames

## Goal

Capture real MCC-1 command/response frames for currently unverified operations.

## Priority Commands

1. getSpeed
2. movePlus
3. moveMinus
4. stopMotion

## Required Evidence

For each command, capture:

* TX hex
* RX hex
* timestamp
* whether the command succeeded
* controller address used
* short human description

## Output Target

Update the following context files after capture:

* CONTEXT/phytron_capture_log.md
* CONTEXT/phytron_command_mapping.md

## Important Rule

Do not replace existing verified getPosition evidence unless new capture clearly proves otherwise.

## Expected Result

Reduce placeholder payloads in phytron.proto by replacing them with captured real frames.
