#!/usr/bin/python3
# -*- coding: utf-8 -*-

import controller
from lxml import etree

class MatchsettingsModel():
    def __init__(self, c):
        self._c = c
        self._f = None
        self._matchsettings = {}
        self._tree = None

    def matchsettings_updated(self):
        common_keys = set(self._c.matchsettings).intersection(self._matchsettings)
        modified = {k: (self._c.matchsettings[k], self._matchsettings[k])
                    for k in common_keys if self._c.matchsettings[k] != self._matchsettings[k]}
        if len(modified) > 0:
            self._matchsettings = self._c.matchsettings
            self._save()

    def matchsettingspath_updated(self):
        if self._c.matchsettingspath is not '':
            if self._f:
                self._f.close()
            self._parse()
        else:
            self._c.matchsettings = {}
            self._f.close()

    def _parse(self):
        self._f = open(self._c.matchsettingspath, 'r+')
        self._tree = etree.parse(self._f)
        self.__parse_challenge(self._tree, '/playlist//challenge')
        self.__parse_challenge(self._tree, '/playlist//comment()', commented=True)
        self._c.matchsettings = self._matchsettings

    def __parse_challenge(self, tree, query, commented=False):
        assert 'challenge' or 'comment()' in query
        for e in tree.xpath(query):
            if commented:
                e = etree.fromstring(e.text.replace('<!--', '').replace('-->', ''))
            for c in list(e):
                if c.tag == 'file':
                    self._matchsettings[c.text] = not commented

    def _save(self):
        for e in self._tree.xpath('/playlist//challenge'):
            e.getparent().remove(e)
        for e in self._tree.xpath('/playlist//comment()'):
            e.getparent().remove(e)

        playlist = self._tree.xpath('/playlist')

        for k, v in self._matchsettings.items():
            challenge = etree.Element('challenge')
            file = etree.Element('file')
            file.text = k
            challenge.append(file)
            if v: # enabled challenge
                playlist.append(challenge)
            else: # disabled challenge
                commented_challenge = etree.Comment('<!-- {} -->'.format(etree.tostring(challenge)))
                playlist.append(commented_challenge)

        xml = etree.tostring(self._tree, pretty_print=True, xml_declaration=True)





