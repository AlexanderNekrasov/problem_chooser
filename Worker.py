import traceback
from PyQt5 import QtCore


class WorkerSignals(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    error = QtCore.pyqtSignal(tuple)


class Worker(QtCore.QRunnable):

    def __init__(self, threadpool, function):
        super(Worker, self).__init__()
        self.threadpool = threadpool
        self.function = function
        self.args = list()
        self.kwargs = dict()
        self.result = None
        self.error = None
        self.cnt_start = 0
        self.is_started = False
        self.is_running = False
        self.signals = WorkerSignals()
        self.reset()

    def set_args(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def reset(self):
        super().__init__()
        self.is_started = False

    @QtCore.pyqtSlot()
    def run(self):
        self.is_running = True
        try:
            self.result = self.function(*self.args, **self.kwargs)

        except Exception as ex:
            self.error = (ex, traceback.format_exc())
            self.signals.error.emit(self.error)
        finally:
            self.signals.finished.emit()
        self.is_running = False

    def start(self):
        if self.is_started:
            self.reset()
        self.cnt_start += 1
        self.is_started = True
        self.threadpool.start(self)
