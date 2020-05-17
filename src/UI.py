import gzip
from os import path
import webbrowser
from PyQt5 import QtCore, QtWidgets, QtGui

import cfg
from src.MainPageParser import MainPageParser
from src.RowSpanTableWidget import RowSpanTableWidget
from src.TableParser import TableParser


def initParser(parserClass):
    name = parserClass.__name__
    # parserClass.delete_cache()
    if parserClass.is_cache_exists():
        try:
            print(f'Loading {name} from cache...')
            return parserClass.from_cache()
        except Exception as ex:
            print(ex)
    print(f'Loading {name} from server...')
    return parserClass.from_server()


tableParser = initParser(TableParser)
mainPageParser = initParser(MainPageParser)


class Ui_MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self.setupUi()

    def setupUi(self):
        self.setWindowTitle("Problem Chooser v" + cfg.VERSION)

        self.resize(600, 800)

        font = QtGui.QFont()
        font.setPixelSize(16)
        font.setStyleHint(QtGui.QFont.Monospace)
        self.setFont(font)

        self.centralwidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.centralwidget)

        self.headerLabel = QtWidgets.QLabel(self.centralwidget)
        self.headerLabel.setText("Find the easiest problems for you")

        self.reloadButton = QtWidgets.QPushButton("Reload")
        self.reloadButton.clicked.connect(self.reload_table)

        self.header = QtWidgets.QHBoxLayout()
        self.header.addWidget(self.headerLabel, stretch=5)
        self.header.addWidget(self.reloadButton, stretch=1)

        self.lineEdit = QtWidgets.QLineEdit()
        self.lineEdit.textChanged.connect(self.update_table)
        self.lineEdit.setPlaceholderText("Input your name here")

        self.table = RowSpanTableWidget(3)
        self.table.doubleClicked.connect(self.double_clicked)

        self.main_layout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.main_layout.addLayout(self.header)
        self.main_layout.addSpacing(10)
        self.main_layout.addWidget(self.lineEdit)
        self.main_layout.addWidget(self.table)

        self.menubar = QtWidgets.QMenuBar(self)
        self.setMenuBar(self.menubar)

        self.reloadSubmenu = QtWidgets.QAction("Reload (~5 sec)")
        self.reloadSubmenu.setShortcut("Ctrl+R")
        self.reloadSubmenu.triggered.connect(self.reload_table)

        self.tableMenu = self.menubar.addMenu("&Table")
        self.tableMenu.addAction(self.reloadSubmenu)

        self.helpSubmenu = QtWidgets.QAction("Help")
        self.helpSubmenu.setShortcut("Ctrl+H")
        self.helpSubmenu.triggered.connect(self.open_help)

        self.helpMenu = self.menubar.addMenu("&Help")
        self.helpMenu.addAction(self.helpSubmenu)

        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbarLabel = QtWidgets.QLabel()
        self.statusbar.addWidget(self.statusbarLabel)
        self.setStatusBar(self.statusbar)
        self.set_last_reload_time()

        self.update_table()

    def update_table(self):
        name = self.lineEdit.text().lower()
        names = tableParser.get_names()
        self.table.clear()
        good_names = []
        for el in names:
            if len(el) >= len(name) and el[:len(name)].lower() == name:
                good_names.append(el)
                self.table.appendRow([3], [el])
        if not good_names:
            for el in names:
                if name in el.lower():
                    good_names.append(el)
                    self.table.appendRow([3], [el])
        if len(good_names) == 1:
            name = good_names[0]
            stat = tableParser.get_stat(name)
            self.table.appendRow([1, 1, 1], ["Contest id", "Problem", "Score"])
            for el in stat:
                self.table.appendRow(
                    [1, 1, 1],
                    tuple(map(str, [el.contest_id, el.short_name, el.score]))
                )
        elif len(good_names) == 0:
            self.table.appendRow([3], ['NOT FOUND'])
            self.table.item(0, 0).setTextAlignment(QtCore.Qt.AlignHCenter)

    def open_help(self):
        location = cfg.resource('help')
        with open(location, 'r') as f:
            text = f.read()
        QtWidgets.QMessageBox.about(self.centralwidget, "Help", text)

    def set_last_reload_time(self):
        self.statusbarLabel.setText(self.get_last_reload_time())

    def get_last_reload_time(self):
        if tableParser.last_reload_time is None:
            return " Last reload: undefined"
        else:
            strtime = tableParser.last_reload_time.strftime('%x %X')
            return " Last reload: " + strtime

    def on_reload_finished(self):
        self.statusbarLabel.setText(self.get_last_reload_time())
        self.set_last_reload_time()
        self.update_table()

    def reload_table(self):
        if tableParser.isReloading():
            print('Already reloading')
            return
        self.statusbarLabel.setText(" Reloading...")
        tableParser.reload(self.on_reload_finished)
        mainPageParser.reload()

    def double_clicked(self):
        item = self.table.currentItem()
        if item.text() in tableParser.get_names():
            self.lineEdit.setText(item.text())
            return
        cells = [self.table.item(item.row(), col) for col in range(3)]
        if item.column() == 0:
            url = mainPageParser.get_contest_url_by_id(cells[0].text())
            if url is not None:
                webbrowser.open(url)
        elif item.column() == 1:
            url = mainPageParser.get_statements_url_by_id(cells[0].text())
            if url is not None:
                url += "#prob_" + item.text()
                webbrowser.open(url)
        elif item.column() == 2:
            url = mainPageParser.get_results_url_by_id(cells[0].text())
            if url is not None:
                webbrowser.open(url)
