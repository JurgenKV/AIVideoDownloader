# VizardAuto.spec
# -*- mode: python ; coding: utf-8 -*-

hidden_imports = [
    # корневые модули
    'ai_config',
    'config',

    # utils
    'utils',
    'utils.pause_controller',
    'utils.path_utils',

    # classes
    'classes',
    'classes.ui',
    'classes.browser_manager',
    'classes.video_loader',
    'classes.email_manager',
    'classes.vizard_registrator',
    'classes.email_confirmer',
    'classes.vizard_manager',
    'classes.vizard_uploader',
    'classes.vizard_template_manager',
    'classes.vizard_downloader',

    # selenium + драйвер
    'selenium.webdriver.chrome.webdriver',
    'selenium.webdriver.chrome.service',
    'webdriver_manager',
    'webdriver_manager.chrome',

    # прочее
    'pyperclip',
    'pywinauto',
    'pywinauto.timings',
    'pywinauto.keyboard',
]

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=[],
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    name='VizardAuto',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,        # поставь True, если хочешь видеть консоль для отладки
    disable_windowed_traceback=False,
)

coll = COLLECT(exe, a.binaries, a.zipfiles, a.datas,
              strip=False, upx=True, name='VizardAuto')