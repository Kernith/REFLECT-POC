PyInstaller Command (run in venv):
`pyinstaller --onefile --windowed --icon=images/icon.png --add-data "images;images" --add-data "config.json;." --add-data "pages;pages" --add-data "widgets;widgets" --add-data "utils;utils" main.py`

with hidden imports
`pyinstaller --onefile --windowed --icon=images/icon.png --add-data "images;images" --add-data "config.json;." --add-data "pages;pages" --add-data "widgets;widgets" --add-data "utils;utils" --add-data "venv/Lib/site-packages/matplotlib/mpl-data;mpl-data"  --hidden-import=_ctypes --hidden-import=pkg_resources.py2_warn --hidden-import=matplotlib.backends.backend_qt5agg main.py`