"""Simplicio native Rust performance layer.

The compiled PyO3 extension is importable as ``simplicio._core``. Vendored +
rebranded from headroom (Apache-2.0); see ../../NOTICE.
"""

from . import _core as _core  # noqa: F401

__all__ = ["_core"]
