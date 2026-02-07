## 

## 打包
```shell script
pyinstaller -wF -i icon.ico run.py --add-data "icon.ico;." --upx-dir D:\code\python\z_logon6\ --clean
pyinstaller run.spec --upx-dir E:\code\python\pyqt6\ --clean
```

## 或者使用下面命令
```shell
pyinstaller run.spec
```
- 文件 run.spec
```text
# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['run.py'],
    pathex=['D:\code\python\z_logon8'],
    binaries=[],
    datas=[('icon.ico', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='run',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['icon.ico'],
)

```