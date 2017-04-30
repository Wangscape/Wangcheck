import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
excludes = [
  "_ssl",
  "unicodedata",
  "pyexpat",
  "_hashlib",
  "_bz2",
  "html",
  "logging",
  "pydoc_data",
  "unittest",
  "xml"
]
build_exe_options = {
    "packages": [],
    "excludes": excludes,
    "optimize": 2}

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None

setup(  name = "Wangcheck",
        version = "0.1",
        description = "Validate JSON configuration files for Wangscape",
        options = {"build_exe": build_exe_options},
        executables = [Executable("Wangcheck.py", base=base)])