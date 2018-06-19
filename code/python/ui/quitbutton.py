#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
ZetCode PyQt5 tutorial

This program creates a quit
button. When we press the button,
the application terminates.

Author: Jan Bodnar
Website: zetcode.com
Last edited: January 2018
"""

import sys

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QPushButton, QApplication, QToolTip


class Example(QWidget):

    def __init__(self):
        super().__init__()

        self.initUI()

    def hibtn(self):
        print('hibtn')


    def initUI(self):
        qbtn = QPushButton('Quit', self)
        # qbtn.clicked.connect(QApplication.instance().quit)
        qbtn.clicked.connect(self.hibtn)
        qbtn.resize(qbtn.sizeHint())
        qbtn.move(50, 50)

        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('Quit button')
        # self.show()

        QToolTip.setFont(QFont('SansSerif', 10))

        self.setToolTip('This is a <b>QWidget</b> widget')

        btn = QPushButton('Button', self)
        btn.setToolTip('This is a <b>QPushButton</b> widget')
        # btn.clicked.connect(hibtn)
        btn.resize(btn.sizeHint())
        btn.move(150, 150)

        self.setGeometry(300, 300, 300, 200)
        self.setWindowTitle('Tooltips')
        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())