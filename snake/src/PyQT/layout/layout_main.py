import sys

from PyQt5 import *
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication

if __name__ == '__main__':

    app = QApplication(sys.argv)
    ui = uic.loadUi("public/mywindows.ui")
    ui.show()

    app.exec()
