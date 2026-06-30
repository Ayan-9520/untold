"""Input sanitization unit tests."""

import pytest

from app.domain.security.sanitization import escape_html_output, reject_script_markup, sanitize_text


@pytest.mark.unit
def test_sanitize_text_strips_control_chars():
    assert sanitize_text("hello\x00world") == "helloworld"


@pytest.mark.unit
def test_sanitize_text_max_length():
    with pytest.raises(ValueError, match="exceeds"):
        sanitize_text("x" * 100, max_length=10)


@pytest.mark.unit
def test_reject_script_markup_blocks_script_tag():
    with pytest.raises(ValueError, match="disallowed"):
        reject_script_markup("<script>alert(1)</script>", field="prompt")


@pytest.mark.unit
def test_escape_html_output():
    assert escape_html_output('<img onerror="x">') == "&lt;img onerror=&quot;x&quot;&gt;"
