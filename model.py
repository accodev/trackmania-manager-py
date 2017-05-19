#!/usr/bin/python3
# -*- coding: utf-8 -*-

import controller
from lxml import etree

class MatchsettingsModel():
    def __init__(self, c):
        self._c = c

    def parse(self):
        with open(self._c.matchsettings_file) as f:
            tree = etree.parse(f)