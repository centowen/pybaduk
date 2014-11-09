from functools import total_ordering
import locale
import logging
import re

from PyQt4.QtCore import QAbstractTableModel, Qt
from PyQt4.QtGui import (QWidget, QTableWidgetItem,
                         QSpinBox, QValidator, QLabel, QLineEdit,
                         QSortFilterProxyModel)

from player_tab_ui import Ui_PlayerTab


class PlayerFieldLineEdit(QLineEdit):

    def get_db_value(self):
        return unicode(self.text())

    def set_db_value(self, db_value):
        if db_value is None:
            db_value = ''
        self.setText(db_value)

    def clear(self):
        self.setText('')


class RankSpinBox(QSpinBox):

    _minvalue = -50
    _maxvalue = 18

    def __init__(self, *args, **kwargs):
        super(RankSpinBox, self).__init__(*args, **kwargs)
        self.setMinimum(RankSpinBox._minvalue)
        self.setMaximum(RankSpinBox._maxvalue)
        self.acceptable_rank = re.compile(r'([0-9]+)\s*([k|d|p]).*', flags=re.IGNORECASE)
        self.intermediate_rank = re.compile(r'([0-9]+)\s*', flags=re.IGNORECASE)

    def validate(self, text, pos):
        if self.acceptable_rank.match(text) or text == '' or text == 'No rank':
            return QValidator.Acceptable, pos
        elif self.intermediate_rank.match(text):
            return QValidator.Intermediate, pos
        else:
            return QValidator.Invalid, pos

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

    def set_db_value(self, db_value):
        self.setValue(self.valueFromText(db_value))

    def get_db_value(self):
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


class SortPlayers(QSortFilterProxyModel):
    LEVELDICT = {'p': 1, 'd': 2, 'k': 3}
    def __init__(self, *args, **kwargs):
        super(SortPlayers, self).__init__(*args, **kwargs)

        locale_name = "sv_SE.UTF-8"
        try:
            locale.setlocale(locale.LC_ALL, locale_name)
        except locale.Error:
            # TODO: Ugh... ugly workaround:
            try:
                locale.setlocale(locale.LC_ALL, 'swedish')
            except locale.Error:
                logging.warning('Could not set locale {0}. Using system '
                                'default.'.format(locale_name))
        print(locale)

    def _text_less_than(self, data1, data2):
        return locale.strcoll(data1, data2) < 0

    def _rank_to_level_and_value(self, rank):
        if not rank:
            level = None
            number = None
        else:
            try:
                level = SortPlayers.LEVELDICT[rank[-1]]
                number = int(rank[:-1])
            except (KeyError, ValueError):
                logging.error('Invalid rank: {0}'.format(rank))
                level = None
                number = None
        return level, number

    def _rank_less_than(self, rank1, rank2):
        rank1_level, rank1_number = self._rank_to_level_and_value(rank1)
        rank2_level, rank2_number = self._rank_to_level_and_value(rank2)
        if rank1_level and not rank2_level:
            return True
        elif not rank1_level:
            return False
        elif rank1_level != rank2_level:
            return rank1_level < rank2_level
        elif rank1_level == RankTableItem.LEVELDICT['k']:
            return rank1_number < rank2_number
        else:
            return rank1_number > rank2_number

    def lessThan(self, index1, index2):
        field_type = self.sourceModel().get_column_type(index1.column())
        data1 = self.sourceModel().data(index1, Qt.UserRole)
        data2 = self.sourceModel().data(index2, Qt.UserRole)
        if field_type == 'text':
            return self._text_less_than(data1, data2)
        elif field_type == 'rank':
            return self._rank_less_than(data1, data2)
        else:
            logging.warning('Don\'t know how to sort field type {}.'.format(field_type))
            return data1 < data2


class PlayerTableModel(QAbstractTableModel):
    """
    A model containing players. Will only update_data when :meth:`update_data`
    is called.
    """

    def __init__(self, players, fields):
        QAbstractTableModel.__init__(self)
        self._players = None
        self._fields = None
        self.update_data(players, fields)

    def get_column_type(self, column):
        return self._fields[column].datatype

    def update_data(self, players, fields):
        self._players = list(players)
        self._fields = [field for field in fields if field.visible]

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self._fields[section].name

    def columnCount(self, parent):
        if parent.isValid():
            return 0
        return len(self._fields)

    def rowCount(self, parent):
        if parent.isValid():
            return 0
        # TODO : editing?
        return len(self._players)

    def data(self, index, role):
        if not index.isValid():
            return None

        row = index.row()
        col = index.column()
        if role == Qt.DisplayRole:
            return unicode(self._players[row][self._fields[col].name])
        elif role == Qt.UserRole:
            return self._players[row][self._fields[col].name]


