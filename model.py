#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging
import shutil

from PyQt5 import QtCore
from lxml import etree


class MatchsettingsTableModel(QtCore.QAbstractTableModel):
    dataChanged = QtCore.pyqtSignal(QtCore.QModelIndex, QtCore.QModelIndex)

    def __init__(self, parent=None, root_path='.', matchsettings_path='matchsettings.txt'):
        super(MatchsettingsTableModel, self).__init__(parent)
        self._matchsettings_path = matchsettings_path
        self._root_path = root_path
        self._columns = {
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
        self._data = {}

    @property
    def matchsettings_path(self):
        return self._matchsettings_path

    '''
    todo: remove this, in favour of letting the view find data using a function rather than accessing data directly
    '''
    @property
    def internal_data(self):
        return self._data

    @property
    def internal_columns(self):
        return self._columns

    # redefinition of QtCore.QAbstractTableModel methods
    def rowCount(self, parent=None, *args, **kwargs):
        return 0 if (parent and parent.isValid()) else len(self._data)

    def columnCount(self, parent=None, *args, **kwargs):
        cc = 0
        for k, v in self._columns.items():
            if v['enabled']:
                cc += 1
        return cc

    def headerData(self, section, orientation, role=None):
        if role != QtCore.Qt.DisplayRole:
            return QtCore.QVariant()
        if orientation == QtCore.Qt.Horizontal:
            if section == self._columns['id']['position']:
                return QtCore.QVariant("Id")
            if section == self._columns['challenge']['position']:
                return QtCore.QVariant("Challenge")
            elif section == self._columns['status']['position']:
                return QtCore.QVariant("Status")

        return QtCore.QVariant()

    def setData(self, index: QtCore.QModelIndex, v: QtCore.QVariant, role=None):
        if index.isValid() and role == QtCore.Qt.EditRole:
            row = index.row()
            column = index.column()
            value = v.value()
            logging.debug('updating (row={}, column={}) with value => {}'.format(row, column, value))
            if column == self._columns['challenge']['position']:  # challenge
                self._update_or_insert_data(row, challenge=value)
            elif column == self._columns['status']['position']:  # status
                self._update_or_insert_data(row, status=value)
            else:
                logging.warning('unmapped column {}'.format(column))
                return False  # unmapped column
            self.dataChanged.emit(index, index)
            return True  # all is well
        return False  # index is not valid or role is not QtCore.Qt.EditRole

    def data(self, index: QtCore.QModelIndex, role=None):
        if role == QtCore.Qt.DisplayRole:
            row = index.row()
            column = index.column()
            if column == self._columns['id']['position']:  # id
                return QtCore.QVariant(row) if row in self._data.keys() else QtCore.QVariant()
            if column == self._columns['challenge']['position']:  # challenge
                if self._data.get(row):
                    return QtCore.QVariant(self._data[row]['challenge'])
            elif column == self._columns['status']['position']:  # status
                if self._data.get(row):
                    return QtCore.QVariant(self._data[row]['status'])
        return QtCore.QVariant()

    def flags(self, index: QtCore.QModelIndex):
        _flags = 0
        column = None
        for k, v in self._columns.items():
            if v['position'] == index.column():
                column = v
        if column and index.column() == column['position'] and column['editable']:  # column is editable
            _flags = QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsSelectable
        return super(MatchsettingsTableModel, self).flags(index) | _flags

    def insertRows(self, row, count, parent=None):
        logging.info('inserting rows from {} to {}'.format(row, row + count - 1))
        self.beginInsertRows(QtCore.QModelIndex(), row, row + count - 1)
        if self._data.get(row):  # starting row already exists...
            operation_result = False  # only allow to append new rows
            logging.error('operation failed: starting row already exists {}'.format(self._data[row]))
        else:  # new rows
            for i in range(row, row + count):
                self._update_or_insert_data(i, status=False)
                logging.info('added: row={} data={}'.format(i, self._data[i]))
            operation_result = True
        self.endInsertRows()
        return operation_result

    def removeRows(self, row, count, parent=None):
        logging.info('removing rows from {} to {}'.format(row, row + count - 1))
        self.beginRemoveRows(QtCore.QModelIndex(), row, row + count - 1)
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

    def create_index_for(self, row, column: str):
        if self._columns.get(column):
            c = self._columns[column]['position']
            return self.createIndex(row, c)
        return None

    def read_matchsettings(self):
        logging.info('reading matchsettings file')
        with open(self._matchsettings_path, 'r', encoding='utf-8') as f:
            tree = etree.parse(f)
            row = 0
            for c, i, s in self._get_challenges(tree, '/playlist//challenge'):
                self._update_or_insert_data(row, challenge=c, ident=i, status=s)
                row += 1
            for c, i, s in self._get_challenges(tree, '/playlist//comment()'):
                self._update_or_insert_data(row, challenge=c, ident=i, status=s)
                row += 1
            i1 = self.createIndex(0, 0)
            i2 = self.createIndex(1, row)
            self.dataChanged.emit(i1, i2)
            logging.debug(['{}: {}'.format(k, v) for k, v in self._data.items()])
        logging.debug('finished reading matchsettings file')

    def save_matchsettings(self):
        logging.info('saving matchsettings file')
        with open(self._matchsettings_path, 'r+b') as f:
            # backup the file before doing anything
            shutil.copy(src=self._matchsettings_path,
                        dst='{}.bak'.format(self._matchsettings_path))
            # go on - modify the file with new/commented challenges (if any)
            parser = etree.XMLParser(remove_blank_text=True)
            tree = etree.parse(f, parser)
            for e in tree.xpath('/playlist//challenge'):
                e.getparent().remove(e)
            for e in tree.xpath('/playlist//comment()'):
                e.getparent().remove(e)
            playlist = tree.xpath('/playlist')[0]  # there's only one playlist for matchsettings file
            for k, v in self._data.items():
                challenge = etree.Element('challenge')
                file = etree.Element('file')
                file.text = v['challenge']
                challenge.append(file)
                if v['ident'] and '' not in v['ident']:  # valid ident
                    ident = etree.Element('ident')
                    ident.text = v['ident']
                    challenge.append(ident)
                if v['status']:  # enabled challenge
                    playlist.append(challenge)
                else:  # disabled challenge
                    playlist.append(etree.Comment(etree.tostring(challenge)))
            xml = etree.tostring(tree, pretty_print=True, xml_declaration=True, encoding='utf-8')
            f.seek(0)
            f.truncate()
            f.write(xml)

    def _get_challenges(self, tree, query):
        assert 'challenge' or 'comment()' in query
        for e in tree.xpath(query):
            if 'comment()' in query:
                e = etree.fromstring(e.text.replace('<!--', '').replace('-->', ''))
            file = ''
            ident = ''
            status = 'comment()' not in query
            for c in list(e):  # cycle through all tags of 'e'
                if 'file' in c.tag:
                    file = c.text
                elif 'ident' in c.tag:
                    ident = c.text
            yield file, ident, status

    def __insert_data(self, row, **kwargs):
        self._data[row] = {
            'challenge': kwargs.get('challenge'),
            'ident': kwargs.get('ident'),
            'status': kwargs.get('status'),
            'path': kwargs.get('path')
        }

    def _update_or_insert_data(self, row, **kwargs):
        if self._data.get(row):
            for k, v in kwargs.items():
                self._data[row][k] = v
        else:
            return self.__insert_data(row, **kwargs)