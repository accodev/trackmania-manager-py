#!/usr/bin/python3
# -*- coding: utf-8 -*-

import controller
from lxml import etree

class MatchsettingsModel():
    def __init__(self, c):
        self._c = c

    def matchsettingspath_updated(self):
        self._parse()

    def _parse(self):
        with open(self._c.matchsettingspath) as f:
            tree = etree.parse(f)
            for challenge in tree.xpath('/playlist//challenge'):
                print(challenge)
