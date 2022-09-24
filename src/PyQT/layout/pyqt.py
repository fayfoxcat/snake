import sys
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QApplication, QWidget

if __name__ == '__main__':
    app = QApplication(sys.argv)

    w = QWidget()

    w.setWindowTitle("pyqt布局演示")

    w.setWindowIcon(QIcon('snake.png'))

    w.show()

    app.exec_()
