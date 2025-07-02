from smo.utils.intent_translation import (
    translate_cpu,
    translate_memory,
    translate_storage,
)


def test_translate_cpu():
    """Test CPU translation."""

    assert translate_cpu("light") == 0.5
    assert translate_cpu("medium") == 4


def test_translate_memory():
    """Test memory translation."""

    assert translate_memory("small") == "1GiB"
    assert translate_memory("large") == "8GiB"


def test_translate_storage():
    """Test storage translation."""

    assert translate_storage("small") == "10GB"
    assert translate_storage("medium") == "20GB"
