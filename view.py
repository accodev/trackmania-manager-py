#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PyQt5 import QtGui, QtWidgets, QtCore
from ui_mainwindow import Ui_MainWindow
from ui_aboutdialog import Ui_AboutDialog
from ui_optionsdialog import Ui_OptionsDialog
import os
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
        super(BooleanWidget, self).__init__(parent, flags=None)
        self._checkbox = QtWidgets.QCheckBox(self)
        self._layout = QtWidgets.QHBoxLayout(self)
        self._layout.addWidget(self._checkbox, alignment=QtCore.Qt.AlignCenter)

    def is_checked(self):
        return self._checkbox.isChecked()

    def set_checked(self, value: bool):
        self._checkbox.setChecked(value)


class StatusItemDelegate(QtWidgets.QItemDelegate):
    def __init__(self, parent=None):
        super(StatusItemDelegate, self).__init__(parent)

    def setEditorData(self, widget, index: QtCore.QModelIndex):
        value = index.model().data(index, QtCore.Qt.DisplayRole)
        checkbox = widget
        checkbox.set_checked(True if value is 1 else False)

    def setModelData(self, widget, model: QtCore.QAbstractItemModel, index: QtCore.QModelIndex):
        checkbox = widget
        model.setData(index, QtCore.Qt.Checked if checkbox.is_checked() else QtCore.Qt.Unchecked, QtCore.Qt.DisplayRole)

    def createEditor(self, widget: QtWidgets.QWidget, option: QtWidgets.QStyleOptionViewItem, index: QtCore.QModelIndex):
        editor = BooleanWidget(widget)
        editor.toggled.connect(self._changed)
        return editor

    def paint(self, painter: QtGui.QPainter, option: QtWidgets.QStyleOptionViewItem, index: QtCore.QModelIndex):
        self.drawCheck(painter, option, option.rect, QtCore.Qt.Checked if index.data() else QtCore.Qt.Unchecked)
        self.drawFocus(painter, option, option.rect)

    def changed(self, value):
        checkbox = self.sender()
        self.commitData(checkbox)
        self.closeEditor(checkbox)


class TrackmaniaManagerMainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(TrackmaniaManagerMainWindow, self).__init__()
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
        # matchsettings_table
        # sid = StatusItemDelegate(self)
        # self.matchsettings_table.setItemDelegateForColumn(1, sid)
        # read settings and apply saved values
        self.__read_settings()

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
            self.matchsettings_model = \
                model.MatchsettingsTableModel(self, self._settings['trackmania_root_path'], selected_file)
            self.matchsettings_table.setModel(self.matchsettings_model)
            self.matchsettings_table.show()
            print(self.matchsettings_model)
            print(self.matchsettings_table.model())

    def save_file_triggered_slot(self):
        # todo: call model._save_matchsettings
        pass

    def close_file_triggered_slot(self):
        # todo: replace self._c.matchsettingspath = '' with model
        # self._c.matchsettingspath = ''
        pass

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
        # todo: update this with model logic
        if len(selected_files):
            self._settings['last_challenges_path'] = os.path.dirname(selected_files[0])
            for selected_file in selected_files:
                path = 'Challenges\\My Challenges\\{}'.format(os.path.basename(selected_file))
                # if path not in self._matchsettings:
                #     self._matchsettings[path] = False
                # else:
                #     QtWidgets.QMessageBox.critical(self, util.APP_NAME, 'Challenge {} already present'.format(
                #         os.path.basename(selected_file)), QtWidgets.QMessageBox.Ok)
            # self.update_matchsettings_table_slot()

    def remove_tracks_button_clicked_slot(self):
        pass

    def update_window_title_slot(self):
        # todo: change this - self._c does not exist anymore
        # self.setWindowTitle('{} - {}'.format(util.APP_NAME, self._c.matchsettingspath))
        pass

    def update_close_button_slot(self):
        # todo: change this - self._c does not exist anymore
        # self.close_file_action.setEnabled(True if len(self._matchsettings) > 0 else False)
        pass

    def update_tracks_count_label_slot(self):
        # todo: change this - self._matchsettings does not exist anymore
        # self._enable_save_action_based_on_context()
        # self.tracks_count_label.setText('Tracks: {}'.format(len(self._matchsettings)))
        pass

    # def update_matchsettings_table_slot(self):
    #     self.matchsettings_table.setRowCount(len(self._matchsettings))
    #     row = 0
    #     for key, value in self._matchsettings.items():
    #         # create both challenge and status widgets
    #         c = self._create_challenge_widget(key)
    #         s = self._create_status_cb_widget(value)
    #         # add both items to the table
    #         self.matchsettings_table.setItem(row, 0, c)
    #         self.matchsettings_table.setCellWidget(row, 1, s)
    #         # go to next element
    #         row += 1
    #     self.matchsettings_table.resizeColumnsToContents()
    #     self.matchsettings_table.resizeRowsToContents()

    def update_matchsettings_table_add_remove_slot(self):
        # self.add_tracks_button.setEnabled(len(self._matchsettings) > 0)
        # self.remove_tracks_button.setEnabled(len(self._matchsettings) > 0)
        pass

    '''
    Private utility methods
    '''

    def _enable_save_action_based_on_context(self):
        # todo: change this
        # if self.tracks_count_label.text() is not '':
        #     s = ''.join(x for x in self.tracks_count_label.text() if x.isdigit())
        #     if int(s) != len(self._matchsettings):
        #         self.save_file_action.setEnabled(True)
        #         # elif # add cell widget changed (enabled/disabled) slot
        pass
