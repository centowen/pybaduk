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
from PyQt4.QtCore import QAbstractTableModel, Qt, QModelIndex
from PyQt4.QtGui import (QWidget, QLabel, QLineEdit, QItemSelectionModel)

from pairing_tab_ui import Ui_PairingTab
from pybaduk_qt import GET_UNFORMATTED_ROLE, GET_INDEX_ROLE
from sort_model import SortModel


class EditState(object):
    def __init__(self):
        self.pairings = set()
        self.adding_pairing = False


class PairingFieldLineEdit(QLineEdit):
    def get_db_value(self):
        return unicode(self.text())

    def set_db_value(self, db_value):
        if db_value is None:
            db_value = ''
        # This isn't right.
        self.setText(unicode(db_value))

    def clear(self):
        self.setText('')


class PairingTableModel(QAbstractTableModel):
    def __init__(self, pairings, fields):
        QAbstractTableModel.__init__(self)
        self._pairings = None
        self._fields = None

        self.update_data(pairings, fields)

    def get_column_type(self, column):
        return self._fields[column].datatype

    def update_data(self, pairings, fields):
        self._pairings = list(pairings)
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
        return len(self._pairings)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        row = index.row()
        col = index.column()
        if role == Qt.DisplayRole:
            return unicode(self._pairings[row][self._fields[col].name])
        elif role == GET_UNFORMATTED_ROLE:
            return self._pairings[row][self._fields[col].name]
        elif role == GET_INDEX_ROLE:
            return self._pairings[row].pairing_index


class PairingTab(QWidget):
    def __init__(self, tournament, parent=None):
        QWidget.__init__(self, parent)
        self._tournament = tournament
        self._edit_state = EditState()
        self.pairing_model = PairingTableModel(
            self._tournament.pairings,
            self._tournament.config['pairing_fields'])
        self.sorted_model = SortModel()
        self.sorted_model.setSourceModel(self.pairing_model)

        self.ui = Ui_PairingTab()
        self.ui.setupUi(self)

        self._pairing_fields = {}

        for (i, field) in enumerate(self._tournament.config['pairing_fields']):
            field_widget = PairingFieldLineEdit()
            self._pairing_fields[field.name] = field_widget
            self.ui.pairing_edit_layout.insertRow(
                i, QLabel(field.name), field_widget)

        self.ui.pairing_list.verticalHeader().hide()
        self.ui.pairing_list.resizeColumnsToContents()
        self.ui.pairing_list.horizontalHeader().setStretchLastSection(True)
        self.ui.pairing_list.setModel(self.sorted_model)
        self.ui.pairing_list.selectionModel().selectionChanged.connect(
            self.pairings_selected)
        self.ui.delete_pairing.clicked.connect(self.delete_pairing_clicked)
        self.ui.filter_edit.textChanged.connect(
            self.sorted_model.setFilterRegExp)

    def get_pairing_at_row(self, index):
        pairing_index = str(
            self.sorted_model.data(index, GET_INDEX_ROLE).toString())
        return self._tournament.pairings[pairing_index]

    def pairings_selected(self, selected, deselected):
        selected = [i for i in selected.indexes() if i.column() == 0]
        deselected = [i for i in deselected.indexes() if i.column() == 0]

        for index in selected:
            self._edit_state.pairings.add(self.get_pairing_at_row(index))

        for index in deselected:
            pairing = self.get_pairing_at_row(index)
            try:
                self._edit_state.pairings.remove(pairing)
            except KeyError:
                pass

        if self._edit_state.pairings:
            for pairing in self._edit_state.pairings:
                for field in self._tournament.config['pairing_fields']:
                    self._pairing_fields[field.name].set_db_value(
                        pairing[field.name])
                # Here should be fancy code to handle multi edit.
                break
        else:
            for field in self._tournament.config['pairing_fields']:
                self._pairing_fields[field.name].clear()

    def update_pairing_model(self):
        self.pairing_model.beginResetModel()
        self.pairing_model.update_data(
            self._tournament.pairings,
            self._tournament.config['pairing_fields'])
        self.pairing_model.endResetModel()

    def clear_edited_pairings(self):
        # if self._adding_player:
        #     self._adding_player = False
        self._edit_state.pairings.clear()
        self.ui.pairing_list.selectionModel().select(
            QModelIndex(), QItemSelectionModel.Clear)

    def delete_pairing_clicked(self):
        for edited_pairing in self._edit_state.pairings:
            self._tournament.remove_pairing(edited_pairing)
        self.clear_edited_pairings()
        self.update_pairing_model()
