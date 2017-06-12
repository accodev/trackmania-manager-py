#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PyQt5 import QtGui, QtWidgets, QtCore
from ui_mainwindow import Ui_MainWindow
from ui_aboutdialog import Ui_AboutDialog
from ui_optionsdialog import Ui_OptionsDialog
import os
import logging
import util
import model


class AboutDialog(QtWidgets.QDialog, Ui_AboutDialog):
    def __init__(self, parent):
        super(AboutDialog, self).__init__(parent)
        self.setupUi(self)
        self.initialize()

    def initialize(self):
        self.setWindowTitle(util.APP_NAME)
        # slots for buttons
        self.ok_button.clicked.connect(self.ok_button_clicked)

    def ok_button_clicked(self):
        self.close()


class OptionsDialog(QtWidgets.QDialog, Ui_OptionsDialog):
    def __init__(self, parent, settings):
        super(OptionsDialog, self).__init__(parent)
        self.setupUi(self)
        self._settings = settings
        self.any_setting_changed = False
        self.initialize()

    @property
    def settings(self):
        return self._settings

    @settings.setter
    def settings(self, value):
        self._settings = value

    def initialize(self):
        self.trackmania_root_folder_line_edit.setText(self.settings['trackmania_root_path'])
        # window title
        self.setWindowTitle(util.APP_NAME)
        # slots for buttons
        self.save_button.clicked.connect(self.save_button_clicked_slot)
        self.cancel_button.clicked.connect(self.cancel_button_clicked_slot)
        # slots for lineedits
        self.trackmania_root_folder_line_edit.double_clicked.connect(
            self.trackmania_root_folder_line_edit_double_clicked_slot)

    def save_button_clicked_slot(self):
        self.settings['trackmania_root_path'] = self.trackmania_root_folder_line_edit.text()
        self.any_setting_changed = False

    def cancel_button_clicked_slot(self):
        self._unsaved_changes()
        self.close()

    def trackmania_root_folder_line_edit_double_clicked_slot(self):
        selected_folder = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select trackmania root folder',
                                                                     self.settings['trackmania_root_path'])
        if selected_folder != self.settings['trackmania_root_path']:
            self.any_setting_changed = True
            self.trackmania_root_folder_line_edit.setText(selected_folder)

    def closeEvent(self, e: QtGui.QCloseEvent):
        self._unsaved_changes()
        e.accept()

    def _unsaved_changes(self):
        if self.any_setting_changed:
            ret = QtWidgets.QMessageBox.information(self, 'Unsaved changes',
                                                    'There are some unsaved changes\nQuit without saving?',
                                                    QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
            if ret == QtWidgets.QMessageBox.No:
                self.save_button_clicked_slot()


class BooleanWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(BooleanWidget, self).__init__(parent)
        self._checkbox = QtWidgets.QCheckBox(self)
        self._layout = QtWidgets.QHBoxLayout(self)
        self._layout.addWidget(self._checkbox, alignment=QtCore.Qt.AlignCenter)

    def is_checked(self):
        return self._checkbox.isChecked()

    def set_checked(self, value: bool):
        self._checkbox.setChecked(value)

    @property
    def checkbox(self):
        return self._checkbox


class StatusItemDelegate(QtWidgets.QItemDelegate):
    def __init__(self, parent=None, real_model=None, proxy_model=None,*args):
        super(StatusItemDelegate, self).__init__(parent, *args)
        self._proxy_model = proxy_model
        self._real_model = real_model
        logging.debug('[self={s}]'.format(s=self))

    def setEditorData(self, widget, index: QtCore.QModelIndex):
        real_index = self._proxy_model.mapToSource(index)
        value = not real_index.model().data(real_index, QtCore.Qt.DisplayRole).value()
        editor = widget
        logging.debug('[editor={e}] [index={i}] - prev. value({pv}) => new value({nv})'.format(e=editor, i=real_index, pv=editor.is_checked(), nv=value))
        editor.set_checked(value)

    def setModelData(self, widget, model: QtCore.QAbstractItemModel, index: QtCore.QModelIndex):
        real_index = self._proxy_model.mapToSource(index)
        editor = widget
        logging.debug('[editor={e}] [model={m}] [index={i}] - editor.is_checked({ic})'.format(e=editor, m=model, i=real_index, ic=editor.is_checked()))
        self._real_model.setData(real_index, QtCore.Qt.Checked if editor.is_checked() else QtCore.Qt.Unchecked, QtCore.Qt.DisplayRole)
        self._real_model.setData(real_index, QtCore.QVariant(editor.is_checked()), QtCore.Qt.EditRole)

    def createEditor(self, widget: QtWidgets.QWidget, option: QtWidgets.QStyleOptionViewItem, index: QtCore.QModelIndex):
        editor = BooleanWidget(widget)
        logging.debug('[widget={w}] [option={o}] [index={i}] - [editor={e}]'.format(w=widget, o=option, i=index, e=editor))
        return editor

    def paint(self, painter: QtGui.QPainter, option: QtWidgets.QStyleOptionViewItem, index: QtCore.QModelIndex):
        # logging.debug('[painter={p}] [option={o}] [index={i}] - index.data()={v}'.format(p=painter, o=option, i=index, v=index.data()))
        self.drawCheck(painter, option, option.rect, QtCore.Qt.Checked if index.data() else QtCore.Qt.Unchecked)
        self.drawFocus(painter, option, option.rect)


class TrackmaniaManagerMainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(TrackmaniaManagerMainWindow, self).__init__()
        logging.info('instancing new window')
        self.setupUi(self)
        self._settings_manager = QtCore.QSettings(QtCore.QSettings.IniFormat, QtCore.QSettings.UserScope, util.AUTHOR,
                                                  util.APP_NAME)
        self._settings = {
            'last_matchsettings_path': './matchsettings.txt',
            'last_challenges_path': '.',
            'trackmania_root_path': '.'
        }
        # todo: remove all references to these fields below in favor of _settings_dict
        self.last_matchsettings_path = './matchsettings.txt'
        self.last_challenges_path = '.'
        self.trackmania_root_path = '.'
        self.matchsettings_model = None
        self.matchsettings_sort_proxy_model = None
        self.tracks_count_label = None
        self.initialize()

    def initialize(self):
        self.setWindowTitle(util.APP_NAME)
        # slots for actions
        self.open_file_action.triggered.connect(self.open_file_triggered_slot)
        self.save_file_action.triggered.connect(self.save_file_triggered_slot)
        self.close_file_action.triggered.connect(self.close_file_triggered_slot)
        self.exit_action.triggered.connect(self.close)
        self.edit_settings_action.triggered.connect(self.edit_settings_triggered_slot)
        self.about_action.triggered.connect(self.about_triggered_slot)
        # slots for buttons
        self.add_tracks_button.clicked.connect(self.add_tracks_button_clicked_slot)
        self.remove_tracks_button.clicked.connect(self.remove_tracks_button_clicked_slot)
        # tracks count
        self.tracks_count_label = QtWidgets.QLabel(self.status_bar)
        self.status_bar.insertPermanentWidget(0, self.tracks_count_label)
        # read settings and apply saved values
        self.__read_settings()
        logging.info('settings: {0}'.format(self._settings))

    '''
    Settings
    '''

    def __read_settings(self):
        self._settings_manager.beginGroup('mainwindow')
        geometry = self._settings_manager.value('geometry', defaultValue=self.geometry())
        is_maximized = self._settings_manager.value('is_maximized', defaultValue=self.isMaximized())
        self._settings_manager.endGroup()
        self.setGeometry(geometry)
        if is_maximized is 'true':
            self.showMaximized()
        self._settings_manager.beginGroup('general')
        self._settings['last_matchsettings_path'] = self._settings_manager.value('last_matchsettings_path', defaultValue=os.curdir)
        self._settings['last_challenges_path'] = self._settings_manager.value('last_challenges_path', defaultValue=os.curdir)
        self._settings['trackmania_root_path'] = self._settings_manager.value('trackmania_root_path', defaultValue=os.curdir)
        self._settings_manager.endGroup()

    def __save_settings(self):
        self._settings_manager.beginGroup('mainwindow')
        self._settings_manager.setValue('geometry', self.geometry())
        self._settings_manager.setValue('is_maximized', self.isMaximized())
        self._settings_manager.endGroup()
        self._settings_manager.beginGroup('general')
        for k, v in self._settings.items():
            self._settings_manager.setValue(k, v)
        self._settings_manager.endGroup()

    '''
    Event handling
    '''

    def dragEnterEvent(self, e: QtGui.QDragEnterEvent):
        if e.mimeData().hasUrls():
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, e: QtGui.QDropEvent):
        # todo: work in progress
        e.accept()
        if len(e.mimeData().urls()) == 1 and e.mimeData().urls()[0].toLocalFile().endswith('.txt'):
            # self._c.matchsettingspath = e.mimeData().urls()[0].toLocalFile()
            pass
        else:
            for url in e.mimeData().urls():
                if url.toLocalFile().endswith('.Gbx'):
                    print(url.toLocalFile())

    def closeEvent(self, e: QtGui.QCloseEvent):
        self.__save_settings()
        e.accept()

    '''
    Slots
    '''

    def open_file_triggered_slot(self):
        selected_file, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open matchsettings file',
                                                                 self._settings['last_matchsettings_path'],
                                                                 'Matchsettings files (*.txt)')
        if selected_file:
            self._settings['last_matchsettings_path'] = os.path.dirname(selected_file)
            self._set_table_model(selected_file)

    def save_file_triggered_slot(self):
        self.matchsettings_model.save_matchsettings()

    def close_file_triggered_slot(self):
        self._set_table_model()

    def about_triggered_slot(self):
        dlg = AboutDialog(self)
        dlg.exec_()

    def edit_settings_triggered_slot(self):
        od = OptionsDialog(self, self._settings)
        ret = od.exec_()
        if ret == 0:
            self._settings = od.settings

    def add_tracks_button_clicked_slot(self):
        # show open file(s) dialog
        selected_files, _ = QtWidgets.QFileDialog.getOpenFileNames(self, 'Open challenge files',
                                                                   self._settings['last_challenges_path'],
                                                                   'Challenge files (*.Gbx)')
        if len(selected_files):
            self._settings['last_challenges_path'] = os.path.dirname(selected_files[0])
            for selected_file in selected_files:
                path = 'Challenges\\My Challenges\\{}'.format(os.path.basename(selected_file))
                values = self.matchsettings_model.internal_data.values()
                if path not in values:
                    new_row_id = self.matchsettings_model.rowCount()
                    self.matchsettings_model.insertRows(new_row_id, 1)
                    new_challenge_idx = self.matchsettings_model.createIndex(new_row_id, 0)
                    new_status_idx = self.matchsettings_model.createIndex(new_row_id, 1)
                    self.matchsettings_model.setData(new_challenge_idx, QtCore.QVariant(path), QtCore.Qt.EditRole)
                    self.matchsettings_model.setData(new_status_idx, QtCore.QVariant(False), QtCore.Qt.EditRole)
                else:
                    QtWidgets.QMessageBox.critical(self, util.APP_NAME, 'Challenge {} already present'.format(
                        os.path.basename(selected_file)), QtWidgets.QMessageBox.Ok)

    def remove_tracks_button_clicked_slot(self):
        logging.info('begin removal of tracks')
        selection = self.matchsettings_table.selectionModel().selection()
        rows = []
        for index in selection.indexes():
            real_index = self.matchsettings_sort_proxy_model.mapToSource(index)
            if real_index.row() not in rows:
                rows.append(real_index.row())
        rows.sort()
        logging.info('selected tracks: {}'.format(rows))
        self.matchsettings_model.removeRows(rows[0], len(rows))
        logging.info('removal of tracks finished')

    def matchsettings_model_data_changed_slot(self, tl: QtCore.QModelIndex, br: QtCore.QModelIndex):
        if (tl and tl.isValid()) and (br and br.isValid()):
            item_count = self.matchsettings_model.rowCount()
            self.add_tracks_button.setEnabled(item_count > 0)
            self.remove_tracks_button.setEnabled(item_count > 0)
            self.save_file_action.setEnabled(item_count > 0)
            self.close_file_action.setEnabled(item_count > 0)
            self.tracks_count_label.setText('Tracks: {ic}'.format(ic=item_count))
            self.setWindowTitle('{an} - {ofn}'.format(an=util.APP_NAME, ofn=self.matchsettings_model.matchsettings_path))

    '''
    Private utility methods
    '''

    def _set_table_model(self, matchsettings_path=''):
        if matchsettings_path:
            self.matchsettings_model = \
                model.MatchsettingsTableModel(self, self._settings['trackmania_root_path'], matchsettings_path)
            # connect to model signals
            self.matchsettings_model.dataChanged.connect(self.matchsettings_model_data_changed_slot)
            # read matchsettings file
            self.matchsettings_model.read_matchsettings()
            # create sort filter proxy model
            self.matchsettings_sort_proxy_model = QtCore.QSortFilterProxyModel(self)
            self.matchsettings_sort_proxy_model.setDynamicSortFilter(True)
            self.matchsettings_sort_proxy_model.setSourceModel(self.matchsettings_model)
            # set model to matchsettings_table
            sid = StatusItemDelegate(self.matchsettings_table, self.matchsettings_model, self.matchsettings_sort_proxy_model)
            self.matchsettings_table.setItemDelegateForColumn(2, sid)
            self.matchsettings_table.setModel(self.matchsettings_sort_proxy_model)
            self.matchsettings_table.setSortingEnabled(True)
            self.matchsettings_table.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Interactive)
            self.matchsettings_table.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
            self.matchsettings_table.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.Interactive)
            self.matchsettings_table.setEditTriggers(QtWidgets.QAbstractItemView.AllEditTriggers)
            # self.matchsettings_table.resizeRowsToContents()
        else:
            self.matchsettings_model = None
            self.matchsettings_table.setModel(None)
            self.add_tracks_button.setEnabled(False)
            self.remove_tracks_button.setEnabled(False)
            self.save_file_action.setEnabled(False)
            self.close_file_action.setEnabled(False)
            self.tracks_count_label.setText('Tracks: {ic}'.format(ic=0))
            self.setWindowTitle('{an}'.format(an=util.APP_NAME))
