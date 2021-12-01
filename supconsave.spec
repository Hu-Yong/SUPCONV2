# -*- mode: python -*-

block_cipher = None


a = Analysis(['supconsave.py'],
             pathex=['C:\\Users\\15656\\Desktop\\SUPCONV2'],
             binaries=[],
             datas=[],
             hiddenimports=['email.mime.message', 'email.mime.image', 'email.mime.text', 'email.mime.multipart', 'email.mime.audio', 'email.mime.base', 'email.mime.application', 'email.mime.nonmultipart'],
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
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='supconsave',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True )
