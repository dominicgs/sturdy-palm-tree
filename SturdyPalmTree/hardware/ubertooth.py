#!/usr/bin/env python
"""
Copyright 2013 - 2016 Ryan Holeman
Copyright 2016 Dominic Spill

This file is part of sturdy palm tree.

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2, or (at your option)
any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; see the file COPYING.  If not, write to
the Free Software Foundation, Inc., 51 Franklin Street,
Boston, MA 02110-1301, USA."""

import array
import usb.core
import time
import struct
from cc2400 import Registers
from enum import IntEnum
from itertools import izip


class U1_USB(IntEnum):
    PING = 0
    RX_SYMBOLS = 1
    TX_SYMBOLS = 2
    GET_USRLED = 3
    SET_USRLED = 4
    GET_RXLED = 5
    SET_RXLED = 6
    GET_TXLED = 7
    SET_TXLED = 8
    GET_1V8 = 9
    SET_1V8 = 10
    GET_CHANNEL = 11
    SET_CHANNEL = 12
    RESET = 13
    GET_SERIAL = 14
    GET_PARTNUM = 15
    GET_PAEN = 16
    SET_PAEN = 17
    GET_HGM = 18
    SET_HGM = 19
    TX_TEST = 20
    STOP = 21
    GET_MOD = 22
    SET_MOD = 23
    SET_ISP = 24
    FLASH = 25
    BOOTLOADER_FLASH = 26
    SPECAN = 27
    GET_PALEVEL = 28
    SET_PALEVEL = 29
    REPEATER = 30
    RANGE_TEST = 31
    RANGE_CHECK = 32
    GET_REV_NUM = 33
    LED_SPECAN = 34
    GET_BOARD_ID = 35
    SET_SQUELCH = 36
    GET_SQUELCH = 37
    SET_BDADDR = 38
    START_HOPPING = 39
    SET_CLOCK = 40
    GET_CLOCK = 41
    BTLE_SNIFFING = 42
    GET_ACCESS_ADDRESS = 43
    SET_ACCESS_ADDRESS = 44
    DO_SOMETHING = 45
    DO_SOMETHING_REPLY = 46
    GET_CRC_VERIFY = 47
    SET_CRC_VERIFY = 48
    POLL = 49
    BTLE_PROMISC = 50
    SET_AFHMAP = 51
    CLEAR_AFHMAP = 52
    READ_REGISTER = 53
    BTLE_SLAVE = 54
    GET_COMPILE_INFO = 55
    BTLE_SET_TARGET = 56
    BTLE_PHY = 57
    WRITE_REGISTER = 58
    JAM_MODE = 59
    EGO = 60
    AFH = 61
    HOP = 62
    TRIM_CLOCK = 63
    GET_API_VERSION = 64
    WRITE_REGISTERS = 65
    READ_ALL_REGISTERS = 66


