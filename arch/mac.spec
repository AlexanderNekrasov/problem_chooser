# -*- mode: python ; coding: utf-8 -*-
from arch import specdata

block_cipher = None


a = Analysis([specdata.Path.main],
             pathex=[specdata.Path.root],
             binaries=[],
             datas=specdata.datas,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='problem-chooser',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='problem-chooser')
app = BUNDLE(coll,
             name='problem-chooser.app',
             icon=specdata.Path.icon,
             bundle_identifier=None)
