"""Regression controls for the versioned source-text hash extractor."""

import importlib.util
from pathlib import Path

import pytest


_SOURCE = Path(__file__).resolve().parents[1] / "reports/reference-admission/source_text_hash.py"
_SPEC = importlib.util.spec_from_file_location("source_text_hash", _SOURCE)
_MODULE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODULE)


@pytest.mark.parametrize(
    "markup",
    [
        b"A<script>hidden</script>B",
        b"A<SCRIPT>hidden</SCRIPT>B",
        b"A<script >hidden</script >B",
        b"A<StYlE>hidden</sTyLe >B",
    ],
)
def test_script_and_style_content_is_omitted(markup):
    assert _MODULE.canonical_text(markup) == "AB"
