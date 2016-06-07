#!/usr/bin/env python
"""
Copyright 2016 Dominic Spill, Michael Ossmann

This file is part of Sturdy Palm Tree.

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

from SturdyPalmTree.radio import Radio
from bitstring import BitStream

# input: whitened packet bits, starting with sync word
# output: whitened CRC
def cx10a_crc(packet):
    crc = 0xb5d2
    # compute CRC over sync word and all data fields
    for byte in packet.cut(8, 0, 192):
        crc ^= byte.unpack('uint:8')[0] << 8
        for j in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc = crc << 1
        crc &= 0xffff
    crc ^= 0x61B1
    return crc

def decode_cx10a(packet):
    # u1-u4 are unknown fields
    sync, mode, cid, vid, roll, u1, pitch, u2, throttle, u3, yaw, \
    u4, special, crc, trailer = packet.unpack('uint:40, uint:8, '
        'uint:32, uint:32, uint:12, uint:4, uint:12, uint:4, uint:12, uint:4, '
        'uint:12, uint:4, uint:16, uint:16, uint:8')

    # unwhiten and reverse bits
    mode = int('{:08b}'.format(mode ^ 0xbc)[::-1], 2)
    cid = int('{:032b}'.format(cid ^ 0xe5660dae)[::-1], 2)
    vid = int('{:032b}'.format(vid ^ 0x8c881269)[::-1], 2)
    roll = int('{:012b}'.format(roll ^ 0xee1)[::-1], 2)
    u1 = int('{:04b}'.format(u1 ^ 0xf)[::-1], 2)
    pitch = int('{:012b}'.format(pitch ^ 0xc76)[::-1], 2)
    u2 = int('{:04b}'.format(u2 ^ 0x2)[::-1], 2)
    throttle = int('{:012b}'.format(throttle ^ 0x97d)[::-1], 2)
    u3 = int('{:04b}'.format(u3 ^ 0x5)[::-1], 2)
    yaw = int('{:012b}'.format(yaw ^ 0x0b7)[::-1], 2)
    u4 = int('{:04b}'.format(u4 ^ 0x9)[::-1], 2)
    special = int('{:016b}'.format(special ^ 0xcacc)[::-1], 2)

    if crc == cx10a_crc(packet):
        print "%02x %08x %08x %4d %01x %4d %01x %4d %01x %4d %01x %04x %04x" \
            % (mode, cid, vid, roll, u1, pitch, u2, throttle, u3, yaw, u4,
               special, crc)

def find_cx10a_packet(symbols):
    # search for whitened sync word
    if symbols.find('0x2f7d872649', 0, symbols.len - 216):
        decode_cx10a(symbols[symbols.pos:symbols.pos + 216])
        return symbols[symbols.pos + 216:]
    else:
        return symbols[symbols.len - 216:]

def ubertooth_rx():
    dev = Radio(Radio.UBERTOOTH)
    syncword = 0x2f7d8726
    dev.configure_radio(frequency=2402, freq_deviation=340, syncword=syncword)
    print dev._dev.cmd_get_modulation()
    #raise
    symbol_stream = BitStream()
    for metadata, pkt in dev.rx_pkts():
        #print metadata
        #print pkt.bin
        symbol_stream.append(pkt)
        symbol_stream = find_cx10a_packet(symbol_stream)

if __name__ == "__main__":
    ubertooth_rx()
