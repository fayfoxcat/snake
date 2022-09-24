#conding=utf-8
'''
Pyqt5 文件对话框实例
'''
from PyQt5.QtWidgets import QWidget, QApplication, QPushButton, QColorDialog, QFontDialog, QTextEdit, QFileDialog
import sys

class Example(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):

        self.setGeometry(300, 300, 500, 300)
        self.setWindowTitle('文件对话框实例')


        self.tx = QTextEdit(self)
        self.tx.setGeometry(20, 20, 300, 270)


        self.bt1 = QPushButton('选择字体',self)
        self.bt1.move(350,20)
        self.bt2 = QPushButton('选择颜色',self)
        self.bt2.move(350,70)
        self.bt3 = QPushButton('打开文件',self)
        self.bt3.move(350,120)
        self.bt4 = QPushButton('选择目录',self)
        self.bt4.move(350,170)
        self.bt5 = QPushButton('保存文件',self)
        self.bt5.move(350,220)

        self.bt1.clicked.connect(self.choiceFont)
        self.bt2.clicked.connect(self.choiceColor)
        self.bt3.clicked.connect(self.openFile)
        self.bt4.clicked.connect(self.selectPath)
        self.bt5.clicked.connect(self.saveToFile)

        self.show()

    def openFile(self):
        fname = QFileDialog.getOpenFileName(self, '打开文件','./')
        if fname[0]:
            with open(fname[0], 'r',encoding='gb18030',errors='ignore') as f:
                self.tx.setText(f.read())

    def selectPath(self):
        path = QFileDialog.getExistingDirectory(self, '请选择保存目录', './')
        if path[0]:
            self.tx.setText('选择的目录为：{}'.format(path))

    def saveToFile(self):
        path = QFileDialog.getSaveFileName(self, '请选择保存位置', './',"Files (*.{});;All Files (*)".format('txt'))
        if path[0]:
            self.tx.setText('选择的保存位置为：{}'.format(path[0]))

    def choiceFont(self):
        font, ok = QFontDialog.getFont()
        if ok:
            self.tx.setCurrentFont(font)

    def choiceColor(self):
        col = QColorDialog.getColor()

        if col.isValid():
            self.tx.setStyleSheet("QTextEdit{{color:{};}}".format(str(col.name())))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())