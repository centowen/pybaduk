from PyQt4.QtCore import QAbstractTableModel, Qt
from PyQt4.QtGui import (QWidget, QLabel, QLineEdit)

from pairing_tab_ui import Ui_PairingTab


GET_UNFORMATTED_ROLE = Qt.UserRole
GET_PAIRING_ROLE = Qt.UserRole + 1


class PairingFieldLineEdit(QLineEdit):
    def get_db_value(self):
        return unicode(self.text())

    def set_db_value(self, db_value):
        if db_value is None:
            db_value = ''
        self.setText(db_value)

    def clear(self):
        self.setText('')


class PairingTableModel(QAbstractTableModel):
    def __init__(self, pairings, fields):
        QAbstractTableModel.__init__(self)
        self._pairings = None
        self._field = None

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

    def data(self, index, role):
        if not index.isValid():
            return None

        row = index.row()
        col = index.column()
        if role == Qt.DisplayRole:
            return unicode(self._pairings[row][self._fields[col].name])
        elif role == GET_UNFORMATTED_ROLE:
            return self._pairings[row][self._fields[col].name]
        elif role == GET_PAIRING_ROLE:
            return self._pairings[row].pairing_index


class PairingTab(QWidget):
    def __init__(self, tournament, parent=None):
        QWidget.__init__(self, parent)
        self._tournament = tournament
        self.pairing_model = PairingTableModel(
            self._tournament.pairings, self._tournament.config['pairing_fields'])

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
        self.ui.pairing_list.setModel(self.pairing_model)