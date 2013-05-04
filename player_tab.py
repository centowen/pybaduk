from functools import total_ordering
import locale
import logging
import re

from PyQt4.QtGui import (QWidget, QTableWidgetItem, QTableWidgetSelectionRange,
                         QSpinBox, QValidator, QLabel, QLineEdit)
from player_tab_ui import Ui_PlayerTab
from players import Player


class PlayerFieldLineEdit(QLineEdit):

    def getDBValue(self):
        return unicode(self.text())

    def setDBValue(self, dbValue):
        if dbValue is None:
            dbValue = ''
        self.setText(dbValue)

    def clear(self):
        self.setText('')


class RankSpinBox(QSpinBox):

    _minvalue = -50

    def __init__(self, *args, **kwargs):
        super(RankSpinBox, self).__init__(*args, **kwargs)
        self.setMinimum(RankSpinBox._minvalue)
        self.acceptable_rank = re.compile('([0-9]+)\s*([k|d|p]).*', flags=re.IGNORECASE)
        self.intermediate_rank = re.compile('([0-9]+)\s*', flags=re.IGNORECASE)

    def validate(self, text, pos):
        if self.acceptable_rank.match(text) or text == '' or text == 'No rank':
            return (QValidator.Acceptable, pos)
        elif self.intermediate_rank.match(text):
            return (QValidator.Intermediate, pos)
        else:
            return (QValidator.Invalid, pos)

    def textFromValue(self, value):
        if value == RankSpinBox._minvalue:
            return 'No rank'
        elif 10 <= value:
            return '{0}p'.format(value - 9)
        elif 1 <= value < 10:
            return '{0}d'.format(value)
        else:
            return '{0}k'.format(1 - value)

    def valueFromText(self, text):
        if not text:
            return RankSpinBox._minvalue

        res = self.acceptable_rank.match(text)
        if res:
            number, level = res.groups()
            number = int(number)
            level = unicode(level).lower()
            if level == 'k':
                return 1 - number
            elif level == 'd':
                return number
            else:
                return number + 9
        else:
            return RankSpinBox._minvalue

    def setDBValue(self, dbValue):
        self.setValue(self.valueFromText(dbValue))

    def getDBValue(self):
        if self.value() == RankSpinBox._minvalue:
            return None

        return self.textFromValue(self.value())

    def clear(self):
        self.setValue(RankSpinBox._minvalue)


class BoolTableItem(QTableWidgetItem):
    def __init__(self, value, *args, **kwargs):
        if value:
            self.name = 'Yes'
        else:
            self.name = 'No'
        super(BoolTableItem, self).__init__(self.name, *args, **kwargs)


@total_ordering
class RankTableItem(QTableWidgetItem):
    LEVELDICT = {'p': 1, 'd': 2, 'k': 3}

    def __init__(self, value, *args, **kwargs):
        self.value = value
        if not self.value:
            self.value = 'No rank'
            self.level = None
            self.number = None
        else:
            try:
                self.level = RankTableItem.LEVELDICT[self.value[-1]]
                self.number = int(self.value[:-1])
            except (KeyError, ValueError):
                logging.error('Invalid rank: {0}'.format(value))
                self.value = 'No rank'
                self.level = None
                self.number = None

        super(RankTableItem, self).__init__(self.value, *args, **kwargs)

    def __unicode__(self):
        return self.value

    def __str__(self):
        return self.value

    def __eq__(self, other):
        return self.level == other.level and self.number == other.number

    def __lt__(self, other):
        if self.level and not other.level:
            return True
        elif not self.level:
            return False
        elif self.level != other.level:
            return self.level < other.level
        elif self.level == RankTableItem.LEVELDICT['k']:
            return self.number < other.number
        else:
            return self.number > other.number


@total_ordering
class StringTableItem(QTableWidgetItem):
    def __init__(self, value, *args, **kwargs):
        locale_name = "sv_SE.UTF-8"
        try:
            locale.setlocale(locale.LC_ALL, locale_name)
        except locale.Error:
            logging.warning('Could not set locale {0}. Using system '
                            'default.'.format(locale_name))
        super(StringTableItem, self).__init__(value, *args, **kwargs)
        self.value = value

    def __unicode__(self):
        return self.value

    def __str__(self):
        return self.value.encode('ascii', errors='egd')

    def __eq__(self, other):
        return locale.strcoll(self.value, other.value) == 0

    def __lt__(self, other):
        return locale.strcoll(self.value, other.value) < 0


