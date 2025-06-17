# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['account-gen-gui.py'],
    pathex=[],
    binaries=[],
    datas=[('pretendo.ico', '.'), ('countries.json', '.'), ('CTkScrollableDropdown', '.'), ('CTkMessagebox', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['numpy', 'asyncio'],
    noarchive=False,
    optimize=2,
)
pyz = PYZ(a.pure)

# Since we assume most people are on Windows 10/11 anyway remove unessesary dlls
exclude_dll_prefixes = [
    "api-ms-win-core-console",
    "api-ms-win-core-datetime",
    "api-ms-win-core-debug",
    "api-ms-win-core-errorhandling",
    "api-ms-win-core-file",
    "api-ms-win-core-handle",
    "api-ms-win-core-heap",
    "api-ms-win-core-interlocked",
    "api-ms-win-core-libraryloader",
    "api-ms-win-core-localization",
    "api-ms-win-core-memory",
    "api-ms-win-core-namedpipe",
    "api-ms-win-core-processenvironment",
    "api-ms-win-core-processthreads",
    "api-ms-win-core-profile",
    "api-ms-win-core-rtlsupport",
    "api-ms-win-core-string",
    "api-ms-win-core-synch",
    "api-ms-win-core-sysinfo",
    "api-ms-win-core-timezone",
    "api-ms-win-core-util",
    "api-ms-win-crt-conio",
    "api-ms-win-crt-convert",
    "api-ms-win-crt-environment",
    "api-ms-win-crt-filesystem",
    "api-ms-win-crt-heap",
    "api-ms-win-crt-locale",
    "api-ms-win-crt-math",
    "api-ms-win-crt-private",
    "api-ms-win-crt-process",
    "api-ms-win-crt-runtime",
    "api-ms-win-crt-stdio",
    "api-ms-win-crt-string",
    "api-ms-win-crt-time",
    "api-ms-win-crt-utility",
    "ucrtbase",
]

a.binaries = [
    b for b in a.binaries if not any(b[0].startswith(prefix) for prefix in exclude_dll_prefixes)
]

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Pretendo Account Generator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['pretendo.ico'],
)