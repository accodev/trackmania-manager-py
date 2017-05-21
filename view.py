#!/usr/bin/python3
# -*- coding: utf-8 -*-

import controller
from PyQt5 import QtGui, QtWidgets, QtCore

class AboutDialog(QtWidgets.QDialog):
    def __init__(self, parent):
        super(AboutDialog, self).__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        information_label = QtWidgets.QLabel(self)
        information_label.setText('This application is awesome')
        ok_button = QtWidgets.QPushButton('Ok', self)    

        
class TrackmaniaManagerMainWindow(QtWidgets.QMainWindow):
    def __init__(self, c):
        super(TrackmaniaManagerMainWindow, self).__init__()
        self.setup_ui()
        self._c = c
        
    def setup_ui(self): 
        self.setAcceptDrops(True)

        menubar = self.menuBar()

        self.open_file_action = QtWidgets.QAction(QtGui.QIcon.fromTheme('document-open', QtGui.QIcon('resources/icons/open-file.ico')), '&Open file', self)
        self.open_file_action.setShortcut('Ctrl+O')
        self.open_file_action.setStatusTip('Open a matchsettings file')
        self.open_file_action.triggered.connect(self.open_file_slot)

        self.save_file_action = QtWidgets.QAction(QtGui.QIcon.fromTheme('document-save', QtGui.QIcon('resources/icons/save-file.ico')), '&Save file', self)
        self.save_file_action.setShortcut('Ctrl+S')
        self.save_file_action.setStatusTip('Save current matchsettings file')
        self.save_file_action.setEnabled(False)
        self.save_file_action.triggered.connect(self.save_file_slot)

        self.close_file_action = QtWidgets.QAction(QtGui.QIcon.fromTheme('window-close', QtGui.QIcon('resources/icons/close-file.ico')), '&Close file', self)
        self.close_file_action.setStatusTip('Close current matchsettings file')
        self.close_file_action.setEnabled(False)
        self.close_file_action.triggered.connect(self.close_file_slot)

        exit_action = QtWidgets.QAction(QtGui.QIcon.fromTheme('window-close', QtGui.QIcon('resources/icons/exit.ico')), '&Exit', self)        
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('Exit application')
        exit_action.triggered.connect(QtWidgets.qApp.quit)
        
        file_menu = menubar.addMenu('&File')
        file_menu.addAction(self.open_file_action)
        file_menu.addAction(self.save_file_action)
        file_menu.addAction(self.close_file_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)

        edit_settings_action = QtWidgets.QAction(QtGui.QIcon.fromTheme('edit', QtGui.QIcon('resources/icons/edit-settings.ico')), '&Edit settings', self)
        edit_settings_action.setStatusTip('Edit application settings')
        edit_settings_action.triggered.connect(self.edit_settings_slot)

        options_menu = menubar.addMenu('&Options')
        options_menu.addAction(edit_settings_action)

        about_action = QtWidgets.QAction(QtGui.QIcon.fromTheme('faq', QtGui.QIcon('resources/icons/about.ico')), '&About', self)
        about_action.setStatusTip('Information about this application')
        about_action.triggered.connect(self.about_slot)

        help_menu = menubar.addMenu('&Help')
        help_menu.addAction(about_action)

        self.toolbar = self.addToolBar('File management')
        self.toolbar.addAction(self.open_file_action)
        self.toolbar.addAction(self.save_file_action)
        self.toolbar.addAction(self.close_file_action)

        central_widget = QtWidgets.QWidget(self)

        self.matchsettings_table = QtWidgets.QTableWidget(central_widget)
        self.matchsettings_table.setColumnCount(2)
        self.matchsettings_table.setHorizontalHeaderLabels(('Challenge', 'Status'))

        add_tracks_button = QtWidgets.QPushButton('&Add track(s)', central_widget)
        add_tracks_button.setEnabled(False)
        add_tracks_button.clicked.connect(self.add_tracks_button_clicked)

        remove_tracks_button = QtWidgets.QPushButton('&Remove track(s)', central_widget)
        remove_tracks_button.setEnabled(False)
        remove_tracks_button.clicked.connect(self.remove_tracks_button_clicked)

        hbox_layout = QtWidgets.QHBoxLayout()
        hbox_layout.addStretch(1)
        hbox_layout.addWidget(add_tracks_button)
        hbox_layout.addWidget(remove_tracks_button)

        vbox_layout = QtWidgets.QVBoxLayout()
        vbox_layout.addWidget(self.matchsettings_table, 1)
        vbox_layout.addLayout(hbox_layout)

        central_widget.setLayout(vbox_layout)
        
        self.setCentralWidget(central_widget)
        
        status_bar = self.statusBar()
        self.tracks_count_label = QtWidgets.QLabel(status_bar)
        status_bar.insertPermanentWidget(0, self.tracks_count_label)
        self._update_tracks_count_label(0)

        self.setMinimumSize(640, 480)
        self.setWindowTitle('trackmania-manager')  
        self.setWindowIcon(QtGui.QIcon('resources/icons/app.ico'))

    def dragEnterEvent(self, e: QtGui.QDragEnterEvent):
        if e.mimeData().hasUrls() and len(e.mimeData().urls()) == 1:
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, e: QtGui.QDropEvent):
        self._c.matchsettingspath = e.mimeData().urls()[0].toLocalFile()

    def open_file_slot(self):
        self._c.matchsettingspath, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open matchsettings file', 'c:\\nph\\tmnf\\gamedata\\tracks\\matchsettings', 'Matchsettings files (*.txt)')

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
        self.matchsettings_table.setRowCount(len(self._c.matchsettings))
        self._update_tracks_count_label(len(self._c.matchsettings))
        self.close_file_action.setEnabled(True if len(self._c.matchsettings) > 0 else False)
        # todo: refactor this - controller.matchsettings should be QTableModel
        row = 0
        for key, value in self._c.matchsettings.items():
            challenge_name_twi = QtWidgets.QTableWidgetItem(key)
            self.matchsettings_table.setItem(row, 0, challenge_name_twi)
            status_twi = QtWidgets.QTableWidgetItem()
            status_twi.setCheckState(QtCore.Qt.Checked) if value else status_twi.setCheckState(QtCore.Qt.Unchecked)
            self.matchsettings_table.setItem(row, 1, status_twi)
            row +=1

    def add_tracks_button_clicked(self):
        pass

    def remove_tracks_button_clicked(self):
        pass

    def _update_tracks_count_label(self, count: int):
        self.tracks_count_label.setText('Tracks: {}'.format(count))