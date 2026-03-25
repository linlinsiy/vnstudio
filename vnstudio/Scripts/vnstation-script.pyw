#!C:\vnstudio\pythonw.exe
# EASY-INSTALL-ENTRY-SCRIPT: 'vnstation==2.4.6','gui_scripts','vnstation'
__requires__ = 'vnstation==2.4.6'
import re
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(
        load_entry_point('vnstation==2.4.6', 'gui_scripts', 'vnstation')()
    )
