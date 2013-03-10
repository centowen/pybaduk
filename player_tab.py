from functools import total_ordering
import locale

from PyQt4.QtGui import QWidget, QTableWidgetItem, QTableWidgetSelectionRange
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


class PlayerTab(QWidget):
    def __init__(self, tournament, parent=None):
        QWidget.__init__(self, parent)
        self.tournament = tournament

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

        table_header = ['player_index']
        for field in self.tournament.config['player_fields']:
            if field.visible:
                table_header.append(field.name)

        # Add player index as column zero but don't show it.
        tableWidget.setColumnCount(len(table_header))
        tableWidget.setHorizontalHeaderLabels(table_header)
        tableWidget.setColumnHidden(0, True)

        for i, player in enumerate(self.tournament.players):
            print player.player_index
            for col_index, col_name in enumerate(table_header):
                if col_index == 0:
                    cell_value = player.player_index
                else:
                    print col_name
                    print player[col_name]
                    cell_value = player[col_name]

                if isinstance(cell_value, bool):
                    cell_value = unicode(cell_value)

                tableWidget.setItem(i, col_index, QTableWidgetItem(cell_value))

            if player in selectedPlayers:
                selRange = QTableWidgetSelectionRange(
                            i, 0, i, tableWidget.columnCount() - 1)
                tableWidget.setRangeSelected(selRange, True)
            print

        tableWidget.setSortingEnabled(True)
        tableWidget.setCurrentCell(currentRow, currentColumn)
