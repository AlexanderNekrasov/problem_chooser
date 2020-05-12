from PyQt5 import QtCore, QtWidgets
from RowSpanTableWidget import RowSpanTableWidget
from Parser import Parser
from Worker import Worker


parser = Parser()


def reload_table():
    global parser
    parser = Parser.from_server()
    parser.save_cache()


class Ui_MainWindow:

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(600, 800)

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.label = QtWidgets.QLabel(self.centralwidget)

        self.reloadButton = QtWidgets.QPushButton("Reload")
        self.reloadButton.clicked.connect(self.reload_table)

        self.header = QtWidgets.QHBoxLayout()
        self.header.addWidget(self.label, stretch=1)
        self.header.addWidget(self.reloadButton)

        self.lineEdit = QtWidgets.QLineEdit()
        self.lineEdit.textChanged.connect(self.update_table)

        self.table = RowSpanTableWidget(3)
        self.table.doubleClicked.connect(self.select_name)

        self.main_layout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.main_layout.addLayout(self.header)
        self.main_layout.addWidget(self.lineEdit)
        self.main_layout.addWidget(self.table)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        MainWindow.setMenuBar(self.menubar)

        self.reloadButton = QtWidgets.QAction("Reload (~5 sec)")
        self.reloadButton.setShortcut("Ctrl+R")
        self.reloadButton.triggered.connect(self.reload_table)

        self.tableMenu = self.menubar.addMenu("&Table")
        self.tableMenu.addAction(self.reloadButton)

        self.helpButton = QtWidgets.QAction("Help")
        self.helpButton.setShortcut("Ctrl+H")
        self.helpButton.triggered.connect(self.open_help)

        self.fileMenu = self.menubar.addMenu("&Help")
        self.fileMenu.addAction(self.helpButton)

        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        MainWindow.setStatusBar(self.statusbar)
        self.retranslateUi(MainWindow)
        self.threadPool = QtCore.QThreadPool()
        self.reloading = False
        self.set_last_reload_time()
        self.update_table()

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow",
                                             "Problem Chooser v1.79"))
        self.label.setText(_translate("MainWindow",
                                      "Find easiest problems for you"))
        self.lineEdit.setPlaceholderText(_translate("MainWindow",
                                                    "Input your name here"))

    def update_table(self):
        name = self.lineEdit.text().lower()
        names = parser.get_names()
        self.table.clear()
        good_names = []
        for el in names:
            if len(el) >= len(name) and el[:len(name)].lower() == name:
                good_names.append(el)
                self.table.appendRow([3], el)
        if not good_names:
            for el in names:
                if name in el.lower():
                    good_names.append(el)
                    self.table.appendRow([3], el)
        if len(good_names) == 1:
            name = good_names[0]
            stat = parser.get_stat(name)
            self.table.appendRow([1, 1, 1], ["Contest id", "Problem", "Score"])
            for el in stat:
                self.table.appendRow(
                    [1, 1, 1],
                    map(str, [el.contest_id, el.short_name, el.score])
                )
        elif len(good_names) == 0:
            self.table.appendRow(3, 'NOT FOUND')
            self.table.item(0, 0).setTextAlignment(QtCore.Qt.AlignHCenter)

    def open_help(self):
        text_help = '''Problem Chooser for 22b class, school 179

Здесь вы можете узнать, какие задачи вам будет проще всего решить, что бы \
побыстрее закрыть дедлайн.

В поле ввода можно ввести своё имя, и вам будет предложен список \
нерешённых задач в порядке возрастания сложности.
В списке вы можете увидеть счёт задачи, id контеста и название задачи (как в \
тестирующей системе - A, B, C и т.д.)

Score - счёт задач. Чем больше счёт, тем, скорее всего, вам будет проще \
решить задачу. Это значение зависит от посылок других людей, так что у самых \
новых задач счёт будет не совсем корректен (он просто будет около нуля).

Данные о посылках для подсчёта простоты задач берутся из общей таблицы \
ejudge, так что если server.179.ru недоступен, то обновить данные не \
получиться. Но они сохраняются, так что при перезапуске программы все данные \
останутся.
Вручную обновить данные можно при нажатии Сtrl+R или в меню.

Поддержать проект вы можете отправив любую сумму:
- на телефон +79295917075 (мегафон).
- на yandex.money 4100 1489 0105 922
'''
        QtWidgets.QMessageBox.about(self.centralwidget, "Help",
                                    text_help)

    def set_last_reload_time(self):
        if parser.last_reload_time is None:
            self.statusbar.showMessage("Last reload: undefined")
        else:
            strtime = parser.last_reload_time.strftime('%x %X')
            self.statusbar.showMessage("Last reload: " + strtime)

    def on_reload_finished(self):
        self.set_last_reload_time()
        self.update_table()
        self.reloading = False

    def reload_table(self):
        if self.reloading:
            return
        self.reloading = True
        self.statusbar.showMessage("Reloading...")
        worker = Worker(self.threadPool, reload_table)
        worker.signals.finished.connect(self.on_reload_finished)
        self.threadPool.start(worker)

    def select_name(self):
        item = self.table.currentItem()
        if item.text() in parser.get_names():
            self.lineEdit.setText(item.text())
