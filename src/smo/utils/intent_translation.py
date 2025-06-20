from __future__ import annotations

CPU_MAPPING = {"light": 0.5, "small": 1, "medium": 4, "large": 8}

MEMORY_MAPPING = {"light": "500MiB", "small": "1GiB", "medium": "2GiB", "large": "8GiB"}

STORAGE_MAPPING = {"small": "10GB", "medium": "20GB", "large": "40GB"}


def translate_cpu(cpu_class):
    return CPU_MAPPING[cpu_class]


def translate_memory(memory_class):
    return MEMORY_MAPPING[memory_class]


def translate_storage(storage_class):
    return STORAGE_MAPPING[storage_class]
