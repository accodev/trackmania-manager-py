#!/usr/bin/python3
# -*- coding: utf-8 -*-
import view
import model
import util

class Controller():
    def __init__(self):
        self.view = view.TrackmaniaManagerMainWindow(self)
        self.model = model.MatchsettingsModel(self)
        # subscribe to updates - note: this is not thread-safe.
        self.update_subscribers = []
        self.update_subscribers.append(self.model)
        self.update_subscribers.append(self.view)
        # vars
        self._matchsettings = {}
        self._matchsettingspath = ''

    def start(self):
        self.view.show()

    @property
    def matchsettingspath(self):
        return self._matchsettingspath
    
    @matchsettingspath.setter
    @util.updater
    def matchsettingspath(self, value):
        if self._matchsettingspath is not value:
            self._matchsettingspath = value

    @property
    def matchsettings(self):
        return self._matchsettings

    @matchsettings.setter
    @util.updater
    def matchsettings(self, value):
        if self._matchsettings is not value:
            self._matchsettings = value