# -*- coding: utf-8 -*-
import sys
# import PyQt4
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qttest_ui import Ui_MainWindow
from player_tab import Ui_PlayerTab

from dulwich.repo import Repo
import dulwich.errors

import codecs
import egdcodec
from tournament import Tournament

import locale
from functools import total_ordering

class MainUIWindow(QMainWindow):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.ui = Ui_MainWindow()

        self.ui.setupUi(self)


class PlayerTab(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.ui = Ui_PlayerTab()

        self.ui.setupUi(self)


@total_ordering
class Name(QTableWidgetItem):
    def __init__(self, name):
        super(Name,self).__init__(name)
        self.name = name
        locale.setlocale(locale.LC_ALL, "sv_SE.UTF-8")

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name.encode('ascii', errors='egd')
    
    def __eq__(self, other_name):
        return locale.strcoll(self.name, other_name.name) == 0

    def __lt__(self, other_name):
        return locale.strcoll(self.name, other_name.name) < 0


codecs.register_error('egd', egdcodec.egd_replace)

def main():
    app = QApplication(sys.argv)

    turnpath = '/data/lindroos/pybaduk/turn'
    gbgopen = Tournament(turnpath, u'Göteborg Open 2013')

    myapp = MainUIWindow()
    playerTab = PlayerTab()
    playerlist = gbgopen.players
    playerTab.ui.tableWidget.setRowCount(len(playerlist))
    playerTab.ui.tableWidget.setColumnCount(3)
    playerTab.ui.tableWidget.verticalHeader().hide()
    playerTab.ui.tableWidget.setHorizontalHeaderLabels(['Given name', 'Family name', 'Rank'])

    myapp.ui.tabWidget.clear()
    myapp.ui.tabWidget.addTab(playerTab, "Players")
    for (i,player) in enumerate(sorted(playerlist, key=lambda player: player['family_name'])):
#         QTableWidgetItem(unicode(player), myapp.ui.tableWidget)
        family_name = Name(player['family_name'])
        given_name = Name(player['given_name'])
#         family_name = QTableWidgetItem(Name(player['family_name']))
#         given_name = QTableWidgetItem(Name(player['given_name']))
        rank = player['rank']
        if player['rank'] == None:
            rank = 'No rank'
        rank = QTableWidgetItem(rank)
        playerTab.ui.tableWidget.setItem(i, 0, given_name)
        playerTab.ui.tableWidget.setItem(i, 1, family_name)
        playerTab.ui.tableWidget.setItem(i, 2, rank)
    playerTab.ui.tableWidget.resizeColumnsToContents()
    playerTab.ui.tableWidget.horizontalHeader().setStretchLastSection(True)
    myapp.show()
    sys.exit(app.exec_())
#   a = QApplication(sys.argv)
# 
#   w = QWidget()
#   w.resize(320, 240)
#   w.setWindowTitle('Hello World!')
#   w.show()
# 
#   sys.exit(a.exec_())

if __name__ == "__main__":
    main()