class Ubertooth(object):
    # TODO: add support for multiple ubertooth devices
    def __init__(self, device=True, infile=None, outfile=None):
        if device:
            self.device = self._init_device()
        else:
            self.device = None

        if infile:
            self.infile = open(infile, 'rb')
        else:
            infile = None

    def _init_device(self):
        device = usb.core.find(idVendor=0x1D50, idProduct=0x6002)
        device.default_timeout = 3000
        device.set_configuration()
        return device

    def set_rx_mode(self, channel=None):
        self.device.ctrl_transfer(0x40, 1, 0, 0)

    def rx_file_stream(self, count=None, secs=None):
        i = 0
        start = time.time()
        while True:
            buffer = array.array('B')
            try:
                buffer.fromfile(self.infile, 68)
            except:
                break
            if count is not None:
                if i >= count:
                    break
                i += 1
            if secs is not None:
                if time.time() >= start+secs:
                    break
            yield buffer

    def rx_stream(self, count=None, secs=None):
        self.set_rx_mode()
        i = 0
        start = time.time()
        while True:
            buffer = self.device.read(0x82, 64)
            if count is not None:
                if i >= count:
                    print i
                    break
                i += 1
            if secs is not None:
                if time.time() >= start+secs:
                    break
            yield buffer

    def close(self):
        self.device.ctrl_transfer(0x40, U1_USB.STOP)
        self.device.ctrl_transfer(0x40, U1_USB.RESET)

    # Start new stuff 4/27/16
    def cmd_trim_clock(self):
        # trim clock
        # line 65 ubertooth_control.c
        # THIS IS AN UBERTOOTH ASYNC COMMAND
        pass

    def cmd_ping(self):
        # cmd ping
        # line 75 ubertooth_control.c
        result = self.device.ctrl_transfer(0xc0, U1_USB.PING, 0, 0, 0)
        return result

    def cmd_rx_syms(self):
        # already implemented above
        # set rx mode
        # line 88 ubertooth_control.c
        self.device.ctrl_transfer(0x40, U1_USB.RX_SYMBOLS, 0, 0)

    def cmd_specan(self, low_freq=2402, high_freq=2480):
        # specan where low_freq & high_freq is 2402-2480
        # line 101 ubertooth_control.c
        self.device.ctrl_transfer(0x40, U1_USB.SPECAN, low_freq, high_freq)

    def cmd_set_usrled(self, state=0):
        # set usrled where state is 0-1
        # line 127 ubertooth_control.c
        self.device.ctrl_transfer(0x40, U1_USB.SET_USRLED, state, 0)

    def cmd_get_usrled(self):
        # get usrled where state is 0-1
        # line 140 ubertooth_control.c
        state = self.device.ctrl_transfer(0xc0, U1_USB.GET_USRLED, 0, 0, 1)
        state = struct.unpack('b', state)[0]
        return state

    def cmd_set_rxled(self, state=0):
        # set rxled where state is 0-1
        # line 154 ubertooth_control.c
        self.device.ctrl_transfer(0x40, U1_USB.SET_RXLED, state, 0)

    def cmd_get_rxled(self):
        # get rxled where state is 0-1
        # line 167 ubertooth_control.c
        state = self.device.ctrl_transfer(0xc0, U1_USB.GET_RXLED, 0, 0, 1)
        state = struct.unpack('b', state)[0]
        return state

    def cmd_set_txled(self, state=0):
        # set txled where state is 0-1
        # line 181 ubertooth_control.c
        self.device.ctrl_transfer(0x40, U1_USB.SET_TXLED, state, 0)

    def cmd_get_txled(self):
        # get txled where state is 0-1
        # line 194 ubertooth_control.c
        state = self.device.ctrl_transfer(0xc0, U1_USB.GET_TXLED, 0, 0, 1)
        state = struct.unpack('b', state)[0]
        return state

    def cmd_get_partnum(self):
        # get partnum where result=0 for success and part is in hex format
        # line 257 ubertooth_control.c
        part = self.device.ctrl_transfer(0xc0, U1_USB.GET_PARTNUM, 0, 0, 5)
        result = struct.unpack('B', part[0:1])[0]
        part = hex(struct.unpack('<I', part[1:])[0])
        return part

    def cmd_get_serial(self):
        # get serial where result=0 for success
        # line 287 ubertooth_control.c
        serial = self.device.ctrl_transfer(0xc0, U1_USB.GET_SERIAL, 0, 0, 17)
        result = struct.unpack('B', serial[0:1])[0]
        serial = struct.unpack('>4i', serial[1:])
        serial = ''.join([format(i, 'x') for i in serial])
        return serial

    def cmd_set_isp(self):
        # set isp mode (in system programing)
        # line 319 ubertooth_control.c
        self.device.ctrl_transfer(0x40, U1_USB.SET_ISP, 0, 0)

    def cmd_reset(self):
        # reset ubertooth
        # line 334 ubertooth_control.c
        self.device.ctrl_transfer(0x40, U1_USB.RESET, 0, 0)

    def cmd_stop(self):
        # stop ubertooth
        # line 349 ubertooth_control.c
        self.device.ctrl_transfer(0x40, U1_USB.STOP, 0, 0)

    def cmd_set_paen(self, state=-1):
        # set paen where state ???
        # line 365 ubertooth_control.c
        self.device.ctrl_transfer(0x40, U1_USB.SET_PAEN, state, 0)

    def cmd_set_hgm(self, state=-1):
        # set hgm where state ???
        # line 381 ubertooth_control.c
        self.device.ctrl_transfer(0x40, U1_USB.SET_HGM, state, 0)

    def cmd_flash(self):
        # flash mode
        # line 413 ubertooth_control.c
        self.device.ctrl_transfer(0x40, U1_USB.FLASH, 0, 0)

    def cmd_get_palevel(self):
        # get palevel (power amplifier level)
        # line 427 ubertooth_control.c
        level = self.device.ctrl_transfer(0xc0, U1_USB.GET_PALEVEL, 0, 0, 1)
        struct.unpack('b', level)[0]

    def cmd_set_palevel(self, level=7):
        # set palevel (power amplifier level) where level 0-7
        # line 441 ubertooth_control.c
        self.device.ctrl_transfer(0x40, U1_USB.SET_PALEVEL, level, 0)

    def cmd_get_rev_num(self):
        # get revision number
        # line 518 ubertooth_control.c
        # result = device.ctrl_transfer(0xc0,33,0, 0,258)
        pass

    def cmd_get_compile_info(self):
        # get compile info
        # line 547 ubertooth_control.c
        # result = device.ctrl_transfer(0xc0,55,0, 0,256)
        pass

    def cmd_get_board_id(self):
        # get board id
        # line 570 ubertooth_control.c
        result = self.device.ctrl_transfer(0xc0, U1_USB.GET_BOARD_ID, 0, 0, 1)
        result = struct.unpack('b', result)[0]
        return result

    def cmd_set_squelch(self, level=0):
        # set squelch where level is ???
        # line 587 ubertooth_control.c
        self.device.ctrl_transfer(0x40, U1_USB.SET_SQUELCH, level, 0)

    def cmd_get_squelch(self):
        # get squelch where level is default 136
        # line 587 ubertooth_control.c
        level = self.device.ctrl_transfer(0xc0, U1_USB.GET_SQUELCH, 0, 0, 1)
        level = struct.unpack('B', level)[0]
        return level

    def cmd_read_register(self, reg):
        value = self.device.ctrl_transfer(0xc0, U1_USB.READ_REGISTER,
                                          reg & 0xFF, 0, 2)
        value = struct.unpack('>H', value)
        return value

    def cmd_write_register(self, reg, value=0):
        self.device.ctrl_transfer(0x40, U1_USB.WRITE_REGISTER,
                                  reg & 0xFF, value)

    def cmd_write_registers(self, registers):
        """
        registers is a dictionary of register:value pairs
        """
        count = len(registers)
        data = array.array("B", [0]*count*3)
        for i, reg in enumerate(registers):
            data[i*3] = reg & 0xFF
            data[(i*3)+1] = (registers[reg] >> 8) & 0xFF
            data[(i*3)+2] = registers[reg] & 0xFF
        self.device.ctrl_transfer(0x40, U1_USB.WRITE_REGISTERS, count, 0, data)

    def cmd_read_all_registers(self,):
        """
        Read all CC2400 registers in to a dictionary
        """
        MAX_REGISTER = 0x2d
        length = MAX_REGISTER*3
        data = self.device.ctrl_transfer(0xc0, U1_USB.READ_ALL_REGISTERS,
                                         0, 0, length)
        registers = dict(
            [(reg, (valh << 8) | vall)
             for reg, valh, vall in izip(*[iter(data)]*3)]
        )
        return registers
