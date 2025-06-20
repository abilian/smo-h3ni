"""Replica scaling algorithm."""

import time

import requests
import cvxpy as cp

from utils.karmada_helper import KarmadaHelper
from utils.prometheus_helper import PrometheusHelper


def scaling_loop(
    graph_name,
    acceleration,
    alpha,
    beta,
    cluster_capacity,
    cluster_acceleration,
    maximum_replicas,
    managed_services,
    decision_interval,
    config_file_path,
    prometheus_host,
    stop_event,
):
    """Runs the scaling algorithm periodically."""

    karmada_helper = KarmadaHelper(config_file_path)
    prometheus_helper = PrometheusHelper(prometheus_host, decision_interval)
    while True:
        previous_replicas = [
            karmada_helper.get_replicas(service) for service in managed_services
        ]
        if None in previous_replicas:
            time.sleep(5)
        else:
            break

    previous_replicas = [
        karmada_helper.get_replicas(service) for service in managed_services
    ]
    cpu_limits = [karmada_helper.get_cpu_limit(service) for service in managed_services]

    while not stop_event.is_set():
        request_rates = []
        for service in managed_services:
            if service == "image-compression-vo":
                request_rates.append(
                    prometheus_helper.get_request_rate("noise-reduction")
                )
            else:
                request_rates.append(prometheus_helper.get_request_rate(service))
        print(
            request_rates,
            previous_replicas,
            cpu_limits,
            acceleration,
            alpha,
            beta,
            cluster_capacity,
            cluster_acceleration,
            maximum_replicas,
        )

        new_replicas = decide_replicas(
            request_rates,
            previous_replicas,
            cpu_limits,
            acceleration,
            alpha,
            beta,
            cluster_capacity,
            cluster_acceleration,
            maximum_replicas,
        )
        if new_replicas is None:
            requests.get(f"http://localhost:8000/graphs/{graph_name}/placement")
        else:
            for idx, replicas in enumerate(new_replicas):
                karmada_helper.scale_deployment(managed_services[idx], replicas)
        print(new_replicas)

        previous_replicas = new_replicas
        time.sleep(decision_interval)


def decide_replicas(
    request_rates,
    previous_replicas,
    cpu_limits,
    acceleration,
    alpha,
    beta,
    cluster_capacity,
    cluster_acceleration,
    maximum_replicas,
):
    """
    Parameters
    ---
    request_rates: List of incoming rates of requests
    previous_replicas: List of previous replicas
    cpu_limits: List of CPU limits
    acceleration: List of acceleration flags
    alpha: Coefficient of the equation y = a * x + b
           where x is the number of replicas and y is the
           maximum number of request the service can handle
    beta: Coefficient in the same equation as alpha mentioned above
    cluster_capacity: Cluster CPU capacity in cores
    cluster_acceleration: Acceleration enabled for cluster flag

    Return value
    ---
    solution: List with replicas for each service
    """

    num_nodes = len(previous_replicas)

    # Decision variables
    r_current = [
        cp.Variable(integer=True, name=f"r_current_{s}") for s in range(num_nodes)
    ]
    abs_diff = [
        cp.Variable(nonneg=True, name=f"abs_diff_{s}") for s in range(num_nodes)
    ]

    w_util = 0.4
    w_trans = 0.4

    # Max values for normalization
    max_util_cost = max(maximum_replicas[s] * cpu_limits[s] for s in range(num_nodes))
    max_trans_cost = maximum_replicas

    constraints = []

    # Absolute difference constraints
    for s in range(num_nodes):
        constraints.append(abs_diff[s] >= previous_replicas[s] - r_current[s])
        constraints.append(abs_diff[s] >= -(previous_replicas[s] - r_current[s]))

    # Cluster CPU capacity constraint
    constraints.append(
        cp.sum([cpu_limits[s] * r_current[s] for s in range(num_nodes)])
        <= cluster_capacity
    )

    # Per-node constraints
    for s in range(num_nodes):
        constraints.append(acceleration[s] <= cluster_acceleration)
        constraints.append(alpha[s] * r_current[s] + beta[s] >= request_rates[s])
        constraints.append(r_current[s] >= 1)

    objective = cp.Minimize(
        w_util
        * cp.sum([
            r_current[s] * cpu_limits[s] / max_util_cost for s in range(num_nodes)
        ])
        + w_trans * cp.sum([abs_diff[s] / max_trans_cost[s] for s in range(num_nodes)])
    )

    problem = cp.Problem(objective, constraints)

    problem.solve(solver=cp.HIGHS)

    if problem.status == cp.OPTIMAL:
        solution = [int(round(r.value)) for r in r_current]
        return solution
    else:
        return None
