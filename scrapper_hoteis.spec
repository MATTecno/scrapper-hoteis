# -*- mode: python ; coding: utf-8 -*-
import os
import site
from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

# Assets do customtkinter (temas, fontes, imagens)
ctk_datas = collect_data_files("customtkinter")

# Playwright driver (Node.js + pacote JS) — necessário para o sync_api funcionar
playwright_pkg = None
for sp in site.getsitepackages() + [site.getusersitepackages()]:
    candidate = os.path.join(sp, "playwright")
    if os.path.isdir(candidate):
        playwright_pkg = candidate
        break
if playwright_pkg is None:
    import playwright as _pw
    playwright_pkg = os.path.dirname(_pw.__file__)

playwright_driver_datas = [
    (os.path.join(playwright_pkg, "driver"), "playwright/driver"),
]

a = Analysis(
    ["app.py"],
    pathex=[],
    binaries=[],
    datas=ctk_datas + playwright_driver_datas,
    hiddenimports=[
        "customtkinter",
        "tkinter",
        "tkinter.ttk",
        "tkinter.messagebox",
        "tkinter.filedialog",
        "openpyxl",
        "playwright",
        "playwright.sync_api",
        "gui.app_window",
        "gui.worker",
        "gui.setup_screen",
        "scraper",
        "rate_shopper",
        "relatorio",
        "config",
        "version",
        "updater",
        "autostart",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=["hook_playwright_fix.py"],
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
    name="ScrapperHoteis",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
