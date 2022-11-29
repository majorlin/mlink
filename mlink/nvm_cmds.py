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
import elftools.elf.elffile as elffile
from .mlog import logger


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
        logger.info('Erasing 0x{:08X} - 0x{:08X}'.format(addr, addr + size))
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
        logger.info('Swapping firmware')
        data = MEM_DEVICE + self.MEM_SWAP
        self.mlink.send(data)
        # Device will reset after swap, no response

    def memory_write(self, addr, data):
        logger.info('Writing 0x{:08X} - 0x{:08X}'.format(addr, addr + len(data)))
        data = MEM_DEVICE + self.MEM_WRITE + addr.to_bytes(4, 'little') + len(data).to_bytes(4, 'little') + data
        self.mlink.send(data)
        return self.mlink.positive_ack()

    def update_firmware(self, elf_file, offset=0):
        elf = elffile.ELFFile(open(elf_file, 'rb'))
        for segment in elf.iter_segments():
            if segment.header.p_type == 'PT_LOAD' and segment.header.p_paddr < 0x10000000:
                # size align to 2K bytes
                size = (segment.header.p_memsz + 2047) & 0xFFFFF800
                # address align to 2K bytes
                addr = segment.header.p_paddr & 0xFFFFF800
                self.memory_erase(addr + offset, size)
        for segment in elf.iter_segments():
            if segment.header.p_type == 'PT_LOAD' and segment.header.p_paddr < 0x10000000:
                # check address is 8 bytes aligned
                if segment.header.p_paddr & 0x7 != 0:
                    raise Exception('Address is not 8 bytes aligned')
                # extern data will be filled with 0xFF
                data_size = segment.header.p_filesz
                # check if size is align with 8 byte
                if data_size % 8 != 0:
                    data = segment.data() + b'\xFF' * (8 - segment.header.p_filesz % 8)
                    data_size = len(data)
                else:
                    data = segment.data()
                for i in range(0, data_size, 256):
                    self.memory_write(segment.header.p_paddr + i + offset, data[i:i + 256])
        self.memory_swap()
