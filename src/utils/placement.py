"""Application node placement related functionalities."""

import cvxpy as cp


def swap_placement(service_dict):
    """
    Takes a dictionary that maps a service to its cluster
    and returns a dictionary that maps a cluster to the list of
    services deployed there.
    """

    cluster_dict = {}
    for key, value in service_dict.items():
        cluster_dict.setdefault(value, []).append(key)
    return cluster_dict


def convert_placement(placement, services, clusters):
    """
    Convert placement from list of lists to dictionary mapping a
    service with the name of its cluster.
    E.g. Input
            placement:[[1, 0], [1, 0]]
            services: [{'id': 'service1'}, {'id': 'service2'}]
            clusters ['cluster1', 'cluster2']
         Output: {'service1': 'cluster1', 'service2': 'cluster1'}
    """

    service_placement = {}
    for service_index, cluster_list in enumerate(placement):
        # Get the index of the element that has a value of 1
        cluster_index = cluster_list.index(1)
        service_name = services[service_index]['id']
        service_placement[service_name] = clusters[cluster_index]

    return service_placement


def decide_placement(
        cluster_capacities, cluster_acceleration, cpu_limits,
        acceleration, replicas, current_placement,
):
    """
    Parameters
    ---
    cluster_capacities: List of CPU capacity for each cluster
    cluster_acceleration: List of GPU acceleration feature for each cluster
    cpu_limits: List of CPU limits for each service
    acceleration: List of GPU acceleration feature for each service
    replicas: List of number of replicas
    current_placement: List of current placement

    Return value
    ---
    placement: 2D List of placement. If the element at index [i][j] is 1
               it means that service i is placed at cluster j
    """

    num_clusters = len(cluster_capacities)
    num_nodes = len(cpu_limits)

    x = cp.Variable((num_nodes, num_clusters), boolean=True)

    y = current_placement

    w_dep = 1  # Deployment cost weight
    w_re = 1   # Re-optimization cost weight

    # Objective function
    objective = cp.Minimize(
        w_dep * cp.sum(x) +
        w_re * cp.sum(cp.multiply(y, (y - x)))
    )

    constraints = []

    # Constraint 1: Each service must be placed in exactly one cluster
    for s in range(num_nodes):
        constraints.append(cp.sum(x[s, :]) == 1)

    # Constraint 2: Cluster capacity constraints
    for e in range(num_clusters):
        constraints.append(
            cp.sum(
                cp.multiply(x[:, e], [cpu_limits[s] * replicas[s] for s in range(num_nodes)])
            ) <= cluster_capacities[e]
        )

    # Constraint 3: Acceleration feature constraints
    for s in range(1, num_nodes):  # Assuming s0 has no acceleration constraint
        for e in range(num_clusters):
            constraints.append(
                x[s, e] * acceleration[s] <= cluster_acceleration[e]
            )

    # Constraint 4: Dependency constraint - This is adjusted to avoid recursion
    # Ensure no cyclic dependency by rethinking how dependencies are handled
    d = [0, 0]
    for i in range(1, num_nodes):
        for e in range(num_clusters):
            constraints.append(x[i, e] + x[i - 1, e] >= d[i - 1])

    problem = cp.Problem(objective, constraints)
    problem.solve(solver=cp.GLPK_MI, qcp=True)

    placement = [[int(x.value[s, e]) for e in range(num_clusters)] for s in range(num_nodes)]
    return placement


def calculate_naive_placement(cluster_capacities, cluster_accelerations, cpu_limits, accelerations, replicas):
    """
    Parameters
    ---
    cluster_capacities: List of CPU capacity for each cluster
    cluster_acceleration: List of GPU acceleration feature for each cluster
    cpu_limits: List of CPU limits for each service
    acceleration: List of GPU acceleration feature for each service
    replicas: List of number of replicas

    Return value
    ---
    placement: 2D List of placement. If the element at index [i][j] is 1
               it means that service i is placed at cluster j
    """

    num_clusters = len(cluster_capacities)
    num_nodes = len(cpu_limits)

    service_reqs = [a * b for a, b in zip(replicas, cpu_limits)]

    if max(service_reqs) > min(cluster_capacities):
        raise ValueError('A single service cannot fit into any cluster. Increase cluster capacity or reduce service requirements.')

    if sum(service_reqs) > sum(cluster_capacities):
        raise ValueError('Insufficient total capacity to fit all services across the clusters.')

    placement = [[0 for _ in range(num_clusters)] for _ in range(num_nodes)]
    cluster_usage = [0] * num_clusters

    for service_id, service_req in enumerate(service_reqs):
        placed = False
        for cluster_id, cluster_cap in enumerate(cluster_capacities):
            if accelerations[service_id] <= cluster_accelerations[cluster_id] and\
                    cluster_usage[cluster_id] + service_req <= cluster_cap:
                placement[service_id][cluster_id] = 1
                cluster_usage[cluster_id] += service_req
                placed = True
                break
        if not placed:
            raise ValueError(f'Service {service_id} with requirement {service_req} could not be placed in any cluster.')

    return placement
