"""Locks the package version to a single source of truth.

The version appears in both ``setup.py`` and ``accessgrid/__init__.py``
(``__version__``). Drift between them is silent and ships bad metadata to
PyPI / pip-show / SDK consumers. This test fails the build if they disagree.
"""

import pathlib
import re

import accessgrid

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent


def _setup_py_version():
    text = (REPO_ROOT / "setup.py").read_text(encoding="utf-8")
    match = re.search(r'version\s*=\s*"([^"]+)"', text)
    assert match, "Could not find version= in setup.py"
    return match.group(1)


def test_setup_py_matches_dunder_version():
    assert _setup_py_version() == accessgrid.__version__
