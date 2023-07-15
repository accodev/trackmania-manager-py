@echo off
pyinstaller -F __init__.py -p . --distpath "dist" -i "resources\icons\app.ico" -w -n "trackmania-manager-py"