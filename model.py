#!/usr/bin/python3
# -*- coding: utf-8 -*-

import collections
import logging
from lxml import etree
from PyQt5 import QtCore


class MatchsettingsTableModel(QtCore.QAbstractTableModel):
    def __init__(self, parent=None, root_path='.', matchsettings_path='matchsettings.txt'):
        super(MatchsettingsTableModel, self).__init__(parent)
        self._data = collections.OrderedDict()
        self._matchsettings_path = matchsettings_path
        self._root_path = root_path
        self._read_matchsettings()

    # redefinition of QtCore.QAbstractTableModel methods
    def rowCount(self, parent=None, *args, **kwargs):
        if parent.isValid():
            print('rowCount: {}'.format(0))
            return 0
        print('rowCount: {}'.format(len(self._data)))
        return len(self._data)

    def columnCount(self, parent=None, *args, **kwargs):
        return 2

    def headerData(self, section, orientation, role=None):
        if role != QtCore.Qt.DisplayRole:
            return QtCore.QVariant()
        if orientation == QtCore.Qt.Horizontal:
            if section == 0:
                return QtCore.QVariant("Challenge name")
            elif section == 1:
                return QtCore.QVariant("Status")
            return ""
        return QtCore.QVariant()

    def setData(self, index: QtCore.QModelIndex, value: QtCore.QVariant, role=None):
        if index.isValid() and role == QtCore.Qt.EditRole:
            row = index.row()
            column = index.column()
            logging.debug('updating row({}),column({}) with value({})'.format(row, column, value))
            if column == 0:  # challenge
                if self._data.get(row):  # already existing challenge
                    self._data[row].update({'challenge': value})
                else:  # new challenge
                    self._data[row] = {'challenge': value, 'status': False}
            elif column == 1:  # status
                if self._data.get(row):  # already existing challenge
                    self._data[row].update({'status': value})
                else:  # new status
                    self._data[row] = {'challenge': '', 'status': value}
            else:
                logging.warning('unmapped column {}'.format(column))
                return False  # unmapped column
            # todo: emit dataChanged signal - see QAbstractTableModel documentation
            self.dataChanged(index, index)
            return True  # all is well
        return False  # index is not valid or role is not QtCore.Qt.EditRole

    def data(self, index: QtCore.QModelIndex, role=None):
        if role == QtCore.Qt.DisplayRole:
            row = index.row()
            column = index.column()
            if column == 0:  # challenge
                if self._data.get(row):
                    return QtCore.QVariant(self._data[row]['challenge'])
            elif column == 1:  # status
                if self._data.get(row):
                    return QtCore.QVariant(self._data[row]['status'])
        return QtCore.QVariant()

    def flags(self, index: QtCore.QModelIndex):
        _flags = QtCore.Qt.ItemIsEnabled
        if index.column() == 0 or index.column() == 1:  # challenge and status are editable
            _flags |= QtCore.Qt.ItemIsEditable
        return _flags

    def insertRows(self, row, count, parent=None, *args, **kwargs):
        self.beginInsertRows(args, kwargs)
        if self._data.get(row):  # starting row already exists...
            operation_result = False  # only allow to append new rows
        else:  # new rows
            for i in range(row, count):
                self._data[i] = {'challenge': '', 'status': False}
            operation_result = True
        self.endInsertRows(args, kwargs)
        return operation_result

    def removeRows(self, row, count, parent=None, *args, **kwargs):
        self.beginRemoveRows(args, kwargs)
        if self._data.get(row):  # starting row exists
            for i in range(row, count):
                self._data.pop(i)
            operation_result = True
        else:  # does not exist
            operation_result = False
        self.endRemoveRows(args, kwargs)
        return operation_result

    def insertColumns(self, column, count, parent=None, *args, **kwargs):
        self.beginInsertColumns()
        self.endInsertColumns()
        return False

    def removeColumns(self, column, count, parent=None, *args, **kwargs):
        self.beginRemoveColumns()
        self.endRemoveColumns()
        return False

    def _read_matchsettings(self):
        with open(self._matchsettings_path, 'r') as f:
            tree = etree.parse(f)
            row = 0
            for k, v in self._get_challenges(tree, '/playlist//challenge'):
                self._data[row] = {'challenge': k, 'status': v, 'path': ''}
                row += 1
            for k, v in self._get_challenges(tree, '/playlist//comment()'):
                self._data[row] = {'challenge': k, 'status': v, 'path': ''}
                row += 1
            # [print('{}: {}'.format(k, v)) for k, v in self._data.items()]

    def _get_challenges(self, tree, query):
        assert 'challenge' or 'comment()' in query
        for e in tree.xpath(query):
            if 'comment()' in query:
                e = etree.fromstring(e.text.replace('<!--', '').replace('-->', ''))
            for c in list(e):
                if c.tag == 'file':
                    yield c.text, 'comment()' not in query

    def _save_matchsettings(self):
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

if __name__ == '__main__':
    m = MatchsettingsTableModel(matchsettings_path='C:\\nph\\tmnf\\GameData\\Tracks\\MatchSettings\\Custom\\gvr.txt')
    print(m.rowCount())
