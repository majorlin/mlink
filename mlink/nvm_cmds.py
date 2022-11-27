#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# Copyright (c) 2022 YTMicro
# ******************************************************************************
# File: nvm_cmds.py
# Created Date: 2022/11/26 - 10:04
# Author: Major Lin
# ******************************************************************************

from .mlink import MLink
from .mlink import MEM_DEVICE
import elftools


class NvmCmd(object):
    # Memory Commands
    MEM_ERASE = b'\x01\x00\x00'
    MEM_WRITE = b'\x02\x00\x00'
    MEM_READ = b'\x03\x00\x00'
    MEM_UPLOAD = b'\x04\x00\x00'
    MEM_JUMP = b'\x05\x00\x00'
    MEM_SWAP = b'\x06\x00\x00'

    def __init__(self, mlink: MLink):
        self.mlink = mlink

    def memory_read(self, addr, size):
        data = MEM_DEVICE + self.MEM_READ + addr.to_bytes(4, 'little') + size.to_bytes(4, 'little')
        self.mlink.send(data)
        return self.mlink.recv()

    def memory_erase(self, addr, size):
        data = MEM_DEVICE + self.MEM_ERASE + addr.to_bytes(4, 'little') + size.to_bytes(4, 'little')
        self.mlink.send(data)
        return self.mlink.positive_ack()

    def memory_upload(self, addr, size):
        data = MEM_DEVICE + self.MEM_UPLOAD + addr.to_bytes(4, 'little') + size.to_bytes(4, 'little')
        self.mlink.send(data)
        return self.mlink.recv()

    def memory_jump(self, addr):
        data = MEM_DEVICE + self.MEM_JUMP + addr.to_bytes(4, 'little')
        self.mlink.send(data)
        # Device will reset after jump, no response

    def memory_swap(self):
        data = MEM_DEVICE + self.MEM_SWAP
        self.mlink.send(data)
        # Device will reset after swap, no response

    def memory_write(self, addr, data):
        data = MEM_DEVICE + self.MEM_WRITE + addr.to_bytes(4, 'little') + len(data).to_bytes(4, 'little') + data
        self.mlink.send(data)
        return self.mlink.positive_ack()

    def update_firmware(self, elf_file):
        elf = elftools.elf.elffile.ELFFile(elf_file)
        for segment in elf.iter_segments():
            if segment.header.p_type == 'PT_LOAD':
                self.memory_erase(segment.header.p_paddr, segment.header.p_memsz)
                self.memory_write(segment.header.p_paddr, segment.data())
