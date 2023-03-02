# SPDX-FileCopyrightText: Copyright 2023 Neradoc, https://neradoc.me
# SPDX-License-Identifier: MIT

"""
Usage:
python host-auto.py COMPORT

- set PORT to set a default com port
- set DRIVE to the drive full path (letter on windows)

1 - sends a command to the board that makes it reboot so the PC can write
2 - reads config.json and writes back some modifications to it
3 - sends a command to the board that makes it reboot so the board can write
"""
import json
import os
import psutil
import serial
import sys
import time
import adafruit_board_toolkit.circuitpython_serial

DRIVE = r"D:\\"
# DRIVE = "/Volumes/CIRCUITPY"
PORT = ""
FILE_NAME = "config.json"

############################################################################
# Customize this function to setup the data
############################################################################

def modify_the_file(content):
    """
    content: the data structure from json (usually dictionary or list).
    Modify it or ignore it, and return the data to write back.
    """
    if "timestamps" not in content or not isinstance(content["timestamps"], list):
        content["timestamps"] = []
    content["timestamps"].append(str(time.localtime()))
    return content

############################################################################
# Test the drive first
############################################################################

has_boot = os.path.exists(os.path.join(DRIVE, "boot_out.txt"))
if not has_boot:
    raise OSError(f"No {DRIVE} or no boot_out.txt in it (not a CP board)")

############################################################################
# Find the board among the serial ports
############################################################################

ports = adafruit_board_toolkit.circuitpython_serial.data_comports()
if len(sys.argv) > 1:
    PORT = sys.argv[1]
if PORT:
    for portnum, board in enumerate(ports):
        if board.device == PORT:
            break
    else:
        raise OSError(f"Board not found on {sys.argv[1]}")
else:
    # raise ValueError("No PORT given")
    portnum = 0

port = ports[portnum]
serial_number = port.serial_number
print(f"Connect to device with serial number {serial_number}\n  {port}")

############################################################################
# Reset the board in write mode (if needed)
############################################################################

print(f"Make the board go into writeable mode if necessary")
command = b"WRITE"
with serial.Serial(port.device) as board:
    board.write(command)
    try:
        # wait until the buffer is read on the other side
        while board.out_waiting:
            time.sleep(1)
        # this might crash because the board resets, so catch it
    except OSError:
        pass

print("Wait a little for reboot")
time.sleep(2)

############################################################################
# Find the drive setup at the top
############################################################################

print("Wait until the drive is mounted")
found = False
while not found:
    drives = psutil.disk_partitions()
    for drive in drives:
        if drive.mountpoint == DRIVE:
            try:
                has_boot = os.path.exists(os.path.join(DRIVE, "boot_out.txt"))
                if not has_boot:
                    raise OSError(f"No boot_out.txt in {DRIVE}")
            except (OSError, FileNotFoundError):
                print("Board (probably) not mounted (yet).")
                break
            file_path = os.path.join(DRIVE, FILE_NAME)
            try:
                with open(file_path, "r") as fp:
                    data_in = json.load(fp)
            except (OSError, FileNotFoundError):
                print(f"No {FILE_NAME}")
                data_in = {} # some default values ?
            # modify the data
            data_out = modify_the_file(data_in)
            # write back
            try:
                with open(file_path, "w") as fp:
                    json.dump(data_out, fp)
                    fp.flush()
            except (OSError, FileNotFoundError):
                print("Can't write back")
            # finish
            found = True
            break
    time.sleep(2)

print("File written (?) prepare to set the board back to RO mode")
time.sleep(2)

############################################################################
# Find the board among the serial ports
# Based on saved serial number, in case the port changed
############################################################################

print(f"Waiting for data port with SN:{serial_number}")
found = False
while not found:
    ports = adafruit_board_toolkit.circuitpython_serial.data_comports()
    for port in ports:
        if port.serial_number == serial_number:
            command = b"READ"
            found = True
            break
    time.sleep(2)

############################################################################
# Reset the board in write mode (if needed)
############################################################################

print(f"Make the board go back into read only mode")
with serial.Serial(port.device) as board:
    board.write(command)
    try:
        # wait until the buffer is read on the other side
        while board.out_waiting:
            time.sleep(1)
        # this might crash because the board resets, so catch it
    except OSError:
        pass

print("Finished")
