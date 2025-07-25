# hooks/hook-PySide6.py
from PyInstaller.utils.hooks import copy_metadata, collect_dynamic_libs

# This hook is often needed to correctly bundle PySide6's dependencies,
# especially for networking and SSL which can cause the "ordinal not found" error.
datas = copy_metadata('PySide6')
binaries = collect_dynamic_libs('PySide6')
