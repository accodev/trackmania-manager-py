#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import view
from PyQt5 import QtWidgets


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    tmmw = view.TrackmaniaManagerMainWindow()
    tmmw.show()
    sys.exit(app.exec_())