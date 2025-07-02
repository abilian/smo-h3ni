from utils.intent_translation import tranlsate_cpu, tranlsate_memory, tranlsate_storage


def test_translate_cpu():
    """Test CPU translation."""

    assert tranlsate_cpu('light') == 0.5
    assert tranlsate_cpu('medium') == 4


def test_translate_memory():
    """Test memory translation."""

    assert tranlsate_memory('small') == '1GiB'
    assert tranlsate_memory('large') == '8GiB'


def test_translate_storage():
    """Test storage translation."""

    assert tranlsate_storage('small') == '10GB'
    assert tranlsate_storage('medium') == '20GB'

