import webbrowser
from PyQt5 import QtCore, QtWidgets, QtGui

import cfg
from src.MainPageParser import MainPageParser
from src.RowSpanTableWidget import RowSpanTableWidget
from src.TableParser import TableParser
from src.Worker import Worker, reconnect, disconnect_all
from src.Config import config, save_config, reset_config


initializing_parsers_number = 0


def initParser(parserClass):
    global initializing_parsers_number
    initializing_parsers_number += 1

    name = parserClass.__name__
    parser = None

    # parserClass.delete_cache()
    if parserClass.cache_exists():
        try:
            print(f"Loading {name} from cache...")
            parser = parserClass.from_cache()
        except Exception as ex:
            print(ex)
    if parser is None:
        print(f"Loading {name} from server...")
        parser = parserClass.from_server()

    initializing_parsers_number -= 1
    return parser


class Ui_MainWindow(QtWidgets.QMainWindow):

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.tableParser = TableParser()
        self.mainPageParser = MainPageParser()
        self.setupUi()

    def initParsers(self):
        self.tableParser = initParser(TableParser)
        self.mainPageParser = initParser(MainPageParser)

    def setupUi(self):
        self.setWindowTitle("Problem Chooser v" + cfg.VERSION)

        self.resize(500, 600)

        self.centralwidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.centralwidget)

        self.headerLabel = QtWidgets.QLabel(self.centralwidget)
        self.headerLabel.setText("Найдите самые простые задачи для себя")

        self.reloadButton = QtWidgets.QPushButton(" Обновить ")
        self.reloadButton.clicked.connect(self.reload_table)

        self.header = QtWidgets.QHBoxLayout()
        self.header.addWidget(self.headerLabel, stretch=5)
        self.header.addWidget(self.reloadButton, stretch=1)

        self.lineEdit = QtWidgets.QLineEdit()
        self.lineEdit.textChanged.connect(self.update_table)
        self.lineEdit.setPlaceholderText("Введите ваше имя")

        self.table = RowSpanTableWidget(3, self)
        self.table.doubleClicked.connect(self.double_clicked)

        self.main_layout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.main_layout.addLayout(self.header)
        self.main_layout.addSpacing(10)
        self.main_layout.addWidget(self.lineEdit)
        self.main_layout.addWidget(self.table)

        self.menubar = QtWidgets.QMenuBar(self)
        self.setMenuBar(self.menubar)

        self.tableReloadSubmenu = QtWidgets.QAction("Обновить (~5 сек)")
        self.tableReloadSubmenu.setShortcut("Ctrl+R")
        self.tableReloadSubmenu.triggered.connect(self.reload_call)

        self.tableAutoreloadSubmenu = QtWidgets.QAction(
            "Автообновление таблицы")
        self.tableAutoreloadSubmenu.triggered.connect(
            self.open_autoreload_table)

        self.tableMenu = self.menubar.addMenu("&Таблица")
        self.tableMenu.addAction(self.tableReloadSubmenu)
        self.tableMenu.addAction(self.tableAutoreloadSubmenu)

        self.configFontSubmenu = QtWidgets.QAction("Шрифт")
        self.configFontSubmenu.triggered.connect(self.open_font_config)

        self.configAutoinputSubmenu = QtWidgets.QAction("Автоввод имени")
        self.configAutoinputSubmenu.triggered.connect(
            self.open_autoinput_config)

        self.configResetSubmenu = QtWidgets.QAction("Сбросить")
        self.configResetSubmenu.triggered.connect(self.reset_config)

        self.configMenu = self.menubar.addMenu("&Настройки")
        self.configMenu.addAction(self.configFontSubmenu)
        self.configMenu.addAction(self.configAutoinputSubmenu)
        self.configMenu.addAction(self.configResetSubmenu)

        self.helpSubmenu = QtWidgets.QAction("О программе")
        self.helpSubmenu.setShortcut("Ctrl+H")
        self.helpSubmenu.triggered.connect(self.open_help)

        self.helpMenu = self.menubar.addMenu("&Помощь")
        self.helpMenu.addAction(self.helpSubmenu)

        self.autoreloadTimer = QtCore.QTimer()
        self.autoreloadTimer.timeout.connect(
            lambda: self.reload_call(is_autoreload=True))
        self.autoreload_waiting = False

        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbarLabel = QtWidgets.QLabel()
        self.statusbarTimer = QtCore.QTimer()
        self.statusbar.addWidget(self.statusbarLabel)
        self.setStatusBar(self.statusbar)
        self.set_last_reload_time()

        self.update_table()
        self.reload_table(initialize=True)
        self.load_autoinput()
        self.update_autoreload()

    def reset_config(self):
        config.clear()
        config.update(reset_config())
        save_config()
        self.update_font()

    def closeEvent(self, event):
        self.save_autoinput_last()
        event.accept()

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # #  TABLE  # # # # # # # # # # # # # # # # #

    def double_clicked(self):
        item = self.table.currentItem()
        if item.text() in self.tableParser.get_names():
            self.lineEdit.setText(item.text())
            return
        cells = self.table.getRow(item.row())
        if item.column() == 0:
            url = self.mainPageParser.get_contest_url_by_id(cells[0].text())
            if url is not None:
                webbrowser.open(url)
        elif item.column() == 1:
            url = self.mainPageParser.get_statements_url_by_id(cells[0].text())
            if url is not None:
                url += "#prob_" + item.text()
                webbrowser.open(url)
        elif item.column() == 2:
            url = self.mainPageParser.get_results_url_by_id(cells[0].text())
            if url is not None:
                webbrowser.open(url)

    def update_table(self):
        name = self.lineEdit.text().lower()
        names = self.tableParser.get_names()
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
            stat = self.tableParser.get_stat(name)
            self.table.appendRow([1, 1, 1],
                                 ["ID контеста", "Задача", "Простота"])
            for el in stat:
                self.table.appendRow(
                    [1, 1, 1],
                    tuple(map(str, [el.contest.id, el.short_name, el.score]))
                )
                self.table.lastRowItem(0).setToolTip(el.contest.name)
                self.table.lastRowItem(1).setToolTip(el.full_name)
        elif len(good_names) == 0:
            self.table.appendRow([3], ["Не найдено"])
            self.table.item(0, 0).setTextAlignment(QtCore.Qt.AlignHCenter)

    def set_last_reload_time(self):
        self.statusbarLabel.setText(self.get_last_reload_time())

    def get_last_reload_time(self):
        if self.tableParser.last_reload_time is None:
            strtime = "undefined"
        else:
            strtime = self.tableParser.last_reload_time.strftime("%x %X")
        return " Последнее обновление: " + strtime + " "

    def on_reload_finished(self):
        if self.tableParser.isReloading() or self.mainPageParser.isReloading():
            print('Still reloading...')
            return
        print('Reload finished')
        self.statusbarTimer.stop()
        self.statusbarLabel.setText(self.get_last_reload_time())
        self.set_last_reload_time()
        self.update_table()
        if self.autoreload_waiting:
            self.autoreload_waiting = False
            self.reload_table(is_autoreload=True)
            self.update_autoreload()

    def is_reloading(self):
        return self.tableParser.isReloading() or \
               self.mainPageParser.isReloading()

    def reload_call(self, is_autoreload=False):
        if is_autoreload:
            disconnect_all(self.reloadButton.clicked)
            self.reloadButton.animateClick()
            self.reloadButton.clicked.connect(self.reload_table)
            self.reload_table(is_autoreload=True)
        else:
            self.reloadButton.animateClick()

    def reload_table(self, initialize=False, is_autoreload=False):
        already_run = not initialize and \
                      (initializing_parsers_number > 0 or self.is_reloading())
        if is_autoreload:
            self.autoreload_waiting = already_run
            print('Autoreload waiting:', already_run)
            if already_run:
                self.autoreloadTimer.stop()
        if already_run:
            print("Already reloading")
            return

        def show_statusbar_reloading():
            nonlocal timer_count
            self.statusbarLabel.setText(f" Обновление... {timer_count}с ")
            timer_count += 1

        reconnect(self.statusbarTimer.timeout, show_statusbar_reloading)
        timer_count = 0
        show_statusbar_reloading()
        self.statusbarTimer.start(1000)

        if initialize:
            print('Initializing parsers...')
            self.worker = Worker()
            self.worker(self.initParsers, self.on_reload_finished)
        else:
            self.tableParser.reload(self.on_reload_finished)
            self.mainPageParser.reload(self.on_reload_finished)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # #  HELP   # # # # # # # # # # # # # # # # #

    def open_help(self):
        with open(cfg.resource("help"), "r", encoding="utf-8") as f:
            text = f.read().strip()
        with open(cfg.resource("help-title"), "r", encoding="utf-8") as f:
            title = f.read().strip()
        with open(cfg.resource("help-suggest-link"),
                  "r", encoding="utf-8") as f:
            suggest_link = f.read().strip()
        # init window
        help_window = QtWidgets.QDialog(self)
        help_window.setWindowTitle('О программе')
        help_window.resize(self.width() + 50, 600)
        help_window.setLayout(QtWidgets.QVBoxLayout())

        # title
        img = QtGui.QPixmap(cfg.resource('icon.ico'))
        title_layout = QtWidgets.QHBoxLayout()
        img_label = QtWidgets.QLabel()
        img_label.setPixmap(img)
        title_layout.addWidget(img_label)
        title_label = QtWidgets.QLabel(title)
        font = self.font()
        font.setPointSize(config["title_font_size"])
        title_label.setFont(font)
        title_layout.addStretch(1)
        title_layout.addWidget(title_label)
        title_layout.addStretch(2)

        # body
        help_label = QtWidgets.QLabel(text)
        help_label.setWordWrap(True)
        scroll_help = QtWidgets.QScrollArea()
        scroll_help.setWidget(help_label)

        # buttons
        buttons_layout = QtWidgets.QHBoxLayout()
        suggest_button = QtWidgets.QPushButton("Поддержать")
        suggest_button.clicked.connect(
            lambda: webbrowser.open(suggest_link))
        ok_button = QtWidgets.QPushButton("ОК")
        ok_button.clicked.connect(help_window.close)
        ok_button.setDefault(True)
        buttons_layout.addStretch(4)
        buttons_layout.addWidget(suggest_button, stretch=1)
        buttons_layout.addWidget(ok_button, stretch=1)

        # add parts to window
        help_window.layout().addLayout(title_layout)
        help_window.layout().addWidget(scroll_help)
        help_window.layout().addLayout(buttons_layout)
        help_window.resizeEvent = lambda *args: help_label.setFixedWidth(
            help_window.width() - 50)

        # show window
        help_window.exec_()

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # #  FONT SETTINGS  # # # # # # # # # # # # # # #

    def update_font(self):
        font = self.font()
        font.setPointSize(config["main_font_size"])
        self.app.setFont(font)
        self.update_table()

    def save_font_size(self, main_font_size, title_font_size):
        config["main_font_size"] = main_font_size
        config["title_font_size"] = title_font_size
        save_config()
        self.update_font()

    def open_font_config(self):
        def font_config_item(name, pretty_name):
            layout = QtWidgets.QHBoxLayout()
            label = QtWidgets.QLabel(pretty_name)
            layout.addWidget(label, stretch=1)
            spin_box = QtWidgets.QSpinBox()
            spin_box.setRange(3, 50)
            spin_box.setValue(config[name])
            layout.addWidget(spin_box)
            return layout, spin_box.value

        window = QtWidgets.QDialog(self)
        window.setWindowTitle("Настройки шрифта")
        window.setLayout(QtWidgets.QVBoxLayout())

        lay_main, get_main_font_size = font_config_item("main_font_size",
                                                        "Основной шрифт:")
        lay_title, get_title_font_size = font_config_item("title_font_size",
                                                          "Шрифт заголовков:")
        window.layout().addWidget(QtWidgets.QLabel("Выберите размеры шрифтов"))
        window.layout().addLayout(lay_main)
        window.layout().addLayout(lay_title)

        def save():
            self.save_font_size(get_main_font_size(), get_title_font_size())
            window.close()

        ok_button = QtWidgets.QPushButton("Сохранить")
        ok_button.clicked.connect(save)
        ok_button.setDefault(True)
        cancel_button = QtWidgets.QPushButton("Отменить")
        cancel_button.clicked.connect(window.close)
        buttons = [cancel_button, ok_button]
        buttons_layout = QtWidgets.QHBoxLayout()
        for b in buttons:
            buttons_layout.addWidget(b)
        window.layout().addLayout(buttons_layout)

        window.exec_()

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # AUTO INPUT SETTINGS # # # # # # # # # # # # # #

    def load_autoinput(self):
        if config["is_autoinput_last"]:
            text = config["autoinput_last"]
        else:
            text = config["autoinput_text"]
        self.lineEdit.setText(text)

    @staticmethod
    def save_autoinput(line, checkBox):
        config["is_autoinput_last"] = checkBox.isChecked()
        config["autoinput_text"] = line.text()
        save_config()

    def save_autoinput_last(self):
        config["autoinput_last"] = self.lineEdit.text()
        save_config()

    def open_autoinput_config(self):
        font_size = config["main_font_size"]
        window = QtWidgets.QDialog(self)
        window.setWindowTitle("Автоввод имени")
        window.setLayout(QtWidgets.QVBoxLayout())

        def checkbox_clicked(state):
            line.setDisabled(state == QtCore.Qt.Checked)

        checkBox = QtWidgets.QCheckBox()
        checkBox.stateChanged.connect(checkbox_clicked)
        checkBox_size = int(font_size * 1.25)
        checkBox.setStyleSheet(  # set size
            f'QCheckBox::indicator {{ width: {checkBox_size}px; \
                                      height: {checkBox_size}px; }}')
        checkBox.setChecked(config["is_autoinput_last"])
        checkbox_clicked(checkBox.isChecked())

        input_last = QtWidgets.QHBoxLayout()
        input_last.addWidget(QtWidgets.QLabel("Запоминать последнее имя?"))
        input_last.addStretch(1)
        input_last.addSpacing(font_size * 5)
        input_last.addWidget(checkBox)

        line = QtWidgets.QLineEdit(config["autoinput_text"])
        line.setPlaceholderText("Имя по умолчанию")

        window.layout().addLayout(input_last)
        window.layout().addWidget(line)

        def save():
            self.save_autoinput(line, checkBox)
            window.close()

        ok_button = QtWidgets.QPushButton("Сохранить")
        ok_button.clicked.connect(save)
        ok_button.setDefault(True)
        cancel_button = QtWidgets.QPushButton("Отменить")
        cancel_button.clicked.connect(window.close)
        buttons = [cancel_button, ok_button]
        buttons_layout = QtWidgets.QHBoxLayout()
        for b in buttons:
            buttons_layout.addWidget(b)
        window.layout().addLayout(buttons_layout)

        window.exec_()

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # #  AUTO RELOAD TABLE  # # # # # # # # # # # # # #

    def update_autoreload(self):
        self.autoreload_waiting = False
        self.autoreloadTimer.stop()
        if config["is_autoreload"]:
            self.autoreloadTimer.start(config["autoreload_timeout"] * 1000)

    def save_autoreload(self, spinBox, checkBox):
        config["is_autoreload"] = checkBox.isChecked()
        config["autoreload_timeout"] = spinBox.value()
        save_config()
        self.update_autoreload()

    def open_autoreload_table(self):
        font_size = config["main_font_size"]
        window = QtWidgets.QDialog(self)
        window.setWindowTitle("Автообновление таблицы")
        window.setLayout(QtWidgets.QVBoxLayout())

        def checkbox_clicked(state):
            spinBox.setEnabled(state)

        spinBox = QtWidgets.QSpinBox()
        spinBox.setRange(0, 9999999)
        spinBox.setValue(config["autoreload_timeout"])
        sec_layout = QtWidgets.QHBoxLayout()
        sec_layout.addWidget(QtWidgets.QLabel("Секунд между обновлениями:"))
        sec_layout.addStretch(1)
        sec_layout.addWidget(spinBox)

        checkBox = QtWidgets.QCheckBox()
        checkBox.stateChanged.connect(checkbox_clicked)
        checkBox_size = int(font_size * 1.25)
        checkBox.setStyleSheet(  # set size
            f'QCheckBox::indicator {{ width: {checkBox_size}px; \
                                      height: {checkBox_size}px; }}')

        checkBox.setChecked(config["is_autoreload"])
        checkbox_clicked(checkBox.isChecked())

        is_autoreload = QtWidgets.QHBoxLayout()
        is_autoreload.addWidget(
            QtWidgets.QLabel("Использовать автообновление таблицы?"))
        is_autoreload.addStretch(1)
        is_autoreload.addSpacing(font_size)
        is_autoreload.addWidget(checkBox)

        window.layout().addLayout(is_autoreload)
        window.layout().addLayout(sec_layout)

        def save():
            self.save_autoreload(spinBox, checkBox)
            window.close()

        ok_button = QtWidgets.QPushButton("Сохранить")
        ok_button.clicked.connect(save)
        ok_button.setDefault(True)
        cancel_button = QtWidgets.QPushButton("Отменить")
        cancel_button.clicked.connect(window.close)
        buttons = [cancel_button, ok_button]
        buttons_layout = QtWidgets.QHBoxLayout()
        for b in buttons:
            buttons_layout.addWidget(b)
        window.layout().addLayout(buttons_layout)

        window.exec_()
