#!/usr/bin/python3
# -*- coding: utf-8 -*-

import controller
from PyQt5 import QtGui, QtWidgets

class AboutDialog(QtWidgets.QDialog):
    def __init__(self, parent):
        super(AboutDialog, self).__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        information_label = QtWidgets.QLabel(self)
        information_label.setText('This application is awesome')

        ok_button = QtWidgets.QPushButton('Ok', self)    

        self.show()

class TrackmaniaManagerMainWindow(QtWidgets.QMainWindow):
    def __init__(self, c):
        super(TrackmaniaManagerMainWindow, self).__init__()
        self.setup_ui()
        self._c = c
        
    def setup_ui(self): 
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

        helpMenu = menubar.addMenu('&Help')
        helpMenu.addAction(about_action)

        self.toolbar = self.addToolBar('File management')
        self.toolbar.addAction(self.open_file_action)
        self.toolbar.addAction(self.save_file_action)
        self.toolbar.addAction(self.close_file_action)
        
        self.statusBar()
        #self.setGeometry(300, 300, 640, 480)
        self.setMinimumSize(640, 480)
        self.setWindowTitle('trackmania-manager')  
        self.setWindowIcon(QtGui.QIcon('trackmania-manager.png'))

    def open_file_slot(self):
        self._c.matchsettings_file, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open matchsettings file', 'c:\\nph\\tmnf\\gamedata\\tracks\\matchsettings',"Matchsettings files (*.txt)")
        self._handle_changed_vars()

    def save_file_slot(self):
        print('save file triggered')

    def close_file_slot(self):
        self._c.matchsettings_file = ''
        self._handle_changed_vars()

    def about_slot(self):
        about_dialog = AboutDialog(self)
        ret = about_dialog.exec_()

    def edit_settings_slot(self):
        print('edit settings triggered')

    def _handle_changed_vars(self):
        if self._c.matchsettings_file:
            self.close_file_action.setEnabled(True)
        elif not self.c.matchsettings_file:
            self.close_file_action.setEnabled(False)