#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
from PyQt5 import QtGui, QtWidgets, QtCore
from ui_mainwindow import Ui_MainWindow
import util


class AboutDialog(QtWidgets.QDialog):
    def __init__(self, parent):
        super(AboutDialog, self).__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        information_label = QtWidgets.QLabel(self)
        information_label.setText('This application is awesome')
        ok_button = QtWidgets.QPushButton('Ok', self)


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
        # self.exit_action.triggered.connect(QtWidgets.qApp.quit)
        self.exit_action.triggered.connect(self.close)
        self.edit_settings_action.triggered.connect(self.edit_settings_triggered_slot)
        self.about_action.triggered.connect(self.about_triggered_slot)
        # slots for buttons
        self.add_tracks_button.clicked.connect(self.add_tracks_button_clicked_slot)
        self.remove_tracks_button.clicked.connect(self.remove_tracks_button_clicked_slot)
        # tracks count
        self.tracks_count_label = QtWidgets.QLabel(self.status_bar)
        self.status_bar.insertPermanentWidget(0, self.tracks_count_label)
        # self.update_tracks_count_label_slot()
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
        self.last_path = self.settings.value('last_path', defaultValue='c:\\')
        self.settings.endGroup()

    def __save_settings(self):
        self.settings.beginGroup('mainwindow')
        self.settings.setValue('geometry', self.geometry())
        self.settings.setValue('is_maximized', self.isMaximized())
        self.settings.endGroup()
        self.settings.beginGroup('general')
        self.settings.setValue('last_path', self.last_path)
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
        selected_file, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open matchsettings file', self.last_path,
                                                                 'Matchsettings files (*.txt)')
        if selected_file:
            self.last_path = os.path.dirname(selected_file)
            self._c.matchsettingspath = selected_file

    def save_file_triggered_slot(self):
        pass

    def close_file_triggered_slot(self):
        self._c.matchsettingspath = ''
        self.matchsettings_table.setRowCount(0)

    def about_triggered_slot(self):
        about_dialog = AboutDialog(self)
        ret = about_dialog.exec_()

    def edit_settings_triggered_slot(self):
        pass

    def add_tracks_button_clicked_slot(self):
        # show open file(s) dialog
        selected_files, _ = QtWidgets.QFileDialog.getOpenFileNames(self, 'Open challenge files', 'c:\\',
                                                                  'Challenge files (*.Gbx)')
        row = self.matchsettings_table.rowCount()
        for selected_file in selected_files:
            path = 'Challenges\\My Challenges\\{}'.format(os.path.basename(selected_file))
            if path not in self._c.matchsettings:
                self.matchsettings_table.insertRow(row)
                # create both challenge and status widgets
                c = self._create_challenge_widget(path)
                s = self._create_status_cb_widget(False)
                # add both items to the table
                self.matchsettings_table.setItem(row, 0, c)
                self.matchsettings_table.setCellWidget(row, 1, s)
            else:
                QtWidgets.QMessageBox.critical(self, util.APP_NAME, 'Challenge {} already present'.format(os.path.basename(selected_file)), QtWidgets.QMessageBox.Ok)
            row += 1
        self.matchsettings_table.resizeRowsToContents()
        self.matchsettings_table.scrollToBottom()

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
