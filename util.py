#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PyQt5 import QtCore
import logging

AUTHOR = 'Marco Accorinti'
APP_NAME = 'trackmania-manager'

# requires self.update_subscribers to be defined
def updater(func):
    def _updater(self, *args, **kwargs):
        func(self, *args, **kwargs)
        for subscriber in self.update_subscribers:
            try:
                update_func = getattr(subscriber, '{}_updated'.format(func.__name__))
                update_func()
            except AttributeError as e:
                print(e)

    return _updater


def qt_msg_type_to_logging_level(t):
    if t is QtCore.QtDebugMsg:
        level = logging.DEBUG
    elif t is QtCore.QtWarningMsg:
        level = logging.WARNING
    elif t in (QtCore.QtSystemMsg, QtCore.QtInfoMsg):
        level = logging.INFO
    elif t is QtCore.QtFatalMsg:
        level = logging.FATAL
    elif t is QtCore.QtCriticalMsg:
        level = logging.CRITICAL
    else:
        level = logging.DEBUG
    return level
