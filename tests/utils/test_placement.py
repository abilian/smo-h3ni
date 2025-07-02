import pytest
import numpy as np
from utils.placement import swap_placement, convert_placement, decide_placement, calculate_naive_placement


def test_swap_placement():
    services = {'svc1': 'c1', 'svc2': 'c2', 'svc3': 'c1'}
    expected = {'c1': ['svc1', 'svc3'], 'c2': ['svc2']}
    assert swap_placement(services) == expected


def test_convert_placement():
    placement = [[1, 0], [0, 1]]
    services = [{'id': 'svc1'}, {'id': 'svc2'}]
    clusters = ['c1', 'c2']
    expected = {'svc1': 'c1', 'svc2': 'c2'}
    assert convert_placement(placement, services, clusters) == expected


def test_decide_placement_basic():
    cluster_capacities = [4, 4]
    cluster_acceleration = [1, 1]
    cpu_limits = [2, 2]
    acceleration = [0, 1]
    replicas = [1, 2]
    current_placement = [[1, 0], [1, 0]]

    result = decide_placement(
        cluster_capacities,
        cluster_acceleration,
        cpu_limits,
        acceleration,
        replicas,
        current_placement
    )

    assert result == [[0, 1], [1, 0]]


def test_calculate_naive_placement_valid():
    cluster_capacities = [4, 4]
    cluster_accelerations = [1, 0]
    cpu_limits = [2, 1]
    accelerations = [1, 0]
    replicas = [1, 2]

    placement = calculate_naive_placement(
        cluster_capacities,
        cluster_accelerations,
        cpu_limits,
        accelerations,
        replicas
    )

    assert placement == [[1, 0], [1, 0]]


def test_calculate_naive_placement_single_service_too_large():
    cluster_capacities = [2]
    cluster_accelerations = [1]
    cpu_limits = [3]
    accelerations = [0]
    replicas = [1]

    with pytest.raises(ValueError, match="cannot fit into any cluster"):
        calculate_naive_placement(
            cluster_capacities,
            cluster_accelerations,
            cpu_limits,
            accelerations,
            replicas
        )


def test_calculate_naive_placement_insufficient_total_capacity():
    cluster_capacities = [2, 2]
    cluster_accelerations = [1, 1]
    cpu_limits = [2, 3]
    accelerations = [0, 1]
    replicas = [1, 1]

    with pytest.raises(ValueError, match="A single service cannot fit into any cluster. " \
    "Increase cluster capacity or reduce service requirements."):
        calculate_naive_placement(
            cluster_capacities,
            cluster_accelerations,
            cpu_limits,
            accelerations,
            replicas
        )
