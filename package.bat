echo Please ensure PYTHON is set to the directory of Python installation at version 3.6.
set OLD_PATH=%PATH%
PATH=%PYTHON%;%PYTHON%\Scripts;%PATH%
python --version
pip --version
pip install cx_Freeze
pip install -r requirements.txt
python setup.py build_exe
cd build
move exe.win32-3.6 Wangcheck
7z a Wangcheck.zip Wangcheck
cd ..
PATH=%OLD_PATH%
