#!/usr/bin/python3
# -*- coding: utf-8 -*-
import view
import model

class Controller():
    def __init__(self):
        self.view = view.TrackmaniaManagerMainWindow(self)
        self.model = model.MatchsettingsModel(self)

    def start(self):
        self.view.show()

    @property
    def matchsettings_file(self):
        return self._matchsettings_file
    
    @matchsettings_file.setter
    def matchsettings_file(self, value):
        self._matchsettings_file = value
        if self._matchsettings_file:
            self.model.parse()