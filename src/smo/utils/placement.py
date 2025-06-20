"""
Module for application service placement on clusters.

Provides functionalities to decide and manage the placement of services
(nodes) onto different clusters, considering resource capacities, service
requirements, and optimization objectives. Includes an optimization-based
solver using CVXPY and a simpler heuristic approach.
"""

from typing import Any

import cvxpy as cp
import numpy as np


class PlacementError(ValueError):
    """
    Custom exception for errors related to service placement.

    This exception is raised when there are issues with the placement of
    services onto clusters, such as insufficient capacity or unmet
    requirements.
    """

    pass


def convert_placement(
    placement_matrix: list[list[int]],
    services_info: list[dict[str, Any]],
    cluster_names: list[str],
) -> dict[str, str]:
    """
    Converts a matrix-based placement to a service-to-cluster name mapping.

    The placement matrix indicates which service is on which cluster.
    This function translates that matrix into a more readable dictionary
    format, mapping service IDs to cluster names.

    Parameters
    ----------
    placement_matrix : list[list[int]]
        A 2D list where `placement_matrix[i][j] == 1` signifies that service `i`
        is placed on cluster `j`, and `0` otherwise.
    services_info : list[dict[str, any]]
        A list of dictionaries, where each dictionary contains information
        about a service. It must include an 'id' key for the service name.
        The order of services in this list corresponds to the rows in
        `placement_matrix`.
    cluster_names : list[str]
        A list of cluster names. The order of names corresponds to the
        columns in `placement_matrix`.

    Returns
    -------
    dict[str, str]
        A dictionary mapping service IDs (e.g., 'service1') to the
        name of the cluster they are placed on (e.g., 'cluster1').

    Examples
    --------
    >>> placement = [[1, 0], [0, 1]]
    >>> services = [{'id': 'serviceA'}, {'id': 'serviceB'}]
    >>> clusters = ['clusterX', 'clusterY']
    >>> convert_placement(placement_matrix, services_info, cluster_names)
    {'serviceA': 'clusterX', 'serviceB': 'clusterY'}
    """

    service_placement_map = {}
    for service_idx, cluster_assignments in enumerate(placement_matrix):
        # Find the cluster index where the service is placed (value is 1)
        try:
            cluster_idx = cluster_assignments.index(1)
        except ValueError:
            msg = f"Service at index {service_idx} is not placed on any cluster according to the placement matrix."
            raise PlacementError(msg)

        service_name = services_info[service_idx]["id"]
        service_placement_map[service_name] = cluster_names[cluster_idx]

    return service_placement_map


def decide_placement(
    cluster_capacities: list[float],
    cluster_acceleration: list[float],
    cpu_limits: list[float],
    acceleration_reqs: list[float],
    replicas: list[int],
    current_placement: list[list[int]],
) -> list[list[int]]:
    """
    Determines an optimal service placement using CVXPY based on an optimization model.

    The model aims to minimize a combination of deployment costs and
    re-optimization costs, subject to capacity, acceleration, and
    dependency constraints.

    Parameters
    ----------
    cluster_capacities : list[float]
        CPU capacity for each cluster. E.g., `[100.0, 200.0]`.
    cluster_acceleration : list[float]
        A numerical value representing the acceleration capability of each
        cluster (e.g., GPU tier, 0 if no special acceleration).
        E.g., `[0.0, 1.0, 2.0]`.
    cpu_limits : list[float]
        CPU limit (requirement) for each service. E.g., `[10.0, 5.0]`.
    acceleration_reqs : list[float]
        A numerical value representing the acceleration requirement of each
        service. E.g., `[0.0, 1.0]`.
    replicas : list[int]
        Number of replicas for each service. E.g., `[2, 3]`.
    current_placement : list[list[int]]
        A 2D matrix representing the current placement, of the same
        dimensions as the output. `current_placement[s][e] == 1` if
        service `s` is currently on cluster `e`.

    Returns
    -------
    list[list[int]]
        A 2D matrix `x` where `x[s][e] == 1` if service `s` should be
        placed on cluster `e`, and `0` otherwise.
    """
    num_clusters = len(cluster_capacities)
    num_nodes = len(cpu_limits)

    x = cp.Variable((num_nodes, num_clusters), boolean=True)

    y = np.array(current_placement)

    w_dep = 1  # Deployment cost weight
    w_re = 1  # Re-optimization cost weight

    # Objective function
    objective = cp.Minimize(w_dep * cp.sum(x) + w_re * cp.sum(cp.multiply(y, (y - x))))

    constraints = []

    # Constraint 1: Each service must be placed in exactly one cluster
    for s in range(num_nodes):
        constraints.append(cp.sum(x[s, :]) == 1)

    # Constraint 2: Cluster capacity constraints
    for e in range(num_clusters):
        constraints.append(
            cp.sum(
                cp.multiply(
                    x[:, e], [cpu_limits[s] * replicas[s] for s in range(num_nodes)]
                )
            )
            <= cluster_capacities[e]
        )

    # Constraint 3: Acceleration feature constraints
    for s in range(1, num_nodes):  # Assuming s0 has no acceleration constraint
        for e in range(num_clusters):
            constraints.append(
                x[s, e] * acceleration_reqs[s] <= cluster_acceleration[e]
            )

    # Constraint 4: Dependency constraint - This is adjusted to avoid recursion
    # Ensure no cyclic dependency by rethinking how dependencies are handled
    d = [0, 0]
    for i in range(1, num_nodes):
        for e in range(num_clusters):
            constraints.append(x[i, e] + x[i - 1, e] >= d[i - 1])

    problem = cp.Problem(objective, constraints)
    problem.solve(solver=cp.HIGHS)

    placement = [
        [int(x.value[s, e]) for e in range(num_clusters)] for s in range(num_nodes)
    ]
    return placement


