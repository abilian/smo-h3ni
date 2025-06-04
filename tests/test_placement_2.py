import pytest
from smo.utils import placement
from smo.utils.placement import PlacementError


# --- Tests for swap_placement ---
def test_swap_placement():
    """Tests the swap_placement function for correct dictionary inversion."""
    service_map = {'serviceA': 'cluster1', 'serviceB': 'cluster1', 'serviceC': 'cluster2'}
    expected_cluster_map = {'cluster1': ['serviceA', 'serviceB'], 'cluster2': ['serviceC']}

    cluster_map = placement.swap_placement(service_map)

    # Sort lists in the actual and expected results for comparison
    # if order within the list doesn't matter and isn't guaranteed.
    # In this case, setdefault().append() preserves insertion order per key.
    for key in expected_cluster_map:
        if key in cluster_map:
            cluster_map[key].sort()
            expected_cluster_map[key].sort()

    assert cluster_map == expected_cluster_map


# --- Tests for convert_placement ---
def test_convert_placement_valid_input():
    """Tests convert_placement with a valid placement matrix."""
    placement_mat = [[1, 0, 0], [0, 1, 0], [1, 0, 0]]
    services_info_list = [{'id': 'app1-svc1'}, {'id': 'app1-svc2'}, {'id': 'app2-svc1'}]
    cluster_name_list = ['kube-main', 'gpu-cluster', 'edge-cluster']
    expected_map = {'app1-svc1': 'kube-main', 'app1-svc2': 'gpu-cluster', 'app2-svc1': 'kube-main'}

    converted_map = placement.convert_placement(placement_mat, services_info_list, cluster_name_list)
    assert converted_map == expected_map


def test_convert_placement_unplaced_service_raises_value_error():
    """Tests convert_placement raises PlacementError if a service is not placed."""
    placement_mat_unplaced = [[0, 0, 0], [0, 1, 0]]  # serviceX is not placed
    services_info_unplaced = [{'id': 'serviceX'}, {'id': 'serviceY'}]
    cluster_names_unplaced = ['clusterA', 'clusterB', 'clusterC']  # Ensure num_clusters matches matrix width

    with pytest.raises(PlacementError):
        placement.convert_placement(placement_mat_unplaced, services_info_unplaced, cluster_names_unplaced)


# --- Tests for decide_placement ---

def test_decide_placement_no_current_placement():
    """Tests decide_placement with no initial placement."""
    dp_cluster_caps = [10.0, 10.0]
    dp_cluster_accel = [0.0, 1.0]
    dp_cpu_limits = [2.0, 1.0, 3.0]
    dp_accel_reqs = [0.0, 1.0, 0.0]
    dp_replicas = [1, 2, 1]
    dp_current_placement = [[0, 0], [0, 0], [0, 0]]
    expected_optimal_placement = [[1, 0], [0, 1], [1, 0]]

    optimal_placement = placement.decide_placement(
        dp_cluster_caps, dp_cluster_accel, dp_cpu_limits,
        dp_accel_reqs, dp_replicas, dp_current_placement
    )
    assert optimal_placement == expected_optimal_placement


def test_decide_placement_with_suboptimal_current_placement():
    """Tests decide_placement with a suboptimal initial placement, expecting re-optimization."""
    dp_cluster_caps = [10.0, 10.0]
    dp_cluster_accel = [0.0, 1.0]
    dp_cpu_limits = [2.0, 1.0, 3.0]
    dp_accel_reqs = [0.0, 1.0, 0.0]  # Service 1 needs acceleration
    dp_replicas = [1, 2, 1]
    # Current placement: S0 on C0, S1 on C0 (violates accel for S1), S2 on C0
    dp_current_placement_suboptimal = [[1, 0], [1, 0], [1, 0]]
    expected_optimal_placement_reopt = [[1, 0], [0, 1], [1, 0]]

    optimal_placement_reopt = placement.decide_placement(
        dp_cluster_caps, dp_cluster_accel, dp_cpu_limits,
        dp_accel_reqs, dp_replicas, dp_current_placement_suboptimal
    )
    assert optimal_placement_reopt == expected_optimal_placement_reopt


# --- Tests for calculate_naive_placement ---
def test_calculate_naive_placement_feasible():
    """Tests calculate_naive_placement for a scenario where placement is feasible."""
    np_cluster_caps = [6.0, 7.0]
    np_cluster_accel = [0.0, 1.0]
    np_cpu_limits = [2.0, 3.0, 1.0]
    np_accel_reqs = [0.0, 1.0, 0.0]
    np_replicas = [1, 1, 2]
    expected_naive_placement = [[1, 0], [0, 1], [1, 0]]
    # Service total CPU: S0=2.0 (to C0), S1=3.0 (needs accel -> to C1), S2=2.0 (to C0)

    naive_placement = placement.calculate_naive_placement(
        np_cluster_caps, np_cluster_accel, np_cpu_limits,
        np_accel_reqs, np_replicas
    )
    assert naive_placement == expected_naive_placement


def test_calculate_naive_placement_insufficient_capacity_raises_value_error():
    """Tests calculate_naive_placement raises ValueError for insufficient capacity."""
    np_cpu_limits_tight = [5.0, 5.0]  # S0=5 CPU, S1=5 CPU
    np_replicas_tight = [1, 1]
    np_accel_reqs_tight = [0.0, 0.0]
    np_cluster_caps_tight = [7.0]  # Single cluster with 7 CPU
    np_cluster_accel_tight = [0.0]
    # S0 takes 5 CPU (C0 has 2 left). S1 needs 5 CPU but C0 only has 2 left.

    with pytest.raises(PlacementError):
        placement.calculate_naive_placement(
            np_cluster_caps_tight, np_cluster_accel_tight, np_cpu_limits_tight,
            np_accel_reqs_tight, np_replicas_tight
        )


def test_calculate_naive_placement_service_too_large_for_any_cluster():
    """Tests if a single service is too large for any cluster initially."""
    cluster_caps = [5.0, 4.0]
    cluster_accel = [0.0, 0.0]
    cpu_limits = [6.0]  # Service requires 6 CPU
    accel_reqs = [0.0]
    replicas = [1]

    with pytest.raises(PlacementError):
        placement.calculate_naive_placement(
            cluster_caps, cluster_accel, cpu_limits, accel_reqs, replicas
        )


def test_calculate_naive_placement_insufficient_total_capacity():
    """Tests if total service requirements exceed total cluster capacity."""
    cluster_caps = [5.0, 5.0]  # Total 10 CPU
    cluster_accel = [0.0, 0.0]
    cpu_limits = [4.0, 4.0, 3.0]  # Total 11 CPU
    accel_reqs = [0.0, 0.0, 0.0]
    replicas = [1, 1, 1]

    with pytest.raises(PlacementError):
        placement.calculate_naive_placement(
            cluster_caps, cluster_accel, cpu_limits, accel_reqs, replicas
        )
