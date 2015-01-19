import locale
import logging

from PyQt4.QtCore import QAbstractTableModel, Qt, QModelIndex, QVariant, \
    QRegExp
from PyQt4.QtGui import (QWidget, QTableWidgetItem,
                         QSpinBox, QValidator, QLabel, QLineEdit,
                         QSortFilterProxyModel, QItemSelectionModel,
                         QShortcut)

from pybaduk_qt import GET_UNFORMATTED_ROLE, GET_INDEX_ROLE


class SortModel(QSortFilterProxyModel):
    LEVELDICT = {'p': 1, 'd': 2, 'k': 3}

    def __init__(self, *args, **kwargs):
        super(SortModel, self).__init__(*args, **kwargs)

        self.setDynamicSortFilter(True)
        self.setFilterCaseSensitivity(Qt.CaseInsensitive)

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

    def filterAcceptsRow(self, source_row, source_parent):
        index0 = self.sourceModel().index(source_row, 0, source_parent)

        regexp = self.filterRegExp()
        return regexp.indexIn(self.sourceModel().data(index0)) != -1 or
                regexp.indexIn(self.sourceModel().data(index1)) != -1)

    def _text_less_than(self, data1, data2):
        return locale.strcoll(data1, data2) < 0

    def _rank_to_level_and_value(self, rank):
        if not rank:
            level = None
            number = None
        else:
            try:
                level = SortModel.LEVELDICT[rank[-1]]
                number = int(rank[:-1])
            except (KeyError, ValueError):
                logging.error('Invalid rank: {0}'.format(rank))
                level = None
                number = None
        return level, number

    def _player_less_than(self, player1, player2):
        return self._rank_less_than(player1[u'Rank'], player2[u'Rank'])

    def _rank_less_than(self, rank1, rank2):
        rank1_level, rank1_number = self._rank_to_level_and_value(rank1)
        rank2_level, rank2_number = self._rank_to_level_and_value(rank2)
        if rank1_level and not rank2_level:
            return True
        elif not rank1_level:
            return False
        elif rank1_level != rank2_level:
            return rank1_level < rank2_level
        elif rank1_level == SortModel.LEVELDICT['k']:
            return rank1_number < rank2_number
        else:
            return rank1_number > rank2_number

    def lessThan(self, index1, index2):
        field_type = self.sourceModel().get_column_type(index1.column())
        data1 = self.sourceModel().data(index1, GET_UNFORMATTED_ROLE)
        data2 = self.sourceModel().data(index2, GET_UNFORMATTED_ROLE)
        if field_type == 'text':
            return self._text_less_than(data1, data2)
        elif field_type == 'player':
            return self._player_less_than(data1, data2)
        elif field_type == 'rank':
            return self._rank_less_than(data1, data2)
        else:
            logging.warning('Don\'t know how to sort field type {}.'.format(field_type))
            return data1 < data2


