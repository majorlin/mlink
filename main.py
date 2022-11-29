#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# Copyright (c) 2022 YTMicro
# ******************************************************************************
# File: main.py
# Created Date: 2022/11/27 - 08:20
# Author: Major Lin
# ******************************************************************************

from mlink.nvm_cmds import NvmCmd
from mlink.can_cmds import CanCmd
from mlink.mlink import MLink
from can import Message
import time

if __name__ == '__main__':
    mlink = MLink("/dev/cu.usbserial-10", baudrate=2000000, dry=False)
    mlink.version()
    nvm = NvmCmd(mlink)
    canA = CanCmd(mlink, 0)
    canB = CanCmd(mlink, 1)
    canA.can_open()
    canB.can_open()
    msg = Message(arbitration_id=0x123, data=[0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88])
    canA.can_send(msg)
    time.sleep(1)
    canB.can_receive()
    # nvm.update_firmware("YTKit.elf", offset=0x80000)

