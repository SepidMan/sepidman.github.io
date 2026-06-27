"""Resume pipeline package for validation, conversion, and PDF builds."""

from __future__ import annotations

import sys
from pathlib import Path
from types import ModuleType


def _prioritize_source_path() -> None:
    """Keep local compatibility shims ahead of site-packages on sys.path."""
    source_dir = Path(__file__).resolve().parent.parent
    source_dir_str = str(source_dir)
    if source_dir_str in sys.path:
        sys.path.remove(source_dir_str)
    sys.path.insert(0, source_dir_str)


def _install_ipython_display_shim() -> None:
    """Provide the tiny IPython surface that pyserials transitively imports."""
    if "IPython" in sys.modules:
        return

    display_module = ModuleType("IPython.display")

    class _RenderedContent:
        def __init__(self, content: str) -> None:
            self.content = content

    def _display(*_args: object, **_kwargs: object) -> None:
        return

    display_module.HTML = _RenderedContent
    display_module.Markdown = _RenderedContent
    display_module.display = _display

    ipython_module = ModuleType("IPython")
    ipython_module.display = display_module

    sys.modules["IPython"] = ipython_module
    sys.modules["IPython.display"] = display_module


_prioritize_source_path()
_install_ipython_display_shim()

__all__ = ["_install_ipython_display_shim", "_prioritize_source_path"]
