import UI
from Parser import Parser
from PyQt5 import QtGui, QtWidgets


is_loaded = False
if Parser.is_cache_exists():
    try:
        print('Loading from cache...')
        UI.parser = Parser.from_cache()
        print('Loaded')
        is_loaded = True
    except Exception as ex:
        print(ex)
if not is_loaded:
    print('Loading from server...')
    UI.parser = Parser.from_server()
    print('Loaded')
    is_loaded = True
    UI.parser.save_cache()


if __name__ == "__main__":
    import sys
    font = QtGui.QFont()
    font.setPixelSize(16)
    font.setStyleHint(QtGui.QFont.Monospace)
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    MainWindow.setFont(font)
    ui = UI.Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
