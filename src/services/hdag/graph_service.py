"""Application graph deployment business logic."""

import subprocess
import tempfile
import threading
from os import path, walk

import yaml
from flask import current_app
from werkzeug.exceptions import BadRequest, NotFound

from models import db, Cluster, Graph, Service
from utils.grafana_helper import GrafanaHelper
from utils.karmada_helper import KarmadaHelper
from utils.prometheus_helper import PrometheusHelper
from utils.placement import convert_placement, decide_placement, swap_placement, calculate_naive_placement
from utils.scaling import scaling_loop
from utils.intent_translation import tranlsate_cpu, tranlsate_memory, tranlsate_storage


background_scaling_threads = {}
stop_events = {}


def fetch_project_graphs(project):
    """Retrieves all the descriptors of a project"""

    graphs = db.session.query(Graph).filter_by(project=project).all()
    project_graphs = [graph.to_dict() for graph in graphs]

    return project_graphs


def deploy_graph(project, graph_descriptor):
    """
    Instantiates an application graph by using Helm to
    deploy each service's artifact.
    """

    grafana_helper = GrafanaHelper(
        current_app.config['GRAFANA_HOST'], current_app.config['GRAFANA_USERNAME'],
        current_app.config['GRAFANA_PASSWORD']
    )
    prom_helper = PrometheusHelper(current_app.config['PROMETHEUS_HOST'])

    hdag_config = graph_descriptor
    name = hdag_config['id']

    graph = db.session.query(Graph).filter_by(name=name).first()
    if graph is not None:
        raise BadRequest(f'Graph with name {name} already exists')

    graph = Graph(
        name=name,
        graph_descriptor=graph_descriptor,
        project=project,
        status='Running',
        grafana=None
    )
    db.session.add(graph)
    db.session.commit()

    background_scaling_threads[name] = [None, None]
    stop_events[name] = [threading.Event(), threading.Event()]

    services = hdag_config['services']
    cpu_limits = [tranlsate_cpu(service['deployment']['intent']['compute']['cpu']) for service in services]
    acceleration_list = [1 if service['deployment']['intent']['compute']['gpu']['enabled'] == 'True' else 0 for service in services]
    replicas = [1 for _ in services]

    available_clusters = db.session.query(Cluster).filter_by(availability=True)
    cluster_list = [cluster.name for cluster in available_clusters]
    cluster_capacity = {cluster.name: cluster.available_cpu for cluster in available_clusters}
    cluster_acceleration = {cluster.name: cluster.acceleration for cluster in available_clusters}
    cluster_capacity_list = [value for value in cluster_capacity.values()]
    cluster_acceleration_list = [value for value in cluster_acceleration.values()]
    placement = calculate_naive_placement(
        cluster_capacity_list, cluster_acceleration_list, cpu_limits, acceleration_list, replicas
    )
    graph.placement = placement


    service_placement = convert_placement(placement, services, cluster_list)
    cluster_placement = swap_placement(service_placement)
    import_clusters = create_service_imports(services, service_placement)

    svc_names = []
    for service in services:
        alert = {}
        name = service['id']
        svc_names.append(name)
        artifact = service['artifact']
        artifact_ref = artifact['ociImage']
        implementer = artifact['ociConfig']['implementer']
        artifact_type = artifact['ociConfig']['type']
        values_overwrite = artifact['valuesOverwrite']
        placement_dict = values_overwrite

        conditional_deployment = False
        deployment_trigger = service['deployment']['trigger']
        if 'event' in deployment_trigger:
            conditional_deployment = True
            deployment_condition = deployment_trigger['event']['condition']
            events = deployment_trigger['event']['events']
            for event in events:
                sources = event['source']
                event_id = event['id']
                event_condition = event['condition']
                prom_query = event_condition['promQuery']
                grace_period = event_condition['gracePeriod']
                description = event_condition['description']

                alert = create_alert(event_id, prom_query, grace_period, description, name)
                prom_helper.update_alert_rules(alert, 'add')

        cpu = tranlsate_cpu(service['deployment']['intent']['compute']['cpu'])
        memory = tranlsate_memory(service['deployment']['intent']['compute']['ram'])
        storage = tranlsate_storage(service['deployment']['intent']['compute']['storage'])
        gpu = 1 if service['deployment']['intent']['compute']['gpu']['enabled'] == 'True' else 0

        if implementer == 'WOT':
            if 'voChartOverwrite' not in values_overwrite:
                values_overwrite['voChartOverwrite'] = {}
            placement_dict = values_overwrite['voChartOverwrite']

        placement_dict['clustersAffinity'] = [service_placement[name]]
        placement_dict['serviceImportClusters'] = import_clusters[name]

        status = 'Pending' if conditional_deployment else 'Deployed'

        svc_dashboard = grafana_helper.create_graph_service(name)
        response = grafana_helper.publish_dashboard(svc_dashboard)
        grafana_url = f'{current_app.config["GRAFANA_HOST"]}{response["url"]}'

        svc = Service(
            name=name,
            values_overwrite=values_overwrite,
            graph_id=graph.id,
            status=status,
            cluster_affinity=service_placement[name],
            artifact_ref=artifact_ref,
            artifact_type=artifact_type,
            artifact_implementer=implementer,
            cpu=cpu,
            memory=memory,
            storage=storage,
            gpu=gpu,
            grafana=grafana_url,
            alert=alert
        )
        db.session.add(svc)

        if not conditional_deployment:
            helm_install_artifact(name, artifact_ref, values_overwrite, 'install')


    dashboard = grafana_helper.create_graph_dashboard(graph.name, svc_names)
    response = grafana_helper.publish_dashboard(dashboard)
    grafana_url = f'{current_app.config["GRAFANA_HOST"]}{response["url"]}'
    graph.grafana = grafana_url

    db.session.commit()

    if current_app.config['SCALING_ENABLED']:
        spawn_scaling_processes(graph.name, cluster_placement)


