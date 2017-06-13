# -*- mode: python -*-

block_cipher = None


a = Analysis(['__init__.py'],
             pathex=['..\\venv\\trackmania-manager\\Lib\\site-packages\\PyQt5', '..\\venv\\trackmania-manager\\Lib\\site-packages\\PyQt5\\Qt\\bin', 'E:\\Development\\py\\trackmania-manager'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='__init__',
          debug=False,
          strip=False,
          upx=True,
          console=False , icon='resources\\icons\\app.ico')
