from PyQt5 import QtCore, QtGui, QtWidgets
from RowSpanTableWidget import RowSpanTableWidget
from tableparser import Parser


from_cache = ''
while from_cache not in ('y', 'n'):
    from_cache = input('Load from cache? (y/n) ').lower()

print('loading data...')
if from_cache == 'y':
    print('loading from cache...')
    parser = Parser.from_cache()
else:
    print('loading from server...')
    parser = Parser.from_server()
    parser.save_cache()
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
        self.lineEdit.textChanged.connect(self.update_table)
        self.table = RowSpanTableWidget(3, self.centralwidget)
        self.table.setGeometry(QtCore.QRect(20, 80, 481, 481))
        self.table.setObjectName("table")
        self.table.horizontalHeader().setSectionResizeMode(
                QtWidgets.QHeaderView.Stretch)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 528, 20))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.helpButton = QtWidgets.QAction("Help")
        self.helpButton.setShortcut("Ctrl+H")
        self.helpButton.setStatusTip("Open help")
        self.helpButton.triggered.connect(self.open_help)
        self.fileMenu = self.menubar.addMenu("&Help")
        self.fileMenu.addAction(self.helpButton)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        self.update_table()

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow",
                                             "Problem Chooser v1.0"))
        self.label.setText(_translate("MainWindow",
                                      "Find easiest problems for you"))
        self.lineEdit.setPlaceholderText(_translate("MainWindow",
                                                    "Input your name here"))

    def update_table(self):
        name = self.lineEdit.text()
        names = parser.get_names()
        self.table.clear()
        good_names = []
        for el in names:
            if len(el) >= len(name) and el[:len(name)] == name:
                good_names.append(el)
                self.table.appendRow([3], el)
        if not good_names:
            for el in names:
                if name in el:
                    good_names.append(el)
                    self.table.appendRow([3], el)
        if len(good_names) == 1:
            name = good_names[0]
            stat = parser.get_stat(name)
            self.table.appendRow([1, 1, 1], ["Contest id", "Problem", "Score"])
            for el in stat:
                self.table.appendRow(
                        [1, 1, 1],
                        map(str, [el.contest.id, el.short_name, el.score])
                        )

    def open_help(self):
        QtWidgets.QMessageBox.about(self.centralwidget, "Help",
                                    "Текст-заглушка")


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
