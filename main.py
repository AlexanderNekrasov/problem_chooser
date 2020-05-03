from PyQt5 import QtCore, QtGui, QtWidgets
from tableparser import Parser


print('loading data...')
parser = Parser()
print('loaded')


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(528, 604)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(20, 10, 461, 20))
        self.label.setMinimumSize(QtCore.QSize(57, 0))
        self.label.setObjectName("label")
        self.lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit.setGeometry(QtCore.QRect(20, 40, 481, 23))
        self.lineEdit.setInputMask("")
        self.lineEdit.setObjectName("lineEdit")
        self.lineEdit.textChanged.connect(self.update_list)
        self.listView = QtWidgets.QListView(self.centralwidget)
        self.listView.setGeometry(QtCore.QRect(20, 80, 481, 481))
        self.listView.setObjectName("listView")
        self.listView.setEditTriggers(
                QtWidgets.QAbstractItemView.NoEditTriggers
                )
        self.listViewModel = QtGui.QStandardItemModel()
        self.listView.setModel(self.listViewModel)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 528, 20))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        self.update_list()

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label.setText(_translate("MainWindow",
                                      "Find easiest problems for you"))
        self.lineEdit.setPlaceholderText(_translate("MainWindow",
                                                    "Input your name here"))

    def update_list(self):
        name = self.lineEdit.text()
        names = parser.get_names()
        self.listViewModel.clear()
        good_names = []
        for el in names:
            if len(el) >= len(name) and el[:len(name)] == name:
                good_names.append(el)
                row = QtGui.QStandardItem()
                row.setText(el)
                self.listViewModel.appendRow(row)
        if not good_names:
            for el in names:
                if name in el:
                    good_names.append(el)
                    row = QtGui.QStandardItem()
                    row.setText(el)
                    self.listViewModel.appendRow(row)
        if len(good_names) == 1:
            name = good_names[0]
            stat = parser.get_stat(name)
            head_row = QtGui.QStandardItem()
            head_row.setChild(0, 0, QtGui.QStandardItem("Contest id"))
            head_row.setChild(1, 0, QtGui.QStandardItem("Problem"))
            self.listViewModel.appendRow(head_row)
            head_row = QtGui.QStandardItem(
                    "{:<15} {:<15} {:<15}".format("Contest id",
                                                  "Problem", "Score"))
            self.listViewModel.appendRow(head_row)
            for el in stat:
                row = QtGui.QStandardItem(
                        "{:<15} {:<15} {:<15}".format(el.contest.id,
                                                      el.short_name, el.score))
                self.listViewModel.appendRow(row)


if __name__ == "__main__":
    import sys

    font = QtGui.QFont()
    font.setPixelSize(16)
    font.setStyleHint(QtGui.QFont.Monospace)
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    MainWindow.setFont(font)
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
