#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
ZetCode PyQt5 tutorial

In this example, we create a simple
window in PyQt5.

Author: Jan Bodnar
Website: zetcode.com
Last edited: August 2017
"""

import sys

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QWidget, QToolTip, QPushButton
import pandas as pd


class Example(QWidget):

    def __init__(self):
        super().__init__()

        self.initUI()

    def hitbtn(self):
        print('hibtn')
        a = pd.DataFrame()

        print('hibtn2')

    def initUI(self):
        conmbinebtn = QPushButton('合并', self)
        conmbinebtn.clicked.connect(self.hitbtn)
        conmbinebtn.resize(conmbinebtn.sizeHint())
        conmbinebtn.move(500, 50)
        QToolTip.setFont(QFont('SansSerif', 12))
        self.setToolTip('This is a <b>QWidget</b> widget')
        self.setGeometry(300, 300, 650, 450)
        self.setWindowTitle('定制小合并')
        self.show()

if __name__ == '__main__':
    # app = QApplication(sys.argv)
    #
    # w = QWidget()
    # w.resize(250, 150)
    # w.move(300, 300)
    # w.setWindowTitle('小程序')
    # w.show()

    ex = Example()
    # a = pd.DataFrame()

    # sys.exit(app.exec_())