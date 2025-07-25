# hooks/hook-PySide6.py
from PyInstaller.utils.hooks import copy_metadata, collect_dynamic_libs

# datas = copy_metadata('PySide6') # Commented out to bypass the metadata error
binaries = collect_dynamic_libs('PySide6')
datas = [] # Add this line to ensure 'datas' is defined
