"""Helper functions"""


def memory_to_bytes(memory_str):
    """Converts memory multiples to bytes"""

    units = {'Ki': 1024, 'Mi': 1024**2, 'Gi': 1024**3}
    for unit, multiplier in units.items():
        if memory_str.endswith(unit):
            return int(memory_str.replace(unit, '')) * multiplier
    raise ValueError(f'Unsupported memory unit in {memory_str}')


def format_memory(bytes_value):
    """Convert bytes to multiples."""

    units = [('GiB', 1024**3), ('MiB', 1024**2), ('KiB', 1024), ('Bytes', 1)]
    for unit, factor in units:
        if bytes_value >= factor:
            value = bytes_value / factor
            return f'{value:.2f} {unit}'
    return f'{bytes_value} Bytes'
