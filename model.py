#!/usr/bin/python3
# -*- coding: utf-8 -*-

import controller
from lxml import etree

class MatchsettingsModel():
    def __init__(self, c):
        self._c = c
        self._f = None
        self._matchsettings = {}

    def matchsettingspath_updated(self):
        if self._c.matchsettingspath is not '':
            if self._f:
                self._f.close()
            self._parse()
        else:
            self._c.matchsettings = {}

    def _parse(self):
        self._f = open(self._c.matchsettingspath, 'r+')
        tree = etree.parse(self._f)
        self.__parse_challenge(tree, '/playlist//challenge')
        self.__parse_challenge(tree, '/playlist//comment()', commented=True)
        self._c.matchsettings = self._matchsettings

    def __parse_challenge(self, tree, query, commented=False):
        assert 'challenge' or 'comment()' in query
        for e in tree.xpath(query):
            if commented:
                e = etree.fromstring(e.text.replace('<!--', '').replace('-->', ''))
            for c in list(e):
                if c.tag == 'file':
                    self._matchsettings[c.text] = not commented