def fetch_graph(name):
    """Retrieves the descriptor of an application graph."""

    graph = db.session.query(Graph).filter_by(name=name).first()

    return graph


def trigger_placement(name):
    """Triggers the placement algorithm for the given graph."""

    graph = db.session.query(Graph).filter_by(name=name).first()
    if graph is None:
        raise NotFound(f'Graph with name {name} not found')

    for stop_event in stop_events[name]:
        stop_event.set()
    karmada_helper = KarmadaHelper(current_app.config['KARMADA_KUBECONFIG'])

    services = [service.name for service in graph.services]
    cpu_limits = [service.cpu for service in graph.services]
    acceleration_list = [service.gpu for service in graph.services]
    current_replicas = [karmada_helper.get_replicas(service) for service in services]

    available_clusters = db.session.query(Cluster).filter_by(availability=True)
    cluster_list = [cluster.name for cluster in available_clusters]
    cluster_capacity = {cluster.name: cluster.available_cpu for cluster in available_clusters}
    cluster_acceleration = {cluster.name: cluster.acceleration for cluster in available_clusters}
    cluster_capacity_list = [value for value in cluster_capacity.values()]
    cluster_acceleration_list = [value for value in cluster_acceleration.values()]

    placement = decide_placement(
        cluster_capacity_list, cluster_acceleration_list, cpu_limits,
        acceleration_list, current_replicas, graph.placement
    )
    graph.placement = placement
    db.session.commit()
    descriptor_services = graph.graph_descriptor['services']

    available_clusters = db.session.query(Cluster).filter_by(availability=True)
    cluster_list = [cluster.name for cluster in available_clusters]

    service_placement = convert_placement(placement, descriptor_services, cluster_list)
    cluster_placement = swap_placement(service_placement)
    import_clusters = create_service_imports(descriptor_services, service_placement)

    for service in graph.services:
        # Updating JSONB fields requires new dictionary creation
        values_overwrite = dict(service.values_overwrite)
        placement_dict = values_overwrite
        if service.artifact_implementer == 'WOT':
            if 'voChartOverwrite' not in values_overwrite:
                values_overwrite['voChartOverwrite'] = {}
            placement_dict = values_overwrite['voChartOverwrite']
        if placement_dict['clustersAffinity'][0] != service_placement[service.name]:
            placement_dict['clustersAffinity'] = [service_placement[service.name]]
            placement_dict['serviceImportClusters'] = import_clusters[service.name]
            service.values_overwrite = values_overwrite
            db.session.commit()

            helm_install_artifact(service.name, service.artifact_ref, values_overwrite, 'upgrade')

    if current_app.config['SCALING_ENABLED']:
        spawn_scaling_processes(name, cluster_placement)


