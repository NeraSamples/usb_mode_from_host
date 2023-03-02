# SPDX-FileCopyrightText: Copyright 2023 Neradoc, https://neradoc.me
# SPDX-License-Identifier: MIT

"""
Valid commands:
SWITCH
READ  - leaves the drive in read only mode
WRITE - allows the python code to write to the drive
"""
import serial
import sys
import time

if len(sys.argv) > 1:
    port = sys.argv[1]
else:
    raise ValueError("No COM port given")

if len(sys.argv) > 2:
    command = sys.argv[2].encode("utf8")
else:
    command = b"SWITCH\r\n"

print(f"Send {command} to {port}")
with serial.Serial(port) as board:
    try:
        board.write(command)
        while board.out_waiting:
            time.sleep(1)
    except Exception:
        pass