class PlayerTab(QWidget):

    def __init__(self, tournament, parent=None):
        QWidget.__init__(self, parent)
        self.tournament = tournament
        self._editedPlayers = set()
        self._adding_player = False

        self.ui = Ui_PlayerTab()
        self.ui.setupUi(self)

        self.ui.player_fields = {}

        for (i, field) in enumerate(self.tournament.config['player_fields']):
            if field.datatype == 'text':
                fieldWidget = PlayerFieldLineEdit()
            elif field.datatype == 'rank':
                fieldWidget = RankSpinBox()
            self.ui.player_fields[field.name] = fieldWidget
            self.ui.player_edit_layout.insertRow(i, QLabel(field.name), 
                                                 fieldWidget)

        self.update()

        self.ui.tableWidget.verticalHeader().hide()
        self.ui.tableWidget.resizeColumnsToContents()
        self.ui.tableWidget.horizontalHeader().setStretchLastSection(True)

        self.ui.tableWidget.itemSelectionChanged.connect(self.players_selected)
        self.ui.add_player.clicked.connect(self.add_player_clicked)
        self.ui.delete_player.clicked.connect(self.delete_player_clicked)
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

                if cell_value is None:
                    cell_value = u''

                datatype = None
                for field in self.tournament.config['player_fields']:
                    if field.name == col_name:
                        datatype = field.datatype

                if datatype == 'text':
                    QTableWidgetItemClass = StringTableItem
                elif datatype == 'bool':
                    QTableWidgetItemClass = BoolTableItem
                elif datatype == 'rank':
                    QTableWidgetItemClass = RankTableItem
                else:
                    QTableWidgetItemClass = QTableWidgetItem
                    logging.warning('Using default QTableWidgetItemClass!')

                tableWidget.setItem(
                        i, col_index, QTableWidgetItemClass(cell_value))

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
                    logging.error('player {0} does not exist in '
                           'database!').format(edited_player.player_index)
                    self._editedPlayers = set()
                    return

            if not selectedPlayers:
                self.clear_edited_players()
                return
            elif self._editedPlayers:
                pass
            elif self._adding_player:
                self._adding_player = False
                self.update()

            self._editedPlayers = selectedPlayers

            for selectedPlayer in selectedPlayers:
                for field in self.tournament.config['player_fields']:
                    self.ui.player_fields[field.name].setDBValue(
                        selectedPlayer[field.name])
                break

    def clear_edited_players(self):
        self._editedPlayers = set()
        if self._adding_player:
            self._adding_player = False
            self.update()
        for field in self.tournament.config['player_fields']:
            self.ui.player_fields[field.name].clear()

        tableWidget = self.ui.tableWidget
        selected_ranges = tableWidget.selectedRanges()
        tableWidget.blockSignals(True)
        for selected_range in selected_ranges:
            tableWidget.setRangeSelected(selected_range, False)
        tableWidget.blockSignals(False)

    def save_edited_players(self):
        if self._adding_player:
            params = {}
            for field in self.tournament.config['player_fields']:
                params[field.name] = self.ui.player_fields[field.name].getDBValue()
            player = self.tournament.add_player(params)
            self._editedPlayers.add(player)

        for edited_player in self._editedPlayers:
            for field in self.tournament.config['player_fields']:
                edited_player[field.name] = self.ui.player_fields[field.name].getDBValue()

        #NB: The set is invalid because hashes have changed. Clearing will take
        #    care of it. So no worries.
        self.clear_edited_players()
    
    def delete_player_clicked(self):
        for edited_player in self._editedPlayers:
            self.tournament.remove_player(edited_player)
        self.clear_edited_players()
        self.update()

    def add_player_clicked(self):
        self.clear_edited_players()
        self._adding_player = True
        self.update()
