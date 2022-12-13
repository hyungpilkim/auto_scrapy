import sys
import threading
import time

from multiprocessing import Process, Queue
import multiprocessing as mp

from PyQt5 import QtWidgets, QtGui, QtCore
import qt_gui
import browser


if __name__ == "__main__":
    job_q = Queue()
    result_q = Queue()

    Browser = browser.Browser(job_q, result_q);
    p = Process(name="open_browser", target=Browser.open_browser, args=(), daemon=True)
    p.start()

    app = QtWidgets.QApplication(sys.argv)
    dm = qt_gui.QtGui(job_q, result_q)
    dm.show()
    app.exit((app.exec_()))