# SPDX-FileCopyrightText: Copyright 2023 Neradoc, https://neradoc.me
# SPDX-License-Identifier: MIT

import storage
import microcontroller
import usb_cdc

usb_cdc.enable(console=True, data=True)

if microcontroller.nvm[0:4] == b"RO**":
	storage.remount("/", readonly=True)
if microcontroller.nvm[0:4] == b"RW**":
	storage.remount("/", readonly=False)
