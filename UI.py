from PyQt5 import QtCore, QtWidgets, QtGui
from RowSpanTableWidget import RowSpanTableWidget
from Parser import Parser
from Worker import Worker
import cfg

parser = Parser()


def initParser():
    global parser
    is_loaded = False
    if Parser.is_cache_exists():
        try:
            print('Loading from cache...')
            parser = Parser.from_cache()
            print('Loaded')
            is_loaded = True
        except Exception as ex:
            print(ex)
    if not is_loaded:
        print('Loading from server...')
        parser = Parser.from_server()
        print('Loaded')
        parser.save_cache()


def reload_table():
    global parser
    parser = Parser.from_server()
    parser.save_cache()


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
        self.table.doubleClicked.connect(self.select_name)

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

        self.threadPool = QtCore.QThreadPool()
        self.reloadWorker = Worker(self.threadPool, reload_table)
        self.reloadWorker.signals.finished.connect(self.on_reload_finished)

        self.update_table()

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

В специальном поле можно ввести своё имя, и вам будет предложен список \
нерешённых задач в порядке возрастания сложности.
В списке вы можете увидеть оценку задачи (score), id контеста и название \
задачи (как в тестирующей системе - A, B, C и т.д.)

Score - оценка простоты задач. Чем больше оценка, тем, скорее всего, вам \
будет легче решить задачу. Она зависит от посылок других людей, так что у \
самых новых задач оценка будет не совсем корректна (она просто будет около \
нуля).

Данные о посылках для подсчёта простоты задач берутся из общей таблицы \
ejudge, так что если server.179.ru недоступен, то обновить данные не \
получиться. Но они сохраняются, так что при перезапуске программы все данные \
останутся.
Вручную обновить данные можно при нажатии на кнопку "Reload", Сtrl+R или в \
меню.

Если вы обнаружили неисправность или хотите новую функциональность, \
*обязательно* напишите разработчикам:
 * telegram: @crazyilian
 * telegram: @AlexNekrasov01
 * vk: @crazyilian

Также поддержать проект вы можете отправив любую сумму:
 * на телефон +79295917075 (мегафон).
 * на yandex.money 4100-1489-0105-922
'''
        QtWidgets.QMessageBox.about(self.centralwidget, "Help",
                                    text_help)

    def set_last_reload_time(self):
        self.statusbarLabel.setText(self.get_last_reload_time())

    def get_last_reload_time(self):
        if parser.last_reload_time is None:
            return " Last reload: undefined"
        else:
            strtime = parser.last_reload_time.strftime('%x %X')
            return " Last reload: " + strtime

    def on_reload_finished(self):
        self.statusbarLabel.setText(self.get_last_reload_time())
        self.set_last_reload_time()
        self.update_table()

    def reload_table(self):
        if self.reloadWorker.is_running:
            return
        self.statusbarLabel.setText(" Reloading...")
        self.reloadWorker.start()

    def select_name(self):
        item = self.table.currentItem()
        if item.text() in parser.get_names():
            self.lineEdit.setText(item.text())
