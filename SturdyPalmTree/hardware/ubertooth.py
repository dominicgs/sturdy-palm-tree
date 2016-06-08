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
from itertools import izip
from bitstring import BitArray


class U1_USB(object):
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


class U1_MOD(object):
    MOD_BT_BASIC_RATE = 0
    MOD_BT_LOW_ENERGY = 1
    MOD_80211_FHSS    = 2
    MOD_NONE          = 3


class Ubertooth(object):
    min_freq = 2400
    max_freq = 2483

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
        self.device.ctrl_transfer(0x40, U1_USB.RX_SYMBOLS, 0, 0)

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
        start = time.time()
        while count is None or count > 0:
            buffer = self.device.read(0x82, 64)
            if count is not None:
                count -= 1
            if secs is not None:
                if time.time() >= start+secs:
                    break
            if buffer:
                pkt = BitArray(bytes=buffer)
                metadata = pkt.unpack('uint:8, uint:8, uint:8, uint:8, uint:32,'
                                      'int:8, int:8, int:8, uint:8')
                metanames = ('pkt_type', 'status', 'channel', 'clkn_high',
                             'clk100ns', 'rssi_max', 'rssi_min', 'rss_avg',
                             'rssi_count')
                yield dict(zip(metanames, metadata)), pkt[112:]

    def close(self):
        self.device.ctrl_transfer(0x40, U1_USB.STOP)
        self.device.ctrl_transfer(0x40, U1_USB.RESET)

    # Start new stuff 4/27/16
    def cmd_trim_clock(self):
        # trim clock
        # THIS IS AN UBERTOOTH ASYNC COMMAND
        pass

    def cmd_ping(self):
        # cmd ping
        result = self.device.ctrl_transfer(0xc0, U1_USB.PING, 0, 0, 0)
        return result

    def cmd_rx_syms(self):
        # already implemented above
        # set rx mode
        self.device.ctrl_transfer(0x40, U1_USB.RX_SYMBOLS, 0, 0)

    def cmd_specan(self, low_freq=2402, high_freq=2480):
        # specan where low_freq & high_freq is 2402-2480
        self.device.ctrl_transfer(0x40, U1_USB.SPECAN, low_freq, high_freq)

    def cmd_simple_get(self, cmd):
        # get usrled where state is 0-1
        state = self.device.ctrl_transfer(0xc0, cmd, 0, 0, 1)
        state = struct.unpack('b', state)[0]
        return state

    def cmd_set_usrled(self, state=0):
        # set usrled where state is 0-1
        self.device.ctrl_transfer(0x40, U1_USB.SET_USRLED, state, 0)

    def cmd_get_usrled(self):
        # get usrled where state is 0-1
        return self.cmd_simple_get(U1_USB.GET_USRLED)

    def cmd_set_rxled(self, state=0):
        # set rxled where state is 0-1
        self.device.ctrl_transfer(0x40, U1_USB.SET_RXLED, state, 0)

    def cmd_get_rxled(self):
        # get rxled where state is 0-1
        return self.cmd_simple_get(U1_USB.GET_RXLED)

    def cmd_set_txled(self, state=0):
        # set txled where state is 0-1
        # line 181 ubertooth_control.c
        self.device.ctrl_transfer(0x40, U1_USB.SET_TXLED, state, 0)

    def cmd_get_txled(self):
        # get txled where state is 0-1
        return self.cmd_simple_get(U1_USB.GET_TXLED)

    def cmd_set_1v8(self, state=0):
        # set txled where state is 0-1
        self.device.ctrl_transfer(0x40, U1_USB.SET_1V8, state, 0)

    def cmd_get_1v8(self):
        # get 1v8 where state is 0-1
        return self.cmd_simple_get(U1_USB.GET_1V8)

    def cmd_set_channel(self, channel=0):
        # set txled where state is 0-1
        self.device.ctrl_transfer(0x40, U1_USB.SET_CHANNEL, channel, 0)

    def cmd_get_channel(self):
        # get txled where state is 0-1
        channel = self.device.ctrl_transfer(0xc0, U1_USB.GET_CHANNEL, 0, 0, 2)
        state = struct.unpack('<H', channel)[0]
        return channel

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
        self.device.ctrl_transfer(0x40, U1_USB.SET_ISP, 0, 0)

    def cmd_reset(self):
        # reset ubertooth
        self.device.ctrl_transfer(0x40, U1_USB.RESET, 0, 0)

    def cmd_stop(self):
        # stop ubertooth
        self.device.ctrl_transfer(0x40, U1_USB.STOP, 0, 0)

    def cmd_set_paen(self, state=1):
        self.device.ctrl_transfer(0x40, U1_USB.SET_PAEN, state, 0)

    def cmd_get_paen(self):
        return self.cmd_simple_get(U1_USB.GET_PAEN)

    def cmd_set_hgm(self, state=-1):
        self.device.ctrl_transfer(0x40, U1_USB.SET_HGM, state, 0)

    def cmd_get_hgm(self):
        return self.cmd_simple_get(U1_USB.GET_HGM)

    def cmd_set_modulation(self, modulation=U1_MOD.MOD_NONE):
        self.device.ctrl_transfer(0x40, U1_USB.SET_MOD, modulation, 0)

    def cmd_get_modulation(self):
        return self.cmd_simple_get(U1_USB.GET_MOD)

    def cmd_flash(self):
        # flash mode
        # line 413 ubertooth_control.c
        self.device.ctrl_transfer(0x40, U1_USB.FLASH, 0, 0)

    def cmd_get_palevel(self):
        # get palevel (power amplifier level)
        # line 427 ubertooth_control.c
        level = self.device.ctrl_transfer(0xc0, U1_USB.GET_PALEVEL, 0, 0, 1)
        return struct.unpack('b', level)[0]

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

    def cmd_read_all_registers(self):
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

    def get_freq_range(self):
        return (self.min_freq, self.max_freq)

    def configure_radio(self, frequency, freq_deviation=None,
                        syncword=None):
        registers = {}
        min_freq, max_freq = self.get_freq_range()
        if frequency < min_freq or frequency > max_freq:
            raise Error("Frequency (%d) is not within supported range (%d-%d)"
                        % (frequency, min_freq, max_freq))
        registers[Registers.FSDIV] = frequency - 1
        registers[Registers.LMTST] = 0x2b22
        registers[Registers.MANAND] = 0x7fff
        registers[Registers.MDMTST0] = 0x124b
        """
        1      2      4b
        00 0 1 0 0 10 01001011
           | | | | |  +---------> AFC_DELTA = ??
           | | | | +------------> AFC settling = 4 pairs (8 bit preamble)
           | | | +--------------> no AFC adjust on packet
           | | +----------------> do not invert data
           | +------------------> TX IF freq 1 0Hz
           +--------------------> PRNG off

        ref: CC2400 datasheet page 67
        AFC settling explained page 41/42
        """
        if freq_deviation:
            mod_dev = int(round(freq_deviation / 3.9062))
            registers[Registers.MDMCTRL] = mod_dev & 0x3f

        if syncword:
            registers[Registers.SYNCL] = syncword & 0xffff
            registers[Registers.SYNCH] = (syncword >> 16) & 0xffff

        # TODO allow these to be set
        registers[Registers.GRMDM] = 0x0461
        """
        0 00 00 1 000 11 0 00 0 1
          |  |  | |   |  |    |---> Modulation: FSK
          |  |  | |   |  +--------> CRC off
          |  |  | |   +-----------> sync word: 32 MSB bits of SYNC_WORD
          |  |  | +---------------> 0 preamble bytes of 01010101
          |  |  +-----------------> packet mode
          |  +--------------------> un-buffered mode
          +-----------------------> sync error bits: 0
        """

        self.cmd_set_channel(frequency)
        self.cmd_set_modulation(U1_MOD.MOD_NONE)
        self.cmd_write_registers(registers)
