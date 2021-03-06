#!/usr/bin/env python
"""
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

from enum import IntEnum


class Registers(IntEnum):
    MAIN = 0x00
    FSCTRL = 0x01
    FSDIV = 0x02
    MDMCTRL = 0x03
    AGCCTRL = 0x04
    FREND = 0x05
    RSSI = 0x06
    FREQUEST = 0x07
    IOCFG = 0x08
    FSMTC = 0x0b
    RESERVED = 0x0c
    MANAND = 0x0d
    FSMSTATE = 0x0e
    ADCTST = 0x0f
    RXBPFTST = 0x10
    PAMTST = 0x11
    LMTST = 0x12
    MANOR = 0x13
    MDMTST0 = 0x14
    MDMTST0 = 0x15
    DACTST = 0x16
    AGCTST0 = 0x17
    AGCTST1 = 0x18
    AGCTST2 = 0x19
    FSTST0 = 0x1a
    FSTST1 = 0x1b
    FSTST2 = 0x1c
    FSTST3 = 0x1d
    MANFIDL = 0x1e
    MANFIDH = 0x1f
    GRMDM = 0x20
    GRDEC = 0x21
    PKTSTATUS = 0x22
    INT = 0x23
    R24 = 0x24
    R25 = 0x25
    R26 = 0x26
    R27 = 0x27
    R28 = 0x28
    R29 = 0x29
    R2A = 0x2a
    R2B = 0x2b
    SYNCL = 0x2c
    SYNCH = 0x2d
    SXOSCON = 0x60
    SFSON = 0x61
    SRX = 0x62
    STX = 0x63
    SRFOFF = 0x64
    SXOSCOFF = 0x65
    R66 = 0x66
    R67 = 0x67
    R68 = 0x68
    R69 = 0x69
    R6A = 0x6a
    R6B = 0x6b
    R6C = 0x6c
    R6D = 0x6d
    R6E = 0x6e
    R6F = 0x6f
    FIFOREG = 0x70