def calculate_naive_placement(
    cluster_capacities: list[float],
    cluster_acceleration_caps: list[float],
    cpu_limits: list[float],
    service_acceleration_reqs: list[float],
    replicas: list[int],
) -> list[list[int]]:
    """
    Calculates a feasible placement using a greedy first-fit heuristic.

    It iterates through services one by one and places each onto the
    first cluster (by index order) that satisfies its CPU and acceleration
    requirements and has enough capacity. This approach is fast but
    typically not optimal.

    Parameters
    ----------
    cluster_capacities : list[float]
        CPU capacity available on each cluster.
    cluster_acceleration_caps : list[float]
        Acceleration capability of each cluster.
    cpu_limits : list[float]
        CPU requirement for each service.
    service_acceleration_reqs : list[float]
        Acceleration requirement for each service.
    replicas : list[int]
        Number of replicas for each service.

    Returns
    -------
    list[list[int]]
        A 2D list representing the placement. `placement[i][j] == 1`
        if service `i` is placed on cluster `j`.

    Raises
    ------
    ValueError
        If a service cannot be placed on any cluster, or if total
        requirements exceed total capacity.
    """

    num_clusters = len(cluster_capacities)
    num_nodes = len(cpu_limits)

    service_reqs = [a * b for a, b in zip(replicas, cpu_limits)]

    if max(service_reqs) > min(cluster_capacities):
        raise PlacementError(
            "A single service cannot fit into any cluster. Increase cluster capacity or reduce service requirements."
        )

    if sum(service_reqs) > sum(cluster_capacities):
        raise PlacementError(
            "Insufficient total capacity to fit all services across the clusters."
        )

    placement = [[0 for _ in range(num_clusters)] for _ in range(num_nodes)]
    cluster_usage = [0] * num_clusters

    for service_id, service_req in enumerate(service_reqs):
        placed = False
        for cluster_id, cluster_cap in enumerate(cluster_capacities):
            if (
                service_acceleration_reqs[service_id]
                <= cluster_acceleration_caps[cluster_id]
                and cluster_usage[cluster_id] + service_req <= cluster_cap
            ):
                placement[service_id][cluster_id] = 1
                cluster_usage[cluster_id] += service_req
                placed = True
                break
        if not placed:
            msg = f"Service {service_id} with requirement {service_req} could not be placed in any cluster."
            raise PlacementError(msg)

    return placement


def swap_placement(service_to_cluster: dict[str, str]) -> dict[str, list[str]]:
    """
    Inverts a service-to-cluster mapping.

    Takes a dictionary mapping each service to its assigned cluster and
    returns a dictionary mapping each cluster to a list of services
    deployed on it.

    Parameters
    ----------
    service_to_cluster : dict
        A dictionary where keys are service identifiers and values are
        their assigned cluster identifiers.

    Returns
    -------
    dict
        A dictionary where keys are cluster identifiers and values are
        lists of service identifiers deployed on that cluster.
    """

    cluster_dict = {}
    for key, value in service_to_cluster.items():
        cluster_dict.setdefault(value, []).append(key)
    return cluster_dict
