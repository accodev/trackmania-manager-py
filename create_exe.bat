@echo off
pyinstaller -F __init__.py -w -p "venv\trackmania-manager\Lib\site-packages\PyQt5" -p "venv\trackmania-manager\Lib\site-packages\PyQt5\Qt\bin" -i "resources\icons\app.ico" --distpath "dist"