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
        self._editedPlayers = set()
        self._adding_player = False

        self.ui = Ui_PlayerTab()
        self.ui.setupUi(self)

        self.update()

        self.ui.tableWidget.verticalHeader().hide()
        self.ui.tableWidget.resizeColumnsToContents()
        self.ui.tableWidget.horizontalHeader().setStretchLastSection(True)

        self.ui.tableWidget.itemSelectionChanged.connect(self.players_selected)
        self.ui.add_player.clicked.connect(self.add_player_clicked)
        self.ui.ok_cancel.rejected.connect(self.clear_edited_players)
        self.ui.ok_cancel.accepted.connect(self.save_edited_players)

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

        tableWidget.blockSignals(True)
        tableWidget.clear()
        tableWidget.blockSignals(False)
        row_count = len(self.tournament.players)
        if self._adding_player:
            row_count += 1
        tableWidget.setRowCount(row_count)

        table_header = ['player_index']
        for field in self.tournament.config['player_fields']:
            if field.visible:
                table_header.append(field.name)

        # Add player index as column zero but don't show it.
        tableWidget.setColumnCount(len(table_header))
        tableWidget.setHorizontalHeaderLabels(table_header)
        tableWidget.setColumnHidden(0, True)

        for i, player in enumerate(self.tournament.players):
            for col_index, col_name in enumerate(table_header):
                if col_index == 0:
                    cell_value = player.player_index
                else:
                    cell_value = player[col_name]

                if isinstance(cell_value, bool):
                    cell_value = unicode(cell_value)

                tableWidget.setItem(i, col_index, QTableWidgetItem(cell_value))

            if player in selectedPlayers and not self._adding_player:
                selRange = QTableWidgetSelectionRange(
                    i, 0, i, tableWidget.columnCount() - 1)
                tableWidget.blockSignals(True)
                tableWidget.setRangeSelected(selRange, True)
                tableWidget.blockSignals(False)

        if self._adding_player:
            tableWidget.blockSignals(True)
            selRange = QTableWidgetSelectionRange(
                row_count - 1, 0, row_count - 1, tableWidget.columnCount() - 1)
            tableWidget.setRangeSelected(selRange, True)
            tableWidget.blockSignals(False)

        tableWidget.setSortingEnabled(True)
        #tableWidget.setCurrentCell(currentRow, currentColumn)
        tableWidget.itemSelectionChanged.emit()

    def players_selected(self):
        selectedItems = self.ui.tableWidget.selectedItems()
        selectedRows = set([item.row() for item in selectedItems])
        selectedPlayers = set([self.playerAtRow(row) for row in selectedRows])

        if self._editedPlayers == selectedPlayers:
            return
        else:
            for edited_player in self._editedPlayers:
                if edited_player not in self.tournament.players:
                    print ('player {0} does not exist in '
                           'database!').format(edited_player.player_index)
                    self._editedPlayers = set()
                    return

            if not selectedPlayers:
                self.clear_edited_players()
                return
            elif self._editedPlayers:
                print self._editedPlayers
            elif self._adding_player:
                self._adding_player = False
                self.update()

            self._editedPlayers = selectedPlayers
            print "Populate right hand side with player{s} {0}!".format(
                list(selectedPlayers),
                s=('s' if len(selectedPlayers) > 1 else ''))

            for selectedPlayer in selectedPlayers:
                self.ui.given_name.setText(selectedPlayer['Given name'])
                self.ui.family_name.setText(selectedPlayer['Family name'])
                break

    def clear_edited_players(self):
        self._editedPlayers = set()
        if self._adding_player:
            self._adding_player = False
            self.update()
        self.ui.given_name.setText('')
        self.ui.family_name.setText('')

        tableWidget = self.ui.tableWidget
        selected_ranges = tableWidget.selectedRanges()
        tableWidget.blockSignals(True)
        for selected_range in selected_ranges:
            tableWidget.setRangeSelected(selected_range, False)
        tableWidget.blockSignals(False)

    def save_edited_players(self):
        if self._adding_player:
            params = {}
            params['Given name'] = unicode(self.ui.given_name.text())
            params['Family name'] = unicode(self.ui.family_name.text())
            player = self.tournament.add_player(params)
            self._editedPlayers.add(player)

        for edited_player in self._editedPlayers:
            edited_player['Given name'] = unicode(self.ui.given_name.text())
            edited_player['Family name'] = unicode(self.ui.family_name.text())

        #NB: The set is invalid because hashes have changed. Clearing will take
        #    care of it. So no worries.
        self.clear_edited_players()

    def add_player_clicked(self):
        self.clear_edited_players()
        self._adding_player = True
        self.update()
