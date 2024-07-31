import datetime
import threading
import time


class Cracker:

    def __init__(self):
        self._msg = datetime.datetime.now()

    def _run(self):
        while True:
            print(self._msg)
            time.sleep(1)

    def run(self):
        t = threading.Thread(target=self._run)
        t.start()


if __name__ == '__main__':
    cracker = Cracker()
    cracker.run()
    time.sleep(5)
    cracker._msg = '123123123'
