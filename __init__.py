#!/usr/bin/python3
# -*- coding: utf-8 -*-

import io
import os
import logging
import sys
import view
from PyQt5 import QtWidgets


if __name__ == '__main__':
    try:
        if os.name != 'nt':
            sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
        logging.basicConfig(handlers=[logging.StreamHandler(sys.stdout)],
                            level=logging.DEBUG,
                            format='%(asctime)-15s|%(levelname)-8s|'
                                   '%(process)d|%(name)s|%(module)s|%(lineno)d|%(message)s')
    except (io.UnsupportedOperation, AttributeError) as e:
        print(e)
    logging.info('start')
    app = QtWidgets.QApplication(sys.argv)
    tmmw = view.TrackmaniaManagerMainWindow()
    tmmw.show()
    sys.exit(app.exec_())
    logging.info('stop')