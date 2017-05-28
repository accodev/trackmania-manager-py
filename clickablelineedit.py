#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PyQt5 import QtGui, QtWidgets, QtCore

class ClickableLineEdit(QtWidgets.QLineEdit):
    double_clicked = QtCore.pyqtSignal()
    def __init__(self, parent):
        super(ClickableLineEdit, self).__init__(parent)

    def mouseDoubleClickEvent(self, e):
        self.double_clicked.emit()
        e.accept()