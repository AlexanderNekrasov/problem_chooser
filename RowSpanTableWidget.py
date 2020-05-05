from PyQt5 import QtCore, QtWidgets


class RowSpanTableWidget(QtWidgets.QTableWidget):

    def __init__(self, maxColumnCount):
        super().__init__()
        self.setColumnCount(maxColumnCount)
        self.horizontalHeader().setVisible(False)
        self.verticalHeader().setVisible(False)

    def _fix_spans_and_texts(self, spans_, texts_):
        if type(spans_) not in (list, tuple):
            spans = [spans_]
        else:
            spans = list(spans_)
        if type(texts_) not in (list, tuple):
            texts = [texts_]
        else:
            texts = list(texts_)
        spans += [1] * max(0, len(texts) - len(spans))
        texts += [''] * max(0, len(spans) - len(texts))

        columns = self.columnCount()
        sm = sum(spans)
        while sm > columns:
            if sm - spans[-1] < columns:
                spans[-1] = columns - (sm - spans[-1])
                sm = columns
            else:
                sm -= spans[-1]
                spans.pop()
                texts.pop()

        spans += [1] * (columns - sm)
        texts += [''] * (columns - sm)
        return tuple(spans), tuple(texts)

    def appendRow(self, spans=(), texts=()):
        spans, texts = self._fix_spans_and_texts(spans, texts)
        ind = self.rowCount()
        self.insertRow(ind)
        jnd = 0
        for cell_size, text in zip(spans, texts):
            if cell_size > 1:
                self.setSpan(ind, jnd, 1, cell_size)
            newItem = QtWidgets.QTableWidgetItem(text)
            newItem.setFlags(QtCore.Qt.ItemIsEnabled)
            self.setItem(ind, jnd, newItem)
            jnd += cell_size
