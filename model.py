#!/usr/bin/python3
# -*- coding: utf-8 -*-

import collections
import logging
from lxml import etree
from PyQt5 import QtCore


class MatchsettingsTableModel(QtCore.QAbstractTableModel):
    dataChanged = QtCore.pyqtSignal(QtCore.QModelIndex, QtCore.QModelIndex)

    def __init__(self, parent=None, root_path='.', matchsettings_path='matchsettings.txt'):
        super(MatchsettingsTableModel, self).__init__(parent)
        self._data = {}
        self._matchsettings_path = matchsettings_path
        self._root_path = root_path
        self._column_ids = {
            'id': {
                'position': 0,
                'enabled': True,
                'editable': False
            },
            'challenge': {
                'position': 1,
                'enabled': True,
                'editable': False
            },
            'status': {
                'position': 2,
                'enabled': True,
                'editable': True
            },
            'path': {
                'position': 3,
                'enabled': False,
                'editable': False
            }
        }

    @property
    def matchsettings_path(self):
        return self._matchsettings_path

    # redefinition of QtCore.QAbstractTableModel methods
    def rowCount(self, parent=None, *args, **kwargs):
        return 0 if (parent and parent.isValid()) else len(self._data)

    def columnCount(self, parent=None, *args, **kwargs):
        cc = 0
        for k, v in self._column_ids.items():
            if v['enabled']:
                cc += 1
        return cc

    def headerData(self, section, orientation, role=None):
        if role != QtCore.Qt.DisplayRole:
            return QtCore.QVariant()
        if orientation == QtCore.Qt.Horizontal:
            if section == self._column_ids['id']['position']:
                return QtCore.QVariant("Id")
            if section == self._column_ids['challenge']['position']:
                return QtCore.QVariant("Challenge")
            elif section == self._column_ids['status']['position']:
                return QtCore.QVariant("Status")
        return QtCore.QVariant()

    def setData(self, index: QtCore.QModelIndex, v: QtCore.QVariant, role=None):
        if index.isValid() and role == QtCore.Qt.EditRole:
            row = index.row()
            column = index.column()
            value = v.value()
            logging.debug('updating (row={}, column={}) with value => {}'.format(row, column, value))
            if column == self._column_ids['challenge']['position']:  # challenge
                if self._data.get(row):  # already existing challenge
                    self._data[row].update({'challenge': value})
                else:  # new challenge
                    self._data[row] = {'challenge': value, 'status': False}
            elif column == self._column_ids['status']['position']:  # status
                if self._data.get(row):  # already existing challenge
                    self._data[row].update({'status': value})
                else:  # new status
                    self._data[row] = {'challenge': '', 'status': value}
            else:
                logging.warning('unmapped column {}'.format(column))
                return False  # unmapped column
            self.dataChanged.emit(index, index)
            return True  # all is well
        return False  # index is not valid or role is not QtCore.Qt.EditRole

    @property
    def internal_data(self):
        return self._data

    def data(self, index: QtCore.QModelIndex, role=None):
        if role == QtCore.Qt.DisplayRole:
            row = index.row()
            column = index.column()
            if column == self._column_ids['id']['position']:  # id
                return QtCore.QVariant(row) if row in self._data.keys() else QtCore.QVariant()
            if column == self._column_ids['challenge']['position']:  # challenge
                if self._data.get(row):
                    return QtCore.QVariant(self._data[row]['challenge'])
            elif column == self._column_ids['status']['position']:  # status
                if self._data.get(row):
                    return QtCore.QVariant(self._data[row]['status'])
        return QtCore.QVariant()

    def flags(self, index: QtCore.QModelIndex):
        _flags = 0
        column = None
        for k, v in self._column_ids.items():
            if v['position'] == index.column():
                column = v
        if column and index.column() == column['position'] and column['editable']:  # column is editable
            _flags = QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsSelectable
        return super(MatchsettingsTableModel, self).flags(index) | _flags

    def insertRows(self, row, count, parent=None):
        logging.info('inserting rows from {} to {}'.format(row, row + count))
        self.beginInsertRows(QtCore.QModelIndex(), row, row + count)
        if self._data.get(row):  # starting row already exists...
            operation_result = False  # only allow to append new rows
            logging.error('operation failed: starting row already exists {}'.format(self._data[row]))
        else:  # new rows
            for i in range(row, row + count):
                self._data[i] = {'challenge': '', 'status': False}
                logging.info('added: row={} data={}'.format(i, self._data[i]))
            operation_result = True
        self.endInsertRows()
        return operation_result

    def removeRows(self, row, count, parent=None):
        logging.info('removing rows from {} to {}'.format(row, row + count - 1))
        self.beginRemoveRows(QtCore.QModelIndex(), row, row + count)
        if self._data.get(row):  # starting row exists
            for i in range(row, row + count):
                logging.info('removed: row={} data={}'.format(i, self._data[i]))
                self._data.pop(i)
            # the dictionary is dirty - need to shift all rows inside it by row + count, starting from row
            j = 0
            for i in range(row + count, list(self._data.keys())[-1] + 1):  # start from the last removed element
                if self._data.get(i):  # element exists, go on
                    new_row = row + j
                    logging.info('moving: data={} from {} to {}'.format(self._data[i], i, new_row))
                    self._data[new_row] = self._data.pop(i)
                    j += 1
                else:
                    break  # no more elements, stop the cycle
            operation_result = True
        else:  # does not exist
            logging.info('operation failed: starting row={} does not exist'.format(row))
            operation_result = False
        self.endRemoveRows()
        return operation_result

    def insertColumns(self, column, count, parent=None):
        self.beginInsertColumns()
        logging.error('not implemented')
        self.endInsertColumns()
        return False

    def removeColumns(self, column, count, parent=None):
        self.beginRemoveColumns()
        logging.error('not implemented')
        self.endRemoveColumns()
        return False

    def read_matchsettings(self):
        logging.debug('reading matchsettings file')
        with open(self._matchsettings_path, 'r') as f:
            tree = etree.parse(f)
            row = 0
            for k, v in self._get_challenges(tree, '/playlist//challenge'):
                self._data[row] = {'challenge': k, 'status': v, 'path': ''}
                row += 1
            for k, v in self._get_challenges(tree, '/playlist//comment()'):
                self._data[row] = {'challenge': k, 'status': v, 'path': ''}
                row += 1
            i1 = self.createIndex(0, 0)
            i2 = self.createIndex(1, row)
            self.dataChanged.emit(i1, i2)
            logging.debug(['{}: {}'.format(k, v) for k, v in self._data.items()])
        logging.debug('finished reading matchsettings file')

    def _get_challenges(self, tree, query):
        assert 'challenge' or 'comment()' in query
        for e in tree.xpath(query):
            if 'comment()' in query:
                e = etree.fromstring(e.text.replace('<!--', '').replace('-->', ''))
            for c in list(e):
                if c.tag == 'file':
                    yield c.text, 'comment()' not in query

    def save_matchsettings(self):
        logging.debug('saving matchsettings file')
        with open(self._matchsettings_path, 'r+') as f:
            tree = etree.parse(f)
            for e in tree.xpath('/playlist//challenge'):
                e.getparent().remove(e)
            for e in tree.xpath('/playlist//comment()'):
                e.getparent().remove(e)

            playlist = self._tree.xpath('/playlist')

            for k, v in self._matchsettings.items():
                challenge = etree.Element('challenge')
                file = etree.Element('file')
                file.text = k
                challenge.append(file)
                if v:  # enabled challenge
                    playlist.append(challenge)
                else:  # disabled challenge
                    commented_challenge = etree.Comment('<!-- {} -->'.format(etree.tostring(challenge)))
                    playlist.append(commented_challenge)

            xml = etree.tostring(self._tree, pretty_print=True, xml_declaration=True)
            f.writelines(xml)
