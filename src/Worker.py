import traceback
from PyQt5 import QtCore


def EMPTY_FUNCTION(*args, **kwargs):
    pass


class ModifiedSignal(QtCore.QObject):
    signal = QtCore.pyqtSignal()

    def disconnect_all(self):
        try:
            while True:
                self.disconnect()
        except TypeError:
            pass

    def reconnect(self, handler):
        self.disconnect_all()
        self.connect(handler)

    def __getattr__(self, item):
        return self.signal.__getattribute__(item)


class WorkerSignals(QtCore.QObject):
    finished = ModifiedSignal()


class Worker(QtCore.QThread):

    def __init__(self):
        super().__init__()
        self.function = EMPTY_FUNCTION
        self.args = []
        self.kwargs = {}
        self.result = None
        self.error = None
        self.signals = WorkerSignals()

    def run(self):
        try:
            self.result = self.function(*self.args, **self.kwargs)
        except Exception as ex:
            self.error = (ex, traceback.format_exc())
        finally:
            self.signals.finished.emit()

    def __call__(self, _worker_function, _worker_finished, *args, **kwargs):
        self.function = _worker_function
        self.signals.finished.reconnect(_worker_finished)
        self.args = args
        self.kwargs = kwargs
        self.start()

    def join(self):
        self.quit()
        self.wait()
