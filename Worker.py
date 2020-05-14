import traceback
from PyQt5 import QtCore


def EMPTY_FUNCTION(*args, **kwargs):
    pass


class WorkerSignals(QtCore.QObject):
    finished = QtCore.pyqtSignal()


class Worker(QtCore.QThread):

    def __init__(self):
        super().__init__()
        self.function = EMPTY_FUNCTION
        self.args = []
        self.kwargs = {}

        self.moveToThread(self)

        self.result = None
        self.error = None

        self.signals = WorkerSignals()
        self.started.connect(self.function_run)

    def function_run(self):
        try:
            self.result = self.function(*self.args, **self.kwargs)
        except Exception as ex:
            self.error = (ex, traceback.format_exc())
        finally:
            self.signals.finished.emit()

    def __call__(self, _worker_function, _worker_finished, *args, **kwargs):
        self.function = _worker_function
        self.signals.finished.connect(_worker_finished)
        self.args = args
        self.kwargs = kwargs
        self.start()