def start_graph(name):
    """Starts a stopped graph"""

    graph = db.session.query(Graph).filter_by(name=name).first()
    if graph is None:
        raise NotFound(f'Graph with name {name} not found')
    if graph.status == 'Running':
        raise BadRequest(f'Graph with name {name} is already running')
    graph.status = 'Running'
    for service in graph.services:
        if service.alert != {}:
            prom_helper = PrometheusHelper(current_app.config['PROMETHEUS_HOST'])
            prom_helper.update_alert_rules(service.alert, 'add')
        if service.status == 'Deployed':
            helm_install_artifact(
                service.name,
                service.artifact_ref,
                service.values_overwrite,
                'install'
            )
    db.session.commit()


def stop_graph(name):
    """Removes a graph's artifacts and sets its status to `Stopped`"""

    graph = db.session.query(Graph).filter_by(name=name).first()
    if graph is None:
        raise NotFound(f'Graph with name {name} not found')
    if graph.status == 'Stopped':
        raise BadRequest(f'Graph with name {name} is already stopped')

    helm_uninstall_graph(graph.services)
    for stop_event in stop_events[name]:
        stop_event.set()

    graph.status = 'Stopped'
    for service in graph.services:
        service.status = 'Not deployed'
    db.session.commit()


def remove_graph(name):
    """Removes a graph's artifacts and removes it from the database."""

    graph = db.session.query(Graph).filter_by(name=name).first()
    if graph is None:
        raise NotFound(f'Graph with name {name} not found')

    helm_uninstall_graph(graph.services)
    for stop_event in stop_events[name]:
        stop_event.set()

    db.session.delete(graph)
    db.session.commit()


def deploy_conditional_service(data):
    """Deploys a service that is triggered when an alert has been fired."""

    alerts = data['alerts']
    for alert in alerts:
        labels = alert['labels']
        if 'service' in labels:
            alertname = labels['alertname']
            service_name = labels['service']
            service = db.session.query(Service).filter_by(name=service_name).first()
            if service is None:
                continue

            helm_install_artifact(service.name, service.artifact_ref, service.values_overwrite, 'install')

            service.status = 'Deployed'
            db.session.commit()


def create_service_imports(services, service_placement):
    """
    Checks to which other services each service connects to and
    returns a dictionary whose keys are the service names and
    the values are a list of cluster names to which the service
    needs to be imported.
    """

    # For each service a list of clusters to which its service will be imported
    service_import_clusters = {
        service['id']: [] for service in services
    }

    for service in services:
        connection_points = service['deployment']['intent']['connectionPoints']
        for other_service in services:
            if other_service['id'] in connection_points:
                service_import_clusters[other_service['id']].extend(
                    [service_placement[service['id']]]
                )

    return service_import_clusters


