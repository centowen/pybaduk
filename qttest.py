# -*- coding: utf-8 -*-
import sys
# import PyQt4
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qttest_ui import Ui_MainWindow

from dulwich.repo import Repo
import dulwich.errors

import codecs
import egdcodec
from tournament import Tournament

class MainUIWindow(QMainWindow):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.ui = Ui_MainWindow()

        self.ui.setupUi(self)


codecs.register_error('egd', egdcodec.egd_replace)

def main():
    app = QApplication(sys.argv)

    turnpath = '/data/lindroos/pybaduk/turn'
    gbgopen = Tournament(turnpath, u'Göteborg Open 2013')

    myapp = MainUIWindow()
    playerlist = gbgopen.players
    myapp.ui.tableWidget.setRowCount(len(playerlist))
    myapp.ui.tableWidget.setColumnCount(3)
    myapp.ui.tableWidget.verticalHeader().hide()
    myapp.ui.tableWidget.setHorizontalHeaderLabels(['Given name', 'Family name', 'Rank'])
    for (i,player) in enumerate(sorted(playerlist, key=lambda player: player['family_name'])):
#         QTableWidgetItem(unicode(player), myapp.ui.tableWidget)
        family_name = QTableWidgetItem(player['family_name'])
        given_name = QTableWidgetItem(player['given_name'])
        rank = player['rank']
        if player['rank'] == None:
            rank = 'No rank'
        rank = QTableWidgetItem(rank)
        myapp.ui.tableWidget.setItem(i, 0, given_name)
        myapp.ui.tableWidget.setItem(i, 1, family_name)
        myapp.ui.tableWidget.setItem(i, 2, rank)
    myapp.ui.tableWidget.resizeColumnsToContents()
    myapp.ui.tableWidget.horizontalHeader().setStretchLastSection(True)
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
