#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# Copyright (c) 2022 YTMicro
# ******************************************************************************
# File: can_cmds.py
# Created Date: 2022/11/29 - 19:59
# Author: Major Lin
# ******************************************************************************
from .mlink import MLink
from .mlink import CANA_DEVICE
from .mlink import CANB_DEVICE
from .mlog import logger
from can import Message

# bit rate to be used for the CANAL interface

BitRateLut75 = {
    # BitRate: Prescaler PROGPSE PSEG1 PSEG2 RJW SamplePoint
    "250": [20, 4, 13, 6, 6, 75],
    "500": [10, 7, 10, 6, 6, 75],
    "750": [4, 16, 13, 10, 10, 75],
    "1000": [2, 31, 13, 15, 15, 75],
}
BitRateLut80 = {
    # BitRate: Prescaler PROGPSE PSEG1 PSEG2 RJW SamplePoint
    "250": [48, 2, 5, 2, 2, 80],
    "500": [24, 3, 4, 2, 2, 80],
    "750": [16, 4, 3, 2, 2, 80],
    "1000": [12, 6, 1, 2, 2, 80],
}
DataBitRateLut75 = {
    # BitRate: Prescaler PROGPSE PSEG1 PSEG2 RJW SamplePoint
    "1000": [1, 10, 7, 6, 6, 75],
    "2000": [1, 30, 14, 15, 15, 75],
    "3000": [5, 2, 3, 2, 2, 75],
    "4000": [1, 13, 9, 7, 7, 75],
    "5000": [1, 10, 7, 6, 6, 75],
    "6000": [1, 8, 6, 5, 5, 75],
    "8000": [1, 6, 4, 4, 4, 73],
}
DataRateLut80 = {
    # BitRate: Prescaler PROGPSE PSEG1 PSEG2 RJW SamplePoint
    "1000": [4, 1, 3, 1, 1, 83],
    "2000": [6, 5, 2, 2, 2, 80],
    "3000": [8, 1, 2, 1, 1, 80],
    "4000": [3, 3, 4, 2, 2, 80],
    "5000": [4, 1, 3, 1, 1, 83],
    "6000": [2, 3, 4, 2, 2, 80],
    "8000": [3, 1, 2, 1, 1, 80],
}

CAN_CFG_FD_MODE = 0x01 << 2
CAN_CFG_LISTEN_ONLY_MODE = 0x01 << 7
CAN_CFG_LOOP_MODE = 0x01 << 6
CAN_CFG_RETRY_MODE = 0x01 << 4

CAN_MSG_RTR = 0x01 << 7
CAN_MSG_EXT = 0x01 << 6
CAN_MSG_FD = 0x01 << 5
CAN_MSG_BRS = 0x01 << 4


class CanCmd(object):
    # Memory Commands
    CAN_RESET = b'\x01'
    CAN_OPEN = b'\x02'
    CAN_CLOSE = b'\x03'
    CAN_SEND = b'\x11'
    CAN_RECEIVE = b'\x12'
    CAN_FILTER = b'\x13'
    CAN_ERROR = b'\x21'

    def __init__(self, mlink: MLink, can_device=0):
        self.can_device = CANA_DEVICE if can_device == 0 else CANB_DEVICE
        self.mlink = mlink
        self.fd = True
        self.can_lut = {CANA_DEVICE: "CAN-A", CANB_DEVICE: "CAN-B"}

    def can_reset(self):
        logger.info('Reset %s' % self.can_lut[self.can_device])
        logger.info('Open %s with bit rate %d' % (self.can_lut[self.can_device], bit_rate))
        data = self.can_device + self.CAN_RESET + b'\x00' + b'\x00'
        self.mlink.send(data)
        return self.mlink.positive_ack(self.can_device)

    def can_open(self, bit_rate=500, data_bit_rate=2000, fd=True):
        logger.info('Open %s with bit rate %d' % (self.can_lut[self.can_device], bit_rate))
        bit_rate = str(bit_rate)
        data_bit_rate = str(data_bit_rate)
        if bit_rate in BitRateLut75:
            bit_rate_lut = BitRateLut75[bit_rate]
        else:
            bit_rate_lut = BitRateLut75["500"]
        if data_bit_rate in DataBitRateLut75:
            data_bit_rate_lut = DataBitRateLut75[data_bit_rate]
        else:
            data_bit_rate_lut = DataBitRateLut75["2000"]
        self.fd = fd
        cfg = 0
        if self.fd:
            cfg = cfg | CAN_CFG_FD_MODE
        data = self.can_device + self.CAN_OPEN + cfg.to_bytes(1, 'little') + \
            b'\x00\x00' + \
            bit_rate_lut[0].to_bytes(1, 'little') + \
            bit_rate_lut[1].to_bytes(1, 'little') + \
            bit_rate_lut[2].to_bytes(1, 'little') + \
            bit_rate_lut[3].to_bytes(1, 'little') + \
            bit_rate_lut[4].to_bytes(1, 'little') + \
            data_bit_rate_lut[0].to_bytes(1, 'little') + \
            data_bit_rate_lut[1].to_bytes(1, 'little') + \
            data_bit_rate_lut[2].to_bytes(1, 'little') + \
            data_bit_rate_lut[3].to_bytes(1, 'little') + \
            data_bit_rate_lut[4].to_bytes(1, 'little')
        self.mlink.send(data)

    def can_close(self):
        logger.info('Close %s' % self.can_lut[self.can_device])
        data = self.can_device + self.CAN_CLOSE + b'\x00' + b'\x00'
        self.mlink.send(data)
        return self.mlink.positive_ack(self.can_device)

    def can_send(self, msg: Message):
        logger.info('Send %s' % self.can_lut[self.can_device])
        flags = 0
        if msg.is_extended_id:
            flags |= CAN_MSG_EXT
        if msg.is_remote_frame:
            flags |= CAN_MSG_RTR
        if self.fd:
            flags |= CAN_MSG_FD
            if msg.bitrate_switch:
                flags |= CAN_MSG_BRS
        data = self.can_device + self.CAN_SEND + \
            msg.dlc.to_bytes(1, 'little') + \
            flags.to_bytes(1, 'little') + \
            int(msg.timestamp).to_bytes(4, 'little') + \
            msg.arbitration_id.to_bytes(4, 'little') + \
            msg.data
        self.mlink.send(data)
        logger.info('Send: %s', msg)

    def can_receive(self):
        self.mlink.recv(self.can_device)
        packet = self.mlink.check(self.can_device)
        if packet is None:
            return None
        if packet[0] == self.can_device and packet[1] == self.CAN_RECEIVE:
            msg = Message()
            msg.dlc = packet[2]
            msg.is_extended_id = packet[3] & CAN_MSG_EXT
            msg.is_remote_frame = packet[3] & CAN_MSG_RTR
            msg.timestamp = int.from_bytes(packet[4:8], 'little')
            msg.arbitration_id = int.from_bytes(packet[8:12], 'little')
            msg.data = packet[12:12 + msg.dlc]
            logger.info('Receive CAN: %s', msg)
            return msg
