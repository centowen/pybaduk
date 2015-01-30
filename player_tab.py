# The GNU General Public License is a free, copyleft license for
# software and other kinds of works.
#
# The licenses for most software and other practical works are designed
# to take away your freedom to share and change the works. By contrast,
# the GNU General Public License is intended to guarantee your freedom
# to share and change all versions of a program--to make sure it remains
# free software for all its users. We, the Free Software Foundation, use
# the GNU General Public License for most of our software; it applies
# also to any other work released this way by its authors. You can apply
# it to your programs, too.
#
# When we speak of free software, we are referring to freedom, not
# price. Our General Public Licenses are designed to make sure that you
# have the freedom to distribute copies of free software (and charge for
# them if you wish), that you receive source code or can get it if you
# want it, that you can change the software or use pieces of it in new
# free programs, and that you know you can do these things.
#
# To protect your rights, we need to prevent others from denying you
# these rights or asking you to surrender the rights. Therefore, you
# have certain responsibilities if you distribute copies of the
# software, or if you modify it: responsibilities to respect the freedom
# of others.
#
# For example, if you distribute copies of such a program, whether
# gratis or for a fee, you must pass on to the recipients the same
# freedoms that you received. You must make sure that they, too, receive
# or can get the source code. And you must show them these terms so they
# know their rights.
#
# Developers that use the GNU GPL protect your rights with two steps:
# (1) assert copyright on the software, and (2) offer you this License
# giving you legal permission to copy, distribute and/or modify it.
#
# For the developers' and authors' protection, the GPL clearly explains
# that there is no warranty for this free software. For both users' and
# authors' sake, the GPL requires that modified versions be marked as
# changed, so that their problems will not be attributed erroneously to
# authors of previous versions.
#
# Some devices are designed to deny users access to install or run
# modified versions of the software inside them, although the
# manufacturer can do so. This is fundamentally incompatible with the
# aim of protecting users' freedom to change the software. The
# systematic pattern of such abuse occurs in the area of products for
# individuals to use, which is precisely where it is most unacceptable.
# Therefore, we have designed this version of the GPL to prohibit the
# practice for those products. If such problems arise substantially in
# other domains, we stand ready to extend this provision to those
# domains in future versions of the GPL, as needed to protect the
# freedom of users.
#
# Finally, every program is threatened constantly by software patents.
# States should not allow patents to restrict development and use of
# software on general-purpose computers, but in those that do, we wish
# to avoid the special danger that patents applied to a free program
# could make it effectively proprietary. To prevent this, the GPL
# assures that patents cannot be used to render the program non-free.
#
# The precise terms and conditions for copying, distribution and
# modification follow.
import re

from PyQt4.QtCore import QAbstractTableModel, Qt, QModelIndex
from PyQt4.QtGui import (QWidget, QTableWidgetItem,
                         QSpinBox, QValidator, QLabel, QLineEdit,
                         QItemSelectionModel, QShortcut)

from player_tab_ui import Ui_PlayerTab
from sort_model import SortModel
from pybaduk_qt import GET_UNFORMATTED_ROLE, GET_INDEX_ROLE


class EditState(object):
    def __init__(self):
        self.players = set()
        self.adding_player = False


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
        self.acceptable_rank = re.compile(r'([0-9]+)\s*([k|d|p]).*',
                                          flags=re.IGNORECASE)
        self.intermediate_rank = re.compile(r'([0-9]+)\s*',
                                            flags=re.IGNORECASE)

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
        if self.value() != RankSpinBox._minvalue:
            return self.textFromValue(self.value())
        else:
            return None

    def clear(self):
        self.setValue(RankSpinBox._minvalue)


class BoolTableItem(QTableWidgetItem):
    def __init__(self, value, *args, **kwargs):
        if value:
            self.name = 'Yes'
        else:
            self.name = 'No'
        super(BoolTableItem, self).__init__(self.name, *args, **kwargs)


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
        # TODO : adding player?
        return len(self._players)

    def data(self, qt_index, role=Qt.DisplayRole):
        if not qt_index.isValid():
            return None

        row = qt_index.row()
        col = qt_index.column()
        if role == Qt.DisplayRole:
            return unicode(self._players[row][self._fields[col].name])
        elif role == GET_UNFORMATTED_ROLE:
            return self._players[row][self._fields[col].name]
        elif role == GET_INDEX_ROLE:
            return self._players[row].player_index


