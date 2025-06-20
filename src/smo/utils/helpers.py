"""Helper functions"""


def format_memory(bytes_value):
    """Convert bytes to multiples."""

    units = [("GiB", 1024**3), ("MiB", 1024**2), ("KiB", 1024), ("Bytes", 1)]
    for unit, factor in units:
        if bytes_value >= factor:
            value = bytes_value / factor
            return f"{value:.2f} {unit}"
    return f"{bytes_value} Bytes"
