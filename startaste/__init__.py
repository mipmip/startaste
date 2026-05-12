from __future__ import annotations

try:
    from importlib.metadata import version
    __version__ = version("startaste")
except Exception:
    import pathlib
    __version__ = (pathlib.Path(__file__).parent.parent / "VERSION").read_text().strip()
__license__ = "BSD"
__copyright__ = "Copyright 2013-2014, Luciano Fiandesio"
__author__ = "Luciano Fiandesio <http://fiandes.io/> & John David Pressman <http://jdpressman.com> & Kraktus"
