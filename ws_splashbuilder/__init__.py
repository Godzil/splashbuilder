#!/usr/bin/env python3

try:
    from ._version import version as __version__
except ImportError:
    __version__ = "Untracked build"
    pass

from . import splashbuilder
from . import cel2wst
from . import map2wsm
