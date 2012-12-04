# -*- coding: utf-8 -*-
import codecs
import sys

from PyQt4.QtCore import QTimer
from PyQt4.QtGui import QMainWindow, QWidget, QApplication
from dulwich.repo import Repo
import dulwich.errors
import egdcodec

from qttest_ui import Ui_MainWindow
from player_tab import PlayerTab
from tournament import Tournament


codecs.register_error('egd', egdcodec.egd_replace)


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

    def updatetabs(self):
        """Update all open tabs from underlying data model."""
        for i in range(len(self.ui.tabWidget)):
            widget = self.ui.tabWidget.widget(i)
            widget.update()


def main():
    app = QApplication(sys.argv)

    turnpath = '/data/lindroos/pybaduk/turn'
    gbgopen = Tournament(turnpath, u'Göteborg Open 2013')

    mainwindow = MainWindow()
    updatetimer = QTimer()
    updatetimer.timeout.connect(mainwindow.updatetabs)
    updatetimer.start(500)

    playerTab = PlayerTab(gbgopen)
    mainwindow.ui.tabWidget.clear()
    mainwindow.ui.tabWidget.addTab(playerTab, "Players")
    mainwindow.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