class PlayerTab(QWidget):

    def __init__(self, tournament, parent=None):
        QWidget.__init__(self, parent)
        self._tournament = tournament
        self._edit_state = EditState()
        self.player_model = PlayerTableModel(
            self._tournament.players, self._tournament.config['player_fields'])
        self.sorted_model = SortModel()
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

        self.update_player_count()

        return_shortcut = QShortcut(
            Qt.Key_Return, self.ui.player_edit_box)
        return_shortcut.setContext(Qt.WidgetWithChildrenShortcut)
        return_shortcut.activated.connect(self.save_edited_players)
        self.ui.player_list.verticalHeader().hide()
        self.ui.player_list.resizeColumnsToContents()
        self.ui.player_list.horizontalHeader().setStretchLastSection(True)
        self.ui.player_list.setModel(self.sorted_model)
        self.ui.player_list.selectionModel().selectionChanged.connect(
            self.players_selected)
        self.player_model.layoutChanged.connect(self.update_player_count)
        self.player_model.modelReset.connect(self.update_player_count)
        self.ui.add_player.clicked.connect(self.add_player_clicked)
        self.ui.delete_player.clicked.connect(self.delete_player_clicked)
        self.ui.ok_cancel.rejected.connect(self.clear_edited_players)
        self.ui.ok_cancel.accepted.connect(self.save_edited_players)
        self.ui.filter_edit.textChanged.connect(
            self.sorted_model.setFilterRegExp)

    def update_player_count(self):
        new_count = self.player_model.rowCount(QModelIndex())
        self.ui.player_count.setText(
            u"Registered: {}\nPreliminary: {}".format(0, new_count))

    def get_player_at_row(self, index):
        player_index = str(self.sorted_model.data(index, GET_INDEX_ROLE))
        player_index = player_index.toString()
        return self._tournament.players[player_index]

    def update_player_model(self):
        self.player_model.beginResetModel()
        self.player_model.update_data(
            self._tournament.players, self._tournament.config['player_fields'])
        self.player_model.endResetModel()

    def players_selected(self, selected, deselected):
        selected = [i for i in selected.indexes() if i.column() == 0]
        deselected = [i for i in deselected.indexes() if i.column() == 0]

        for index in selected:
            self._edit_state.players.add(self.get_player_at_row(index))

        for index in deselected:
            player = self.get_player_at_row(index)
            try:
                self._edit_state.players.remove(player)
            except KeyError:
                pass

        if self._edit_state.players:
            for player in self._edit_state.players:
                for field in self._tournament.config['player_fields']:
                    self._player_fields[field.name].set_db_value(
                        player[field.name])
                # Here should be fancy code to handle multi edit.
                break
        else:
            for field in self._tournament.config['player_fields']:
                self._player_fields[field.name].clear()

    def clear_edited_players(self):
        # if self._adding_player:
        #     self._adding_player = False
        self._edit_state.players.clear()
        self.ui.player_list.selectionModel().select(
            QModelIndex(), QItemSelectionModel.Clear)

    def save_edited_players(self):
        # if self._adding_player:
        #     params = {}
        #     for field in self._tournament.config['player_fields']:
        #         params[field.name] = self._player_fields[field.name].get_db_value()
        #     player = self._tournament.add_player(params)
        #     self._edited_players.add(player)

        for edited_player in self._edit_state.players:
            for field in self._tournament.config['player_fields']:
                edited_player[field.name] = self._player_fields[field.name].get_db_value()

        self.clear_edited_players()
        self.update_player_model()

    def delete_player_clicked(self):
        for edited_player in self._edit_state.players:
            self._tournament.remove_player(edited_player)
        self.clear_edited_players()
        self.update_player_model()

    def add_player_clicked(self):
        self.clear_edited_players()
        self._edit_state.adding_player = True
        self.update()
