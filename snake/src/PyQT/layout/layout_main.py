import sys
from PyQt5 import *
from PyQt5 import uic
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication

from src.PyQT.layout.layout_QHBoxLayout_垂直盒子布局 import MyWindow
from src.PyQT.layout.public.test import Ui_MainWindow

if __name__ == '__main__':

    app = QApplication(sys.argv)
    ui = uic.loadUi("public/mywindows.ui")
    ui.show()

    app.exec()