def get_descriptor_from_artifact(project, artifact_ref):
    """
    Calls the hdarctl cli to pull an artifact and deploys
    the descriptor inside after untaring the artifact.
    """

    with tempfile.TemporaryDirectory() as dirpath:
        subprocess.run([
            'hdarctl',
            'pull',
            artifact_ref,
            '--untar',
            '--destination',
            dirpath
        ])

        for (root, dirs, files) in walk(dirpath):
            for file in files:
                if file.endswith('.yaml') or file.endswith('.yml'):
                    with open(path.join(root, file), 'r') as yaml_file:
                        data = yaml.safe_load(yaml_file)
                        return data


def helm_install_artifact(name, artifact_ref, values_overwrite, command):
    """Executes helm command (install/upgrade) for artifact."""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as values_file:
        yaml.dump(values_overwrite, values_file)

        subprocess_arguments = [
            'helm',
            command,
            name,
            artifact_ref,
            '--values',
            values_file.name,
            '--kubeconfig',
            current_app.config['KARMADA_KUBECONFIG']
        ]
        if current_app.config['INSECURE_REGISTRY']:
            subprocess_arguments.append('--plain-http')
        if command == 'upgrade':
            subprocess_arguments.append('--reuse-values')
        subprocess.run(subprocess_arguments)


def helm_uninstall_graph(services):
    """Uninstalls all service artifacts."""

    for service in services:
        if service.alert != {}:
            prom_helper = PrometheusHelper(current_app.config['PROMETHEUS_HOST'])
            prom_helper.update_alert_rules(service.alert, 'remove')
        if service.status == 'Deployed':
            subprocess.run([
                'helm',
                'uninstall',
                service.name,
                '--kubeconfig',
                current_app.config['KARMADA_KUBECONFIG']
            ])


def spawn_scaling_processes(graph_name, cluster_placement):
    """Spawns background threads that periodically run the scaling algorithm."""

    MAXIMUM_REPLICAS = {'image-compression-vo': 3,'noise-reduction': 3,'image-detection': 3}
    ACCELERATION = {'image-compression-vo': 0,'noise-reduction': 0,'image-detection': 0}
    ALPHA = {'image-compression-vo': 33.33,'noise-reduction': 0.533,'image-detection': 1.67}
    BETA = {'image-compression-vo': -16.66,'noise-reduction': -0.416,'image-detection': -0.01}

    available_clusters = db.session.query(Cluster).filter_by(availability=True)
    cluster_list = [cluster.name for cluster in available_clusters]
    cluster_capacity = {cluster.name: cluster.available_cpu for cluster in available_clusters}
    cluster_acceleration = {cluster.name: cluster.acceleration for cluster in available_clusters}

    for cluster_index, cluster in enumerate(cluster_list):
        if cluster not in cluster_placement.keys():
            break
        # Fetch cluster specific values
        managed_services = cluster_placement[cluster]
        acceleration = [ACCELERATION[service] for service in managed_services]
        alpha = [ALPHA[service] for service in managed_services]
        beta = [BETA[service] for service in managed_services]
        maximum_replicas = [MAXIMUM_REPLICAS[service] for service in managed_services]

        stop_events[cluster_index].clear()
        background_scaling_threads[graph_name][cluster_index] = threading.Thread(
            target=scaling_loop,
            args=(
                graph_name,
                acceleration,
                alpha,
                beta,
                cluster_capacity[cluster],
                cluster_acceleration[cluster],
                maximum_replicas,
                managed_services,
                current_app.config['SCALING_INTERVAL'],
                current_app.config['KARMADA_KUBECONFIG'],
                current_app.config['PROMETHEUS_HOST'],
                stop_events[cluster_index]
            )
        )
        background_scaling_threads[cluster_index].daemon = True
        background_scaling_threads[cluster_index].start()


def create_alert(event_id, prom_query, grace_period, description, name):
    return {
        'alert': f'{event_id}',
        'annotations': {
            'description': description,
            'summary': description
        },
        'expr': f'{prom_query}',
        'for': f'{grace_period}',
        'labels': {
            'severity': 'critical',
            'service': name
        }
    }
