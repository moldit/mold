"""
@var script_root: A L{FilePath} of the root utility script directory.
"""

from twisted.python.filepath import FilePath

_mold_root = FilePath(__file__).parent()

script_root = _mold_root.child('util_scripts')


