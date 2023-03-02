# SPDX-FileCopyrightText: Copyright 2023 Neradoc, https://neradoc.me
# SPDX-License-Identifier: MIT

import usb_cdc
import microcontroller
import time
import supervisor
# supervisor.disable_autoreload()

writeable = False
"""The ability for the board to write"""

try:
    with open("boot_out.txt","a"):
        pass
except OSError:
    writeable = False
else:
    writeable = True

while True:
    print("Doing a thing in the loop")
    if writeable:
        print("Can write to the drive")
    else:
        print("Cannot write to the drive")

    if nbytes := usb_cdc.data.in_waiting:
        data = usb_cdc.data.read(nbytes)
        print(data)
        if data[:6] == b"SWITCH":
            print("Called to switch")
            if microcontroller.nvm[0:4] == b"RW**":
                microcontroller.nvm[0:4] = b"RO**"
            else:
                microcontroller.nvm[0:4] = b"RW**"
            microcontroller.reset()
        if data[:5] == b"WRITE":
            print("The PC wants to write")
            microcontroller.nvm[0:4] = b"RO**"
            if writeable:
                microcontroller.reset()
        if data[:4] == b"READ":
            print("The PC has finished writing")
            microcontroller.nvm[0:4] = b"RW**"
            if not writeable:
                microcontroller.reset()

    time.sleep(.1)

