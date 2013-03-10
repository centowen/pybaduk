from functools import total_ordering
import locale

from PyQt4.QtGui import QWidget, QTableWidgetItem, QTableWidgetSelectionRange
from PyQt4.QtCore import QSettings

from player_tab_ui import Ui_PlayerTab
from players import Player


@total_ordering
class OrderedName(QTableWidgetItem):
    def __init__(self, name):
        super(OrderedName, self).__init__(name)
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

playerUiRepr = {'given_name': {'label': 'Given name', 'tabletype': OrderedName}, 
                'family_name': {'label': 'Family name', 'tabletype': OrderedName}, 
                'rank': {'label': 'Rank', 'tabletype': QTableWidgetItem, 'default': 'No rank'},
                'club': {'label': 'Club', 'tabletype': OrderedName, 'default': 'Homeless'},
                'index': {'label': 'Index', 'tabletype': QTableWidgetItem}}

class PlayerTab(QWidget):
    def __init__(self, tournament, settings, parent=None):
        QWidget.__init__(self, parent)
        self.tournament = tournament
        self.settings = settings
        self.table_columns = [str(column.toString()) for column in settings.value('table_columns').toList()]
        if len(self.table_columns)==0:
            settings.setValue('table_columns', ['given_name', 'family_name', 'rank', 'club'])
            self.table_columns = [str(column.toString()) for column in settings.value('table_columns').toList()]

        self.ui = Ui_PlayerTab()
        self.ui.setupUi(self)

        self.update()

        self.ui.tableWidget.verticalHeader().hide()
        self.ui.tableWidget.resizeColumnsToContents()
        self.ui.tableWidget.horizontalHeader().setStretchLastSection(True)

    def playerAtRow(self, row):
        """Retrieve player object from row number."""
        player_index = str(self.ui.tableWidget.item(row, 0).text())
        return self.tournament.players[player_index]

    def update(self):
        """Update GUI from underlying data model."""
        tableWidget = self.ui.tableWidget
        tableWidget.setSortingEnabled(False)

        selectedItems = tableWidget.selectedItems()
        selectedRows = set([item.row() for item in selectedItems])
        selectedPlayers = [self.playerAtRow(row) for row in selectedRows]

        currentRow = tableWidget.currentRow()
        currentColumn = tableWidget.currentColumn()

        tableWidget.clear()
        tableWidget.setRowCount(len(self.tournament.players))
        local_columns = ['index'] + self.table_columns
        tableWidget.setColumnCount(len(local_columns))
        tableWidget.setHorizontalHeaderLabels([playerUiRepr[column]['label'] for column in local_columns])
        tableWidget.setColumnHidden(0, True)

        for i, player in enumerate(self.tournament.players):
            for (col_index, col_name) in enumerate(local_columns):
                defaultForField = playerUiRepr[col_name].get('default', '')
                field = playerUiRepr[col_name]['tabletype'](player.get(col_name, defaultForField))
                tableWidget.setItem(i, col_index, field)

            if player in selectedPlayers:
                selRange = QTableWidgetSelectionRange(
                            i, 0, i, tableWidget.columnCount() - 1)
                tableWidget.setRangeSelected(selRange, True)

        tableWidget.setSortingEnabled(True)
        tableWidget.setCurrentCell(currentRow, currentColumn)
