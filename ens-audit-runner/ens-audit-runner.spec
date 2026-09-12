# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller specification for the Windows ENS Audit Runner executable."""

from pathlib import Path

project_root = Path(__file__).resolve().parent
source_root = project_root / "src"
package_root = source_root / "ens_audit"

datas = [
    (str(package_root / "known_issues" / "known_issues.yaml"), "ens_audit/known_issues"),
    (str(package_root / "rules" / "ens-custom.yaml"), "ens_audit/rules"),
    (str(package_root / "rules" / "codeql-config.yml"), "ens_audit/rules"),
]

a = Analysis(
    [str(package_root / "__main__.py")],
    pathex=[str(source_root)],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="ENSAuditRunner",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
