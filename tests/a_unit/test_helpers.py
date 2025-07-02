from smo.utils.helpers import format_memory


def test_format_memory():
    """Test format_memory function."""

    assert format_memory(1073741824) == "1.00 GiB"
    assert format_memory(1048576) == "1.00 MiB"
    assert format_memory(1024) == "1.00 KiB"
    assert format_memory(512) == "512.00 Bytes"
