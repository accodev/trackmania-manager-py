import sys
import controller

from PyQt5 import QtWidgets


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    c = controller.Controller()
    c.start()
    sys.exit(app.exec_())