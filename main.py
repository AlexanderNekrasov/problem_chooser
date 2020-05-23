from PyQt5 import QtWidgets
from PyQt5 import QtGui

from src import UI
from cfg import resource


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon(resource("icon.ico")))
    MainWindow = UI.Ui_MainWindow()
    MainWindow.show()
    sys.exit(app.exec_())
