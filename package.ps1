echo "Please ensure PYTHON is set to the directory of Python installation at version 3.6."
$env:OldPath = $env:Path
$env:Path = "$env:PYTHON;$env:PYTHON\Scripts;$env:OldPath"
python --version
pip --version
pip install cx_Freeze
pip install -r requirements.txt
python setup.py build_exe
cd build
move exe.win32-3.6 Wangcheck
mkdir Wangcheck\licenses
Start-FileDownload "https://bitbucket.org/ericvsmith/toposort/raw/default/LICENSE.txt" -FileName "Wangcheck\licenses\LICENSE_toposort.txt"
Start-FileDownload "https://bitbucket.org/ericvsmith/toposort/raw/default/NOTICE" -FileName "Wangcheck\licenses\NOTICE_toposort.txt"
7z a Wangcheck.zip Wangcheck
cd ..
$env:Path=$env:OldPath
