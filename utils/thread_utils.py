import threading


class CodeThread(threading.Thread):
    def __init__(self, func, code, result):
        threading.Thread.__init__(self)
        self.func = func
        self.code = code
        self.result = result

    def run(self):
        self.func(self.code, self.result)
