#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# Copyright (c) 2022 YTMicro
# ******************************************************************************
# File: main.py
# Created Date: 2022/11/27 - 08:20
# Author: Major Lin
# ******************************************************************************

from mlink.nvm_cmds import NvmCmd
from mlink.mlink import MLink

if __name__ == '__main__':
    mlink = MLink("/dev/ttyUSB0")
    nvm = NvmCmd(mlink)
    print(nvm.memory_read(0, 100))
