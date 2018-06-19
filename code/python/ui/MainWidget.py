#!/usr/bin/python
# -*-coding:utf-8-*-
from PyQt5.QtGui import *
from PyQt5.QtCore import *

# 主入口文件
from PyQt5.QtWidgets import QDialog, QGroupBox, QLineEdit, QPushButton, QGridLayout, QLabel, QVBoxLayout, QHBoxLayout, \
    QApplication


class MainWidget(QDialog):
    def __init__(self, parent=None):
        super(MainWidget, self).__init__(parent)
        self.setMinimumSize(100, 100)
        self.setWindowFlags(Qt.CustomizeWindowHint|Qt.WindowCloseButtonHint)
        self.setWindowOpacity(0.9)

        # 添加头部group
        self.headDict = {}
        self.headPostArrayKey = 0
        self.HeadGroupBox = QGroupBox(u'动态添加控件数据')
        self.HeadGroupBox.setMinimumHeight(100)  #高度最小值
        self.HeadGroupBox.scroll(100,2)
        self.HeadAddParam = QPushButton(u'+')
        self.headDict[str(self.headPostArrayKey)+'_key'] = QLineEdit()
        self.headDict[str(self.headPostArrayKey)+'_value'] = QLineEdit()
        self.HeadGroupBoxLayout = QGridLayout()
        self.HeadGroupBoxLayout.addWidget(self.HeadAddParam, 0, 0)
        self.HeadGroupBoxLayout.addWidget(QLabel(u'Key：'), 1, 0)
        self.HeadGroupBoxLayout.addWidget(self.headDict[str(self.headPostArrayKey)+'_key'], 1, 1)
        self.HeadGroupBoxLayout.addWidget(QLabel(u'Value：'), 1, 2)
        self.HeadGroupBoxLayout.addWidget(self.headDict[str(self.headPostArrayKey)+'_value'], 1, 3)
        self.HeadGroupBox.setLayout(self.HeadGroupBoxLayout)
        self.HeadAddParam.clicked.connect(self.addHeadParam)


        # 提交按钮
        self.btnPost = QPushButton(u'提交')
        self.postbtnLoayout = QHBoxLayout()
        self.postbtnLoayout.addStretch()
        self.postbtnLoayout.addWidget(self.btnPost)
        # Main布局
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.HeadGroupBox)
        main_layout.addLayout(self.postbtnLoayout)  # addLayout 添加的是 Layout
        main_layout.setSpacing(0)
        self.setLayout(main_layout)

        # self.connect(self.btnPost, SIGNAL('clicked()'), self.postData)
        self.btnPost.clicked.connect(self.btnPost)


    def postData(self):
        self.headdictdata={}
        for k, v in self.headDict.items():
            temp=k.split('_')
            if temp[1]=='key':
                if self.headdictdata.has_key(temp[0]):
                    self.headdictdata[temp[0]]['key'] =str(v.text())
                else:
                    self.headdictdata[temp[0]] = {'key':str(v.text())}

            elif temp[1]=='value':
                if self.headdictdata.has_key(temp[0]):
                    self.headdictdata[temp[0]]['value'] =str(v.text())
                else:
                    self.headdictdata[temp[0]] = {'value':str(v.text())}

        print(self.headdictdata)

    # 添加头部Data
    def addHeadParam(self):
        sts=str(self.headPostArrayKey+1)
        self.headDict[sts+'_key'] = QLineEdit(sts+'name')
        self.headDict[sts+'_value'] = QLineEdit(sts+'chrome')

        self.HeadGroupBoxLayout.addWidget(QLabel(u'Key'))
        self.HeadGroupBoxLayout.addWidget(self.headDict[sts+'_key'])
        self.HeadGroupBoxLayout.addWidget(QLabel(u'Value'))
        self.HeadGroupBoxLayout.addWidget(self.headDict[sts+'_value'])
        self.headPostArrayKey+=1



if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    main_widget = MainWidget()
    main_widget.show()
    sys.exit(app.exec_())