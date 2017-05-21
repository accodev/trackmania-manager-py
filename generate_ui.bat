@echo off
pyrcc5 resources.qrc -o resources_rc.py >nul
pyuic5 mainwindow.ui -o ui_mainwindow.py >nul