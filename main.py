from PyQt5 import QtWidgets
from PyQt5 import QtGui

from src import UI
from cfg import resource


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    font_id = QtGui.QFontDatabase.addApplicationFont(
        resource('Calibri-Regular.ttf'))
    font = QtGui.QFont(
        QtGui.QFontDatabase.applicationFontFamilies(font_id)[0], 11)
    app.setFont(font)
    app.setWindowIcon(QtGui.QIcon(resource("icon.ico")))
    MainWindow = UI.Ui_MainWindow()
    MainWindow.show()
    sys.exit(app.exec_())
