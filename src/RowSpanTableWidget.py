from PyQt5 import QtCore, QtWidgets


class RowSpanTableWidget(QtWidgets.QTableWidget):

    def __init__(self, maxColumnCount, *args):
        super().__init__(*args)
        self.setStyleSheet(
            "QTableWidget::item:selected { background : grey; }")
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.setColumnCount(maxColumnCount)
        self.horizontalHeader().setVisible(False)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.Stretch)

    def _check_spans_texts(self, spans, texts):
        return sum(spans) == self.columnCount() and len(spans) == len(texts)

    def appendRow(self, spans=(), texts=()):
        if not self._check_spans_texts(spans, texts):
            raise Exception('Wrong format of spans and/or texts')
        ind = self.rowCount()
        self.insertRow(ind)
        self.setRowHeight(ind, QtWidgets.QLabel().fontMetrics().height())
        jnd = 0
        for cell_size, text in zip(spans, texts):
            if cell_size > 1:
                self.setSpan(ind, jnd, 1, cell_size)
            newItem = QtWidgets.QTableWidgetItem(text)
            newItem.setFlags(QtCore.Qt.ItemIsEnabled |
                             QtCore.Qt.ItemIsSelectable)
            newItem.setFont(self.font())
            self.setItem(ind, jnd, newItem)
            jnd += cell_size

    def getRow(self, row):
        return [self.item(row, col) for col in range(self.columnCount())]

    def lastRowItem(self, column):
        return self.item(self.rowCount() - 1, column)

    def clear(self):
        self.setRowCount(0)

    def deselect_all(self):
        self.setCurrentItem(QtWidgets.QTableWidgetItem())

    def focusOutEvent(self, e):
        self.deselect_all()