class PlayerTab(QWidget):

    def __init__(self, tournament, parent=None):
        QWidget.__init__(self, parent)
        self._tournament = tournament
        self._edited_players = set()
        self._adding_player = False
        self.player_model = PlayerTableModel(
            self._tournament.players, self._tournament.config['player_fields'])
        self.sorted_model = SortPlayers()
        self.sorted_model.setSourceModel(self.player_model)

        self.ui = Ui_PlayerTab()
        self.ui.setupUi(self)

        self._player_fields = {}

        for (i, field) in enumerate(self._tournament.config['player_fields']):
            if field.datatype == 'rank':
                field_widget = RankSpinBox()
            else:  # Default treatment as text string.
                field_widget = PlayerFieldLineEdit()
            self._player_fields[field.name] = field_widget
            self.ui.player_edit_layout.insertRow(
                i, QLabel(field.name), field_widget)

        self.ui.table_widget.verticalHeader().hide()
        self.ui.table_widget.resizeColumnsToContents()
        self.ui.table_widget.horizontalHeader().setStretchLastSection(True)
        self.ui.table_widget.setModel(self.sorted_model)

        # self.ui.table_widget.itemSelectionChanged.connect(self.players_selected)
        self.ui.add_player.clicked.connect(self.add_player_clicked)
        self.ui.delete_player.clicked.connect(self.delete_player_clicked)
        self.ui.ok_cancel.rejected.connect(self.clear_edited_players)
        self.ui.ok_cancel.accepted.connect(self.save_edited_players)

    def player_at_row(self, row):
        """Retrieve player object from row number."""
        player_index = str(self.ui.table_widget.item(row, 0).text())
        return self._tournament.players[player_index]

    # def update_data(self):
    #     """Update GUI from underlying data model."""
    #     table_widget = self.ui.table_widget
    #     table_widget.setSortingEnabled(False)
    #
    #     selected_items = table_widget.selectedItems()
    #     selected_rows = set([item.row() for item in selected_items])
    #     selected_players = [self.player_at_row(row) for row in selected_rows]
    #
    #     table_widget.blockSignals(True)
    #     table_widget.clear()
    #     table_widget.blockSignals(False)
    #     row_count = len(self.tournament.players)
    #     if self._adding_player:
    #         row_count += 1
    #     table_widget.setRowCount(row_count)
    #
    #     table_header = ['player_index']
    #     for field in self.tournament.config['player_fields']:
    #         if field.visible:
    #             table_header.append(field.name)
    #
    #     # Add player index as column zero but don't show it.
    #     table_widget.setColumnCount(len(table_header))
    #     table_widget.setHorizontalHeaderLabels(table_header)
    #     table_widget.setColumnHidden(0, True)
    #
    #     for i, player in enumerate(self.tournament.players):
    #         for col_index, col_name in enumerate(table_header):
    #             if col_index == 0:
    #                 cell_value = player.player_index
    #             else:
    #                 cell_value = player[col_name]
    #
    #             if cell_value is None:
    #                 cell_value = u''
    #
    #             datatype = None
    #             for field in self.tournament.config['player_fields']:
    #                 if field.name == col_name:
    #                     datatype = field.datatype
    #
    #             if datatype == 'text':
    #                 item_class = StringTableItem
    #             elif datatype == 'bool':
    #                 item_class = BoolTableItem
    #             elif datatype == 'rank':
    #                 item_class = RankTableItem
    #             else:
    #                 item_class = QTableWidgetItem
    #                 logging.warning('Using default item_class!')
    #
    #             table_widget.setItem(i, col_index, item_class(cell_value))
    #
    #         if player in selected_players and not self._adding_player:
    #             selection_range = QTableWidgetSelectionRange(
    #                 i, 0, i, table_widget.columnCount() - 1)
    #             table_widget.blockSignals(True)
    #             table_widget.setRangeSelected(selection_range, True)
    #             table_widget.blockSignals(False)
    #
    #     if self._adding_player:
    #         table_widget.blockSignals(True)
    #         selection_range = QTableWidgetSelectionRange(
    #             row_count - 1, 0, row_count - 1, table_widget.columnCount() - 1)
    #         table_widget.setRangeSelected(selection_range, True)
    #         table_widget.blockSignals(False)
    #
    #     table_widget.setSortingEnabled(True)
    #     #table_widget.setCurrentCell(currentRow, currentColumn)
    #     table_widget.itemSelectionChanged.emit()

    def players_selected(self):
        selected_items = self.ui.table_widget.selectedItems()
        selected_rows = set([item.row() for item in selected_items])
        selected_players = set([self.player_at_row(row) for row in selected_rows])

        if self._edited_players == selected_players:
            return
        else:
            for edited_player in self._edited_players:
                if edited_player not in self._tournament.players:
                    logging.error(
                        'player {0} does not exist in database!'.format(
                            edited_player.player_index))
                    self._edited_players = set()
                    return

            if not selected_players:
                self.clear_edited_players()
                return
            elif self._edited_players:
                pass
            elif self._adding_player:
                self._adding_player = False
                self.update()

            self._edited_players = selected_players

            for selectedPlayer in selected_players:
                for field in self._tournament.config['player_fields']:
                    self._player_fields[field.name].set_db_value(
                        selectedPlayer[field.name])
                break

    def clear_edited_players(self):
        self._edited_players = set()
        if self._adding_player:
            self._adding_player = False
            self.update()
        for field in self._tournament.config['player_fields']:
            self._player_fields[field.name].clear()

        table_widget = self.ui.table_widget
        selected_ranges = table_widget.selectedRanges()
        table_widget.blockSignals(True)
        for selected_range in selected_ranges:
            table_widget.setRangeSelected(selected_range, False)
        table_widget.blockSignals(False)

    def save_edited_players(self):
        if self._adding_player:
            params = {}
            for field in self._tournament.config['player_fields']:
                params[field.name] = self._player_fields[field.name].get_db_value()
            player = self._tournament.add_player(params)
            self._edited_players.add(player)

        for edited_player in self._edited_players:
            for field in self._tournament.config['player_fields']:
                edited_player[field.name] = self._player_fields[field.name].get_db_value()

        #NB: The set is invalid because hashes have changed. Clearing will take
        #    care of it. So no worries.
        self.clear_edited_players()
    
    def delete_player_clicked(self):
        for edited_player in self._edited_players:
            self._tournament.remove_player(edited_player)
        self.clear_edited_players()
        self.update()

    def add_player_clicked(self):
        self.clear_edited_players()
        self._adding_player = True
        self.update()
