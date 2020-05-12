import UI
from PyQt5 import QtWidgets


UI.initParser()

if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = UI.Ui_MainWindow()
    MainWindow.show()
    sys.exit(app.exec_())
