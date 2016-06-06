#!/usr/bin/env python
"""Copyright 2016 Dominic Spill

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

from hardware.ubertooth import Ubertooth


class Radio(object):
    """
    A class to access radio settings using helper methods
    """
    ANY_DEVICE = 0
    UBERTOOTH = 1

    def __init__(self, radio_type=0):
        if radio_type == self.UBERTOOTH:
            self._dev = Ubertooth()
        if radio_type == self.ANY_DEVICE:
            try:
                self._dev = Ubertooth()
            except:
                raise Error("No devices found")

    def get_device(self):
        return self._dev

    def configure_radio(self, **kwargs):
        self._dev.configure_radio(**kwargs)

    def rx_pkts(self):
        try:
            for buf in self._dev.rx_stream():
                yield buf
        except KeyboardInterrupt:
            self._dev.close()
