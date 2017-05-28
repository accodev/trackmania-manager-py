@echo off
pyrcc5 resources.qrc -o resources_rc.py >nul
pyuic5 mainwindow.ui -o ui_mainwindow.py >nul
pyuic5 aboutdialog.ui -o ui_aboutdialog.py >nul
pyuic5 optionsdialog.ui -o ui_optionsdialog.py >nul