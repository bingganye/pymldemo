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
from PyQt5.QtWidgets import QWidget, QPushButton, QApplication, QToolTip, QLabel, QLineEdit, QGridLayout
import pandas as pd
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *


class Example(QWidget):

    def __init__(self):
        super().__init__()

        self.initUI()

    def hitbtn(self):

        try:
            character2 = "++"
            character1 = "|"

            self.step = 0
            self.i = 0
            self.pbar.setValue(self.step)
            self.tipscontent.setText('正在匹配数据...')
            ENCODE = 'utf-8'

            self.step = self.step + 1
            self.pbar.setValue(self.step)

            patient_detail_data = pd.read_excel(self.patient_detail.text(), encoding=ENCODE)
            charge_data = pd.read_excel(self.charge.text(), encoding=ENCODE)
            charge_data['line'] = ''

            charge_data_count = len(charge_data)
            patient_detail_data_count = len(patient_detail_data)
            # print(charge_data_count)
            # print(patient_detail_data_count)
            # charge_data_count = 1600
            step_length = (patient_detail_data_count * 2 + charge_data_count) / 85

            self.step = self.step + 4
            self.pbar.setValue(self.step)

            def change_ProgressBar():
                self.i = self.i + 1
                # print(self.i)
                if self.i >= step_length:
                    # print("-------+++--",self.i)
                    self.step = self.step + 1
                    self.pbar.setValue(self.step)
                    self.i = 0

            def change_charge_str(data_row):
                change_ProgressBar()

                data_row = data_row.astype('str')
                line = data_row['f_dcmzid'] + character1 + data_row['f_fpny'] + character1 + data_row[
                    'f_total'] + character1 + data_row['number']

                return line

            # charge_data["line"] = charge_data.apply(lambda data_row: change_str(data_row))
            charge_data["line"] = charge_data.apply(lambda data_row: change_charge_str(data_row),
                                                    axis=1)  # axis=1表示对每一行做相同的操作

            charge_data.drop('f_dcmzid', axis=1, inplace=True)
            charge_data.drop('f_fpny', axis=1, inplace=True)
            charge_data.drop('f_total', axis=1, inplace=True)
            charge_data.drop('number', axis=1, inplace=True)

            setdict = {}
            for row in charge_data.index:
                change_ProgressBar()

                data_row = charge_data.loc[row]
                f_brmzid = str(data_row["f_brmzid"])
                line = data_row["line"]

                if f_brmzid in setdict:
                    svalue = setdict[f_brmzid]
                    svalue = svalue + character2 + line

                    setdict[f_brmzid] = svalue
                else:
                    setdict[f_brmzid] = line

            patient_detail_data['次数'] = ''
            patient_detail_data['费用'] = ''

            def change_patient_str(the_id):
                change_ProgressBar()

                the_id = str(the_id)
                if the_id in setdict:
                    svalue = setdict[the_id]
                    return svalue

            def change_str3(charge):
                change_ProgressBar()

                charge = str(charge)
                if charge.__contains__(character1):
                    return charge.count(character2) + 1

            patient_detail_data["费用"] = patient_detail_data['门诊号'].apply(lambda x: change_patient_str(x))
            patient_detail_data['次数'] = patient_detail_data['费用'].apply(lambda x, i=0: change_str3(x))

            try:
                path = self.patient_detail.text()
                rindex = path.rfind('/')
                path = str(path)[:rindex]
                path = path + '/合并表.xlsx'

            except Exception as e:
                print(e)
                self.tipscontent.setText(e)
                path = '合并表.xlsx'

            self.tipscontent.setText('正在生成合并表...')
            patient_detail_data.to_excel(path, index=False)

            self.step = 100
            self.pbar.setValue(self.step)
            self.tipscontent.setText('生成合并表成功')

        except Exception as e:
            print(e)
            self.tipscontent.setText("发生错误：" + str(e))

    def initUI(self):
        conmbinebtn = QPushButton('合并', self)
        conmbinebtn.clicked.connect(self.hitbtn)
        conmbinebtn.resize(conmbinebtn.sizeHint())
        # conmbinebtn.move(500, 50)
        QToolTip.setFont(QFont('SansSerif', 12))
        # self.setToolTip('This is a <b>QWidget</b> widget')
        self.setGeometry(300, 300, 650, 450)
        self.setWindowTitle('定制小合并')

        self.pbar = QProgressBar(self)
        self.step = 0

        self.tips = QLabel('提示')
        self.tipscontent = QLabel('')

        title = QLabel('病人详细表')
        author = QLabel('收费表')
        self.patient_detail = QLineEdit()
        self.charge = QLineEdit()
        grid = QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(title, 1, 0)
        grid.addWidget(self.patient_detail, 1, 1)
        grid.addWidget(author, 2, 0)
        grid.addWidget(self.charge, 2, 1)

        self.pushButton = QPushButton('打开', self)
        self.pushButton.setObjectName("pushButton")
        self.pushButton.clicked.connect(self.openfile)
        grid.addWidget(self.pushButton, 1, 2)

        self.pushButton2 = QPushButton('打开', self)
        self.pushButton2.setObjectName("pushButton")
        self.pushButton2.clicked.connect(self.openfile2)
        grid.addWidget(self.pushButton2, 2, 2)

        grid.addWidget(self.tips, 4, 0)
        grid.addWidget(self.tipscontent, 4, 1)
        grid.addWidget(conmbinebtn, 4, 2)
        grid.addWidget(self.pbar, 3, 1)
        self.setLayout(grid)
        self.show()

    def openfile(self):
        openfile_name = QFileDialog.getOpenFileName(self, '选择文件', '', 'Excel files(*.xlsx , *.xls)')
        add = openfile_name[0]
        self.patient_detail.setText(add)

    def openfile2(self):
        openfile_name = QFileDialog.getOpenFileName(self, '选择文件', '', 'Excel files(*.xlsx , *.xls)')
        add = openfile_name[0]
        self.charge.setText(add)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())

# pyinstaller -w custom_combine.py  --hidden-import=pandas._libs.tslibs.timedeltas


# try:
#     self.tipscontent.setText('正在匹配数据...')
#     ENCODE = 'utf-8'
#     patient_detail_data = pd.read_excel(self.patient_detail.text(), encoding=ENCODE)
#     charge_data = pd.read_excel(self.charge.text(), encoding=ENCODE)
#
#     # patient_detail_data.merge(charge_data, left_on='lkey', right_on='rkey', how='outer')
#     # result = pd.concat([patient_detail_data, charge_data], axis=1, join='right')
#     # result = pd.merge(patient_detail_data, charge_data,how='right',left_on=['门诊号'], right_on=['f_brmzid'])
#     result = pd.merge(patient_detail_data, charge_data,how='outer',left_on=['门诊号'], right_on=['f_brmzid'])
#
#     try:
#         path = self.patient_detail.text()
#         rindex = path.rfind('/')
#         path = str(path)[:rindex]
#         path = path + '/合并表2.xlsx'
#
#     except Exception as e:
#         print(e)
#         self.tipscontent.setText(e)
#         path = '合并表2.xlsx'
#
#     self.tipscontent.setText('正在生成合并表...')
#     result.to_excel(path)
#     self.tipscontent.setText('生成合并表成功')
# except Exception as e:
#     print(e)
#     self.tipscontent.setText("发生错误：" + str(e))
