#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Copyright (c) 2022 YTMicro
# ******************************************************************************
# File: mlink.py
# Created Date: Sunday, November 20th 2022, 10:58:12 am
# Author: Major Lin
# ******************************************************************************
###
import time
import serial

ML_HEADER = b'\xca\xfe'
ML_TAIL = b'\xbe\xef'
# Device ID
MEM_DEVICE = b'\x01'
CANA_DEVICE = b'\x02'
CANB_DEVICE = b'\x03'
LINA_DEVICE = b'\x04'
LINB_DEVICE = b'\x05'
POSITIVE_ACK = b'OK'
TIMEOUT_COUNT = 1000


class MLink(object):
    def __init__(self, com_port, baudrate=115200):
        self.ser = serial.Serial(com_port, baudrate, timeout=0.1)
        self.buffer = b''
        self.frames = []
        self.timeout = 0

    def send(self, data):
        dl = len(data)
        dl = dl.to_bytes(2, 'little')
        chk = sum([x for x in data])
        chk = chk.to_bytes(2, 'little')
        frame = ML_HEADER + dl + data + chk + ML_TAIL
        self.ser.write(frame)

    def positive_ack(self):
        return POSITIVE_ACK == self.recv()

    def recv(self):
        while True:
            if len(self.frames) > 0:
                return self.frames.pop(0)
            else:
                self.search()
                time.sleep(0.001)
                self.timeout += 1
                if self.timeout > TIMEOUT_COUNT:
                    self.timeout = 0
                    raise TimeoutError("Timeout")

    def search(self):
        self.buffer += self.ser.read(self.ser.in_waiting)
        # Try to find header and tail
        if ML_HEADER in self.buffer and ML_TAIL in self.buffer:
            # Get header and tail index
            header_index = self.buffer.find(ML_HEADER)
            tail_index = self.buffer.find(ML_TAIL)
            # Check if header is before tail
            if header_index < tail_index:
                # Get frame
                frame = self.buffer[header_index:tail_index+2]
                # Remove frame from buffer
                self.buffer = self.buffer[tail_index+2:]
                # Check frame length
                dl = int.from_bytes(frame[2:4], 'little')
                if dl == len(frame)-8:
                    # Check frame checksum
                    chk = int.from_bytes(frame[-4:-2], 'little')
                    if chk == sum([x for x in frame[4:-4]]):
                        # Frame is valid
                        self.frames.append(frame[4:-4])
                    else:
                        print("Checksum error")
