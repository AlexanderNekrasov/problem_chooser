import traceback
from PyQt5 import QtCore


def EMPTY_F(*args, **kwargs):
    pass


class Worker(QtCore.QRunnable):

    def __init__(self, threadpool, function, finished_f=EMPTY_F,
                 error_f=EMPTY_F, result_f=EMPTY_F, progress_f=EMPTY_F,
                 worker_info=None):
        self.threadpool = threadpool
        self.function = function
        self.args = list()
        self.kwargs = dict()
        self.finished_f = finished_f
        self.error_f = error_f
        self.result_f = result_f
        self.progress_f = progress_f
        self.worker_info = worker_info
        self.result = None
        self.error = None
        self.cnt_start = 0
        self.is_started = False
        self.is_running = False
        self.reset()

    def set_args(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        if self.progress_f != EMPTY_F:
            self.kwargs['worker_progress_callback'] = self.progress_f

    def reset(self):
        super().__init__()
        self.is_started = False

    @QtCore.pyqtSlot()
    def run(self):
        self.is_running = True
        try:
            self.result = self.function(*self.args, **self.kwargs,
                                        worker_info=self.worker_info)
        except Exception as ex:
            self.error = (ex, traceback.format_exc())
            self.error_f(self.error, worker_info=self.worker_info)
        else:
            self.result_f(self.result, worker_info=self.worker_info)
        finally:
            self.finished_f(worker_info=self.worker_info)
        self.is_running = False

    def start(self):
        if self.is_started:
            self.reset()
        self.cnt_start += 1
        self.is_started = True
        self.threadpool.start(self)
