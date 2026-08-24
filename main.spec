# main.spec
# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# Собираем все подмодули для selenium
selenium_hiddenimports = collect_submodules('selenium')
webdriver_hiddenimports = collect_submodules('webdriver_manager')

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        # Добавляем папки с кодом
        ('classes', 'classes'),
        ('utils', 'utils'),
    ],
    hiddenimports=[
        # Selenium и все его подмодули
        'selenium',
        'selenium.webdriver',
        'selenium.webdriver.common',
        'selenium.webdriver.chrome',
        'selenium.webdriver.chrome.options',
        'selenium.webdriver.chrome.service',
        'selenium.webdriver.support',
        'selenium.webdriver.support.ui',
        'selenium.webdriver.support.expected_conditions',
        'selenium.common',
        'selenium.common.exceptions',
        # WebDriver Manager
        'webdriver_manager',
        'webdriver_manager.chrome',
        'webdriver_manager.core',
        'webdriver_manager.core.download_manager',
        'webdriver_manager.core.manager',
        'webdriver_manager.core.utils',
        # Requests
        'requests',
        'requests.packages',
        'requests.packages.urllib3',
        # PyWinAuto
        'pywinauto',
        'pywinauto.application',
        'pywinauto.timings',
        'pywinauto.keyboard',
        # Другие библиотеки
        'pyperclip',
        'urllib3',
        'certifi',
        'charset_normalizer',
        'idna',
    ] + selenium_hiddenimports + webdriver_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='AIVideoDownloader',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)