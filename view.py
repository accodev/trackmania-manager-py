#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import controller
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
    def __init__(self, c):
        super(TrackmaniaManagerMainWindow, self).__init__()
        self._c = c
        self.setupUi(self)
        self.initialize()
        
    def initialize(self): 
        # callbacks for actions
        self.open_file_action.triggered.connect(self.open_file_slot)
        self.save_file_action.triggered.connect(self.save_file_slot)
        self.close_file_action.triggered.connect(self.close_file_slot)
        #self.exit_action.triggered.connect(QtWidgets.qApp.quit)
        self.exit_action.triggered.connect(self.close)
        self.edit_settings_action.triggered.connect(self.edit_settings_slot)
        self.about_action.triggered.connect(self.about_slot)
        # callbacks for buttons
        self.add_tracks_button.clicked.connect(self.add_tracks_button_clicked)
        self.remove_tracks_button.clicked.connect(self.remove_tracks_button_clicked)
        # tracks count
        self.tracks_count_label = QtWidgets.QLabel(self.status_bar)
        self.status_bar.insertPermanentWidget(0, self.tracks_count_label)
        self._update_tracks_count_label(0)
        # matchsettings_table
        self.matchsettings_table.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.matchsettings_table.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Interactive)
        # read settings and apply saved values
        self.settings = QtCore.QSettings(QtCore.QSettings.IniFormat, QtCore.QSettings.UserScope, util.AUTHOR, util.APP_NAME)
        self.__read_settings()

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


    def dragEnterEvent(self, e: QtGui.QDragEnterEvent):
        if e.mimeData().hasUrls() and len(e.mimeData().urls()) == 1:
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, e: QtGui.QDropEvent):
        self._c.matchsettingspath = e.mimeData().urls()[0].toLocalFile()

    def closeEvent(self, e: QtGui.QCloseEvent):
        self.__save_settings()
        e.accept()

    def open_file_slot(self):
        selected_file, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open matchsettings file', self.last_path, 'Matchsettings files (*.txt)')
        if selected_file:
            self.last_path = os.path.dirname(selected_file)
            self._c.matchsettingspath = selected_file

    def save_file_slot(self):
        print('save file triggered')

    def close_file_slot(self):
        self._c.matchsettingspath = ''
        self.matchsettings_table.setRowCount(0)

    def about_slot(self):
        about_dialog = AboutDialog(self)
        ret = about_dialog.exec_()

    def edit_settings_slot(self):
        print('edit settings triggered')

    def matchsettings_updated(self):
        self.setWindowTitle('{} - {}'.format(self.windowTitle(), self._c.matchsettingspath))
        self.matchsettings_table.setRowCount(len(self._c.matchsettings))
        self._update_tracks_count_label(len(self._c.matchsettings))
        self.close_file_action.setEnabled(True if len(self._c.matchsettings) > 0 else False)
        # todo: refactor this - controller.matchsettings should be QTableModel
        row = 0
        for key, value in self._c.matchsettings.items():
            # challenge name
            challenge_name_twi = QtWidgets.QTableWidgetItem(key)
            challenge_name_twi.setFlags(challenge_name_twi.flags() ^ QtCore.Qt.ItemIsEditable)
            self.matchsettings_table.setItem(row, 0, challenge_name_twi)
            # status
            status_widget = QtWidgets.QWidget()
            status_cbx = QtWidgets.QCheckBox()
            status_cbx.setCheckState(QtCore.Qt.Checked) if value else status_cbx.setCheckState(QtCore.Qt.Unchecked)
            hbl = QtWidgets.QHBoxLayout(status_widget)
            hbl.addWidget(status_cbx)
            hbl.setAlignment(QtCore.Qt.AlignCenter)
            hbl.setContentsMargins(0,0,0,0)
            status_widget.setLayout(hbl)
            self.matchsettings_table.setCellWidget(row, 1, status_widget)
            # go to next element
            row +=1
        self.matchsettings_table.resizeColumnsToContents()
        self.matchsettings_table.resizeRowsToContents()

    def add_tracks_button_clicked(self):
        pass

    def remove_tracks_button_clicked(self):
        pass

    def _update_tracks_count_label(self, count: int):
        self.tracks_count_label.setText('Tracks: {}'.format(count))