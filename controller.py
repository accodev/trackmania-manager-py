#!/usr/bin/python3
# -*- coding: utf-8 -*-
import view
import model

class Controller():
    def __init__(self):
        self.view = view.TrackmaniaManagerMainWindow(self)
        self.model = model.MatchsettingsModel(self)
        # initialize properties
        self._matchsettings = {}
        self._matchsettingspath = ''

    def start(self):
        self.view.show()

    @property
    def matchsettingspath(self):
        return self._matchsettingspath
    
    @matchsettingspath.setter
    def matchsettingspath(self, value):
        if self._matchsettingspath is not value:
            self._matchsettingspath = value

            try:
                self.model.matchsettingspath_updated()
            except AttributeError as e:
                print(e)
            try:
                self.view.matchsettingspath_updated()
            except AttributeError as e:
                print(e)

    @property
    def matchsettings(self):
        return self._matchsettings

    @matchsettings.setter
    def matchsettings(self, value):
        if self._matchsettings is not value:
            self._matchsettings = value

            try:
                self.model.matchsettings_updated()
            except AttributeError as e:
                print(e)
            try:
                self.view.matchsettings_updated()
            except AttributeError as e:
                print(e)