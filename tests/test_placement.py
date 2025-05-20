from __future__ import annotations

import pytest

from src.utils.placement import (convert_placement, decide_placement,
                                 swap_placement)
from . import constant as c


def test_convert_placement():
    placement = [[1, 0], [1, 0]]
    services = [{"id": "service1"}, {"id": "service2"}]
    clusters = ["cluster1", "cluster2"]

    expected = {"service1": "cluster1", "service2": "cluster1"}

    result = convert_placement(placement, services, clusters)
    assert result == expected


def test_swap_placement():
    service_dict = {"service1": "cluster1", "service2": "cluster1"}
    expected = {"cluster1": ["service1", "service2"]}

    result = swap_placement(service_dict)
    assert result == expected


@pytest.mark.skip(reason="FIXME")
def test_decide_placement():
    placement = decide_placement(
        c.CLUSTER_CAPACITY_LIST,
        c.CLUSTER_ACCELERATION_LIST,
        c.CPU_LIMITS_LIST,
        c.ACCELERATION_LIST,
        c.REPLICAS_LIST,
        c.INITIAL_PLACEMENT,
    )
    expected = [[1, 0], [1, 0], [0, 1]]
    assert placement == expected
