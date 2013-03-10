# -*- coding: utf-8 -*-
import codecs
import sys

from PyQt4.QtCore import QTimer, QSettings
from PyQt4.QtGui import QMainWindow, QWidget, QApplication
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

    settings = QSettings('weirdo', 'pybaduk')

    turnpath = str(settings.value('turnpath').toString())
    if turnpath == '':
        turnpath = './turn'
        settings.setValue('turnpath', turnpath)
    gbgopen = Tournament(turnpath, u'Göteborg Open 2013')
#    gbgopen.add_extra_player_field((u'Clöbb', unicode))
    gbgopen.add_extra_player_field((u'Has päjd', bool))
    #gbgopen.remove_extra_player_field(u'Has paid')

    mainwindow = MainWindow()
    updatetimer = QTimer()
    updatetimer.timeout.connect(mainwindow.updatetabs)
    updatetimer.start(500)

    playerTab = PlayerTab(gbgopen, settings)
    mainwindow.ui.tabWidget.clear()
    mainwindow.ui.tabWidget.addTab(playerTab, "Players")
    mainwindow.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
