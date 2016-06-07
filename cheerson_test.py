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
import bitstring

whitening = bitstring.Bits('0xe3b14bea85bce5660dae8c881269ee1fc76297d50b79cacc1b5d19')

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
    unwhitened = packet ^ whitening

    mode = unwhitened[47:39:-1].read('uint:8')
    cid = unwhitened[79:47:-1].read('uint:32')
    vid = unwhitened[111:79:-1].read('uint:32')
    roll = unwhitened[127:111:-1].read('uint:16')
    pitch = unwhitened[143:127:-1].read('uint:16')
    throttle = unwhitened[159:143:-1].read('uint:16')
    yaw = unwhitened[171:159:-1].read('uint:12')
    flip = unwhitened[175:171:-1].read('uint:4')
    special = unwhitened[191:175:-1].read('uint:16')
    crc = packet[192:208].read('uint:16')

    if crc == cx10a_crc(packet):
        print "%02x %08x %08x %5d %5d %5d %5d %01x %04x %04x" \
            % (mode, cid, vid, roll, pitch, throttle, yaw, flip, special, crc)

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
    symbol_stream = bitstring.ConstBitStream()
    for metadata, pkt in dev.rx_pkts():
        #print metadata
        #print pkt.bin
        symbol_stream += pkt
        symbol_stream = find_cx10a_packet(symbol_stream)

if __name__ == "__main__":
    ubertooth_rx()
