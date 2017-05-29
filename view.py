#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
from PyQt5 import QtGui, QtWidgets, QtCore
from ui_mainwindow import Ui_MainWindow
from ui_aboutdialog import Ui_AboutDialog
from ui_optionsdialog import Ui_OptionsDialog
import util


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
        self.initialize(settings)

    def initialize(self, settings):
        self.settings = settings
        self.any_setting_changed = False
        self.trackmania_root_folder_line_edit.setText(self.settings['trackmania_root_path'])
        # window title
        self.setWindowTitle(util.APP_NAME)
        # slots for buttons
        self.save_button.clicked.connect(self.save_button_clicked_slot)
        self.cancel_button.clicked.connect(self.cancel_button_clicked_slot)
        # slots for lineedits
        self.trackmania_root_folder_line_edit.double_clicked.connect(self.trackmania_root_folder_line_edit_double_clicked_slot)

    def save_button_clicked_slot(self):
        self.settings['trackmania_root_path'] = self.trackmania_root_folder_line_edit.text()
        self.any_setting_changed = False

    def cancel_button_clicked_slot(self):
        self._unsaved_changes()
        self.close()

    def trackmania_root_folder_line_edit_double_clicked_slot(self):
        selected_folder = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select trackmania root folder', self.settings['trackmania_root_path'])
        if selected_folder != self.settings['trackmania_root_path']:
            self.any_setting_changed = True
            self.trackmania_root_folder_line_edit.setText(selected_folder)

    def closeEvent(self, e: QtGui.QCloseEvent):
        self._unsaved_changes()
        e.accept()

    def _unsaved_changes(self):
        if self.any_setting_changed:
            ret = QtWidgets.QMessageBox.information(self, 'Unsaved changes', 'There are some unsaved changes\nQuit without saving?', QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
            if ret == QtWidgets.QMessageBox.No:
                self.save_button_clicked_slot()


class TrackmaniaManagerMainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    matchsettingspath_update_signal = QtCore.pyqtSignal()
    matchsettings_update_signal = QtCore.pyqtSignal()

    def __init__(self, c):
        super(TrackmaniaManagerMainWindow, self).__init__()
        self._c = c
        self.setupUi(self)
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
        self.matchsettings_table.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.matchsettings_table.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Interactive)
        # connect my signals to this form's slot
        self.matchsettings_update_signal.connect(self.update_window_title_slot)
        self.matchsettings_update_signal.connect(self.update_close_button_slot)
        self.matchsettings_update_signal.connect(self.update_tracks_count_label_slot)
        self.matchsettings_update_signal.connect(self.update_matchsettings_table_slot)
        self.matchsettings_update_signal.connect(self.update_matchsettings_table_add_remove_slot)
        # read settings and apply saved values
        self.settings = QtCore.QSettings(QtCore.QSettings.IniFormat, QtCore.QSettings.UserScope, util.AUTHOR,
                                         util.APP_NAME)
        self.__read_settings()

    '''
    Settings
    '''

    def __read_settings(self):
        self.settings.beginGroup('mainwindow')
        geometry = self.settings.value('geometry', defaultValue=self.geometry())
        is_maximized = self.settings.value('is_maximized', defaultValue=self.isMaximized())
        self.settings.endGroup()
        self.setGeometry(geometry)
        if is_maximized is 'true':
            self.showMaximized()
        self.settings.beginGroup('general')
        self.last_matchsettings_path = self.settings.value('last_matchsettings_path', defaultValue=os.curdir)
        self.last_challenges_path = self.settings.value('last_challenges_path', defaultValue=os.curdir)
        self.trackmania_root_path = self.settings.value('trackmania_root_path', defaultValue=os.curdir)
        self.settings.endGroup()

    def __save_settings(self):
        self.settings.beginGroup('mainwindow')
        self.settings.setValue('geometry', self.geometry())
        self.settings.setValue('is_maximized', self.isMaximized())
        self.settings.endGroup()
        self.settings.beginGroup('general')
        self.settings.setValue('last_matchsettings_path', self.last_matchsettings_path)
        self.settings.setValue('last_challenges_path', self.last_challenges_path)
        self.settings.setValue('trackmania_root_path', self.trackmania_root_path)
        self.settings.endGroup()

    '''
    Event handling
    '''

    def dragEnterEvent(self, e: QtGui.QDragEnterEvent):
        if e.mimeData().hasUrls():
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, e: QtGui.QDropEvent):
        e.accept()
        if len(e.mimeData().urls()) == 1 and e.mimeData().urls()[0].toLocalFile().endswith('.txt'):
            self._c.matchsettingspath = e.mimeData().urls()[0].toLocalFile()
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
        selected_file, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open matchsettings file', self.last_matchsettings_path,
                                                                 'Matchsettings files (*.txt)')
        if selected_file:
            self.last_matchsettings_path = os.path.dirname(selected_file)
            self._c.matchsettingspath = selected_file

    def save_file_triggered_slot(self):
        pass

    def close_file_triggered_slot(self):
        self._c.matchsettingspath = ''
        self.matchsettings_table.setRowCount(0)

    def about_triggered_slot(self):
        dlg = AboutDialog(self)
        ret = dlg.exec_()

    def edit_settings_triggered_slot(self):
        # todo: this dictionary has to become the container for all settings through the code.
        settings = {
            'trackmania_root_path': self.trackmania_root_path
        }
        dlg = OptionsDialog(self, settings)
        ret = dlg.exec_()
        if ret == 0:
            self.trackmania_root_path = dlg.settings['trackmania_root_path']

    def add_tracks_button_clicked_slot(self):
        # show open file(s) dialog
        selected_files, _ = QtWidgets.QFileDialog.getOpenFileNames(self, 'Open challenge files', self.last_challenges_path,
                                                                  'Challenge files (*.Gbx)')
        if len(selected_files):
            self.last_challenges_path = os.path.dirname(selected_files[0])
            _matchsettings = self._c.matchsettings
            for selected_file in selected_files:
                path = 'Challenges\\My Challenges\\{}'.format(os.path.basename(selected_file))
                if path not in _matchsettings:
                    _matchsettings[path] = False
                else:
                    QtWidgets.QMessageBox.critical(self, util.APP_NAME, 'Challenge {} already present'.format(os.path.basename(selected_file)), QtWidgets.QMessageBox.Ok)
            self._c.matchsettings = _matchsettings

    def remove_tracks_button_clicked_slot(self):
        pass

    def update_window_title_slot(self):
        self.setWindowTitle('{} - {}'.format(util.APP_NAME, self._c.matchsettingspath))

    def update_close_button_slot(self):
        self.close_file_action.setEnabled(True if len(self._c.matchsettings) > 0 else False)

    def update_tracks_count_label_slot(self):
        self.tracks_count_label.setText('Tracks: {}'.format(len(self._c.matchsettings)))

    def update_matchsettings_table_slot(self):
        self.matchsettings_table.setRowCount(len(self._c.matchsettings))
        row = 0
        for key, value in self._c.matchsettings.items():
            # create both challenge and status widgets
            c = self._create_challenge_widget(key)
            s = self._create_status_cb_widget(value)
            # add both items to the table
            self.matchsettings_table.setItem(row, 0, c)
            self.matchsettings_table.setCellWidget(row, 1, s)
            # go to next element
            row += 1
        self.matchsettings_table.resizeColumnsToContents()
        self.matchsettings_table.resizeRowsToContents()

    def update_matchsettings_table_add_remove_slot(self):
        self.add_tracks_button.setEnabled(len(self._c.matchsettings) > 0)
        self.remove_tracks_button.setEnabled(len(self._c.matchsettings) > 0)

    '''
    Controller handled methods
    '''

    def matchsettingspath_updated(self):
        self.matchsettingspath_update_signal.emit()

    def matchsettings_updated(self):
        self.matchsettings_update_signal.emit()

    '''
    Private utility methods
    '''

    def _create_challenge_widget(self, path):
        c = QtWidgets.QTableWidgetItem(path)
        c.setFlags(c.flags() ^ QtCore.Qt.ItemIsEditable)
        return c

    def _create_status_cb_widget(self, status=False):
        s = QtWidgets.QWidget()
        chkbox = QtWidgets.QCheckBox(s)
        chkbox.setCheckState(QtCore.Qt.Checked) if status else chkbox.setCheckState(QtCore.Qt.Unchecked)
        hbl = QtWidgets.QHBoxLayout()
        hbl.setAlignment(QtCore.Qt.AlignCenter)
        hbl.setContentsMargins(0, 0, 0, 0)
        hbl.addWidget(chkbox)
        s.setLayout(hbl)
        return s
