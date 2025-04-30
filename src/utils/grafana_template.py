"""Grafana template creator functions."""


def create_basic_dashboard(name):
    """Create a basic dashboard skeleton with no panels."""

    return {
        "dashboard": {
            "editable": True,
            "id": None,
            "uid": name,
            "title": name,
            "tags": [],
            "timezone": "browser",
            "schemaVersion": 40,
            "version": 0,
            "refresh": "5s",
            "panels": [],
        },
        "overwrite": True,
    }


def create_dashboard_variables(variable_name, possible_values):
    """Create variables for the Grafana dashboard."""

    options = []
    for idx, value in enumerate(possible_values):
        selected = True if idx == 0 else False
        options.append({"selected": selected, "text": value, "value": value})

    query = ", ".join(possible_values)

    return {
        "list": [
            {
                "current": {"text": possible_values[0], "value": possible_values[0]},
                "name": variable_name,
                "includeAll": True,
                "multi": True,
                "options": options,
                "query": query,
                "type": "custom",
            }
        ]
    }


def create_panels_service(service_name):
    """Create panels for a service."""

    return [
        {
            "datasource": {"type": "prometheus", "uid": "prometheus"},
            "fieldConfig": {
                "defaults": {
                    "color": {"mode": "palette-classic"},
                    "custom": {
                        "axisBorderShow": False,
                        "axisCenteredZero": False,
                        "axisColorMode": "text",
                        "axisLabel": "",
                        "axisPlacement": "auto",
                        "barAlignment": 0,
                        "drawStyle": "line",
                        "fillOpacity": 0,
                        "gradientMode": "none",
                        "hideFrom": {"legend": False, "tooltip": False, "viz": False},
                        "insertNulls": False,
                        "lineInterpolation": "linear",
                        "lineWidth": 1,
                        "pointSize": 5,
                        "scaleDistribution": {"type": "linear"},
                        "showPoints": "auto",
                        "spanNulls": False,
                        "stacking": {"group": "A", "mode": "none"},
                        "thresholdsStyle": {"mode": "off"},
                    },
                    "mappings": [],
                    "thresholds": {
                        "mode": "absolute",
                        "steps": [{"color": "green", "value": None}],
                    },
                },
                "overrides": [],
            },
            "gridPos": {"h": 8, "w": 24, "x": 0, "y": 0},
            "id": 2,
            "options": {
                "legend": {
                    "calcs": [],
                    "displayMode": "list",
                    "placement": "bottom",
                    "showLegend": True,
                },
                "tooltip": {"mode": "single", "sort": "none"},
            },
            "repeat": "service",
            "repeatDirection": "h",
            "targets": [
                {
                    "datasource": {"type": "prometheus", "uid": "prometheus"},
                    "editorMode": "code",
                    "expr": f'sum(kube_deployment_status_replicas_ready{{deployment="{service_name}"}}) OR on() vector(0)',
                    "instant": False,
                    "range": True,
                    "refId": "A",
                }
            ],
            "title": f"{service_name} pods",
            "type": "timeseries",
        },
        {
            "datasource": {"type": "prometheus", "uid": "prometheus"},
            "fieldConfig": {
                "defaults": {
                    "color": {"mode": "palette-classic"},
                    "custom": {
                        "axisBorderShow": False,
                        "axisCenteredZero": False,
                        "axisColorMode": "text",
                        "axisLabel": "",
                        "axisPlacement": "auto",
                        "axisSoftMax": 100,
                        "axisSoftMin": 0,
                        "barAlignment": 0,
                        "drawStyle": "line",
                        "fillOpacity": 0,
                        "gradientMode": "none",
                        "hideFrom": {"legend": False, "tooltip": False, "viz": False},
                        "insertNulls": False,
                        "lineInterpolation": "linear",
                        "lineWidth": 1,
                        "pointSize": 5,
                        "scaleDistribution": {"type": "linear"},
                        "showPoints": "auto",
                        "spanNulls": False,
                        "stacking": {"group": "A", "mode": "none"},
                        "thresholdsStyle": {"mode": "off"},
                    },
                    "mappings": [],
                    "thresholds": {
                        "mode": "absolute",
                        "steps": [
                            {"color": "green", "value": None},
                            {"color": "red", "value": 80},
                        ],
                    },
                    "unit": "percent",
                },
                "overrides": [],
            },
            "gridPos": {"h": 8, "w": 24, "x": 0, "y": 8},
            "id": 11,
            "options": {
                "legend": {
                    "calcs": [],
                    "displayMode": "list",
                    "placement": "bottom",
                    "showLegend": True,
                },
                "tooltip": {"mode": "single", "sort": "none"},
            },
            "repeat": "service",
            "repeatDirection": "h",
            "targets": [
                {
                    "datasource": {"type": "prometheus", "uid": "prometheus"},
                    "editorMode": "code",
                    "expr": f'round(100 *sum(rate(container_cpu_usage_seconds_total{{pod=~"{service_name}.*",container=~"{service_name}.*"}}[40s])) by (pod_name, container_name)/sum(kube_pod_container_resource_limits{{pod=~"{service_name}.*",resource="cpu"}}) by (pod_name, container_name))',
                    "instant": False,
                    "range": True,
                    "refId": "A",
                }
            ],
            "title": f"{service_name} CPU utilization",
            "type": "timeseries",
        },
        {
            "datasource": {"type": "prometheus", "uid": "prometheus"},
            "fieldConfig": {
                "defaults": {
                    "color": {"mode": "palette-classic"},
                    "custom": {
                        "axisBorderShow": False,
                        "axisCenteredZero": False,
                        "axisColorMode": "text",
                        "axisLabel": "",
                        "axisPlacement": "auto",
                        "barAlignment": 0,
                        "drawStyle": "line",
                        "fillOpacity": 0,
                        "gradientMode": "none",
                        "hideFrom": {"legend": False, "tooltip": False, "viz": False},
                        "insertNulls": False,
                        "lineInterpolation": "linear",
                        "lineWidth": 1,
                        "pointSize": 5,
                        "scaleDistribution": {"type": "linear"},
                        "showPoints": "auto",
                        "spanNulls": False,
                        "stacking": {"group": "A", "mode": "none"},
                        "thresholdsStyle": {"mode": "off"},
                    },
                    "mappings": [],
                    "thresholds": {
                        "mode": "absolute",
                        "steps": [
                            {"color": "green", "value": None},
                            {"color": "red", "value": 80},
                        ],
                    },
                    "unit": "decbytes",
                },
                "overrides": [],
            },
            "gridPos": {"h": 8, "w": 24, "x": 0, "y": 16},
            "id": 10,
            "options": {
                "legend": {
                    "calcs": [],
                    "displayMode": "list",
                    "placement": "bottom",
                    "showLegend": True,
                },
                "tooltip": {"mode": "single", "sort": "none"},
            },
            "repeat": "service",
            "repeatDirection": "h",
            "targets": [
                {
                    "datasource": {"type": "prometheus", "uid": "prometheus"},
                    "editorMode": "code",
                    "expr": f'sum by (service) (container_memory_usage_bytes{{pod=~"{service_name}.*"}}) AND on()(sum(kube_deployment_status_replicas_ready{{deployment="{service_name}"}})) >= 1',
                    "instant": False,
                    "range": True,
                    "refId": "A",
                }
            ],
            "title": f"{service_name} RAM usage",
            "type": "timeseries",
        },
        {
            "datasource": {"type": "prometheus", "uid": "prometheus"},
            "fieldConfig": {
                "defaults": {
                    "color": {"mode": "palette-classic"},
                    "custom": {
                        "axisBorderShow": False,
                        "axisCenteredZero": False,
                        "axisColorMode": "text",
                        "axisLabel": "",
                        "axisPlacement": "auto",
                        "barAlignment": 0,
                        "drawStyle": "line",
                        "fillOpacity": 0,
                        "gradientMode": "none",
                        "hideFrom": {"legend": False, "tooltip": False, "viz": False},
                        "insertNulls": False,
                        "lineInterpolation": "linear",
                        "lineWidth": 1,
                        "pointSize": 5,
                        "scaleDistribution": {"type": "linear"},
                        "showPoints": "auto",
                        "spanNulls": False,
                        "stacking": {"group": "A", "mode": "none"},
                        "thresholdsStyle": {"mode": "off"},
                    },
                    "mappings": [],
                    "thresholds": {
                        "mode": "absolute",
                        "steps": [
                            {"color": "green", "value": None},
                            {"color": "red", "value": 80},
                        ],
                    },
                },
                "overrides": [],
            },
            "gridPos": {"h": 8, "w": 24, "x": 0, "y": 24},
            "id": 5,
            "options": {
                "legend": {
                    "calcs": [],
                    "displayMode": "list",
                    "placement": "bottom",
                    "showLegend": True,
                },
                "tooltip": {"mode": "single", "sort": "none"},
            },
            "repeat": "service",
            "repeatDirection": "h",
            "targets": [
                {
                    "datasource": {"type": "prometheus", "uid": "prometheus"},
                    "editorMode": "code",
                    "expr": f'sum by (container) (increase(container_cpu_cfs_throttled_periods_total{{pod=~"{service_name}.*", container!=""}}[40s])) / sum by (container)(increase(container_cpu_cfs_periods_total{{pod=~"{service_name}.*", container!=""}}[40s]))',
                    "instant": False,
                    "range": True,
                    "refId": "A",
                }
            ],
            "title": f"{service_name} throttling",
            "type": "timeseries",
        },
    ]


def create_panels_cluster(cluster_name):
    """Create panels for the given cluster."""

    return [
        {
            "datasource": {"type": "prometheus", "uid": "prometheus"},
            "fieldConfig": {
                "defaults": {
                    "color": {"mode": "palette-classic"},
                    "custom": {
                        "axisBorderShow": False,
                        "axisCenteredZero": False,
                        "axisColorMode": "text",
                        "axisLabel": "cpu usage",
                        "axisPlacement": "auto",
                        "barAlignment": 0,
                        "drawStyle": "line",
                        "fillOpacity": 10,
                        "gradientMode": "none",
                        "hideFrom": {"legend": False, "tooltip": False, "viz": False},
                        "insertNulls": False,
                        "lineInterpolation": "linear",
                        "lineWidth": 2,
                        "pointSize": 5,
                        "scaleDistribution": {"type": "linear"},
                        "showPoints": "never",
                        "spanNulls": True,
                        "stacking": {"group": "A", "mode": "normal"},
                        "thresholdsStyle": {"mode": "off"},
                    },
                    "mappings": [],
                    "max": 1,
                    "min": 0,
                    "thresholds": {
                        "mode": "absolute",
                        "steps": [
                            {"color": "green", "value": None},
                            {"color": "red", "value": 80},
                        ],
                    },
                    "unit": "percentunit",
                },
                "overrides": [],
            },
            "gridPos": {"h": 7, "w": 14, "x": 0, "y": 0},
            "id": 3,
            "options": {
                "legend": {
                    "calcs": [],
                    "displayMode": "list",
                    "placement": "bottom",
                    "showLegend": True,
                },
                "tooltip": {"mode": "multi", "sort": "none"},
            },
            "pluginVersion": "10.4.0",
            "targets": [
                {
                    "datasource": {"type": "prometheus", "uid": "prometheus"},
                    "editorMode": "code",
                    "expr": f'sum(irate(node_cpu_seconds_total{{source="{cluster_name}", mode="system"}}[5m])) / scalar(count(count(node_cpu_seconds_total{{source="{cluster_name}"}}) by (cpu)))',
                    "format": "time_series",
                    "hide": False,
                    "intervalFactor": 10,
                    "legendFormat": "Busy System",
                    "range": True,
                    "refId": "A",
                    "step": 50,
                },
                {
                    "datasource": {"type": "prometheus", "uid": "prometheus"},
                    "editorMode": "code",
                    "expr": f'sum(irate(node_cpu_seconds_total{{source="{cluster_name}", mode="user"}}[5m])) / scalar(count(count(node_cpu_seconds_total{{source="{cluster_name}"}}) by (cpu)))',
                    "hide": False,
                    "instant": False,
                    "legendFormat": "Busy user",
                    "range": True,
                    "refId": "B",
                },
                {
                    "datasource": {"type": "prometheus", "uid": "prometheus"},
                    "editorMode": "code",
                    "expr": f'sum(irate(node_cpu_seconds_total{{source="{cluster_name}", mode="iowait"}}[5m])) / scalar(count(count(node_cpu_seconds_total{{source="{cluster_name}"}}) by (cpu)))',
                    "hide": False,
                    "instant": False,
                    "legendFormat": "Busy Iowait",
                    "range": True,
                    "refId": "C",
                },
                {
                    "datasource": {"type": "prometheus", "uid": "prometheus"},
                    "editorMode": "code",
                    "expr": f'sum(irate(node_cpu_seconds_total{{source="{cluster_name}", mode=~".*irq"}}[5m])) / scalar(count(count(node_cpu_seconds_total{{source="{cluster_name}"}}) by (cpu)))',
                    "hide": False,
                    "instant": False,
                    "legendFormat": "Busy IRQs",
                    "range": True,
                    "refId": "D",
                },
                {
                    "datasource": {"type": "prometheus", "uid": "prometheus"},
                    "editorMode": "code",
                    "expr": f"sum(irate(node_cpu_seconds_total{{instance=\"{cluster_name}\",  mode!='idle',mode!='user',mode!='system',mode!='iowait',mode!='irq',mode!='softirq'}}[5m])) / scalar(count(count(node_cpu_seconds_total{{instance=\"{cluster_name}\"}}) by (cpu)))",
                    "hide": False,
                    "instant": False,
                    "legendFormat": "Busy Other",
                    "range": True,
                    "refId": "E",
                },
                {
                    "datasource": {"type": "prometheus", "uid": "prometheus"},
                    "editorMode": "code",
                    "expr": f'sum(irate(node_cpu_seconds_total{{source="{cluster_name}", mode="idle"}}[5m])) / scalar(count(count(node_cpu_seconds_total{{source="{cluster_name}"}}) by (cpu)))',
                    "hide": False,
                    "instant": False,
                    "legendFormat": "Idle",
                    "range": True,
                    "refId": "F",
                },
            ],
            "title": "CPU usage",
            "type": "timeseries",
        },
        {
            "datasource": {"type": "prometheus", "uid": "prometheus"},
            "description": "",
            "fieldConfig": {
                "defaults": {
                    "color": {"mode": "thresholds"},
                    "mappings": [],
                    "thresholds": {
                        "mode": "absolute",
                        "steps": [
                            {"color": "green", "value": None},
                            {"color": "red", "value": 80},
                        ],
                    },
                },
                "overrides": [],
            },
            "gridPos": {"h": 7, "w": 4, "x": 14, "y": 0},
            "hideTimeOverride": False,
            "id": 12,
            "maxDataPoints": 100,
            "options": {
                "colorMode": "value",
                "graphMode": "none",
                "justifyMode": "auto",
                "orientation": "auto",
                "reduceOptions": {"calcs": ["last"], "fields": "", "values": False},
                "showPercentChange": False,
                "textMode": "auto",
                "wideLayout": True,
            },
            "pluginVersion": "10.4.0",
            "targets": [
                {
                    "datasource": {"type": "prometheus", "uid": "prometheus"},
                    "editorMode": "code",
                    "expr": f'machine_cpu_cores{{source="{cluster_name}"}}',
                    "format": "time_series",
                    "hide": False,
                    "intervalFactor": 2,
                    "legendFormat": "__auto",
                    "range": True,
                    "refId": "A",
                    "step": 60,
                    "target": "",
                }
            ],
            "title": "CPU cores",
            "type": "stat",
        },
        {
            "datasource": {"type": "prometheus", "uid": "prometheus"},
            "fieldConfig": {
                "defaults": {
                    "color": {"mode": "thresholds"},
                    "mappings": [
                        {
                            "options": {"match": "None", "result": {"text": "N/A"}},
                            "type": "special",
                        }
                    ],
                    "max": 100,
                    "min": 0,
                    "thresholds": {
                        "mode": "absolute",
                        "steps": [
                            {"color": "rgba(50, 172, 45, 0.97)", "value": None},
                            {"color": "rgba(237, 129, 40, 0.89)", "value": 80},
                            {"color": "rgba(245, 54, 54, 0.9)", "value": 90},
                        ],
                    },
                    "unit": "percent",
                },
                "overrides": [],
            },
            "gridPos": {"h": 7, "w": 6, "x": 18, "y": 0},
            "hideTimeOverride": False,
            "id": 11,
            "maxDataPoints": 100,
            "options": {
                "minVizHeight": 75,
                "minVizWidth": 75,
                "orientation": "horizontal",
                "reduceOptions": {"calcs": ["mean"], "fields": "", "values": False},
                "showThresholdLabels": False,
                "showThresholdMarkers": True,
                "sizing": "auto",
            },
            "pluginVersion": "10.4.0",
            "targets": [
                {
                    "datasource": {"type": "prometheus", "uid": "prometheus"},
                    "editorMode": "code",
                    "expr": f'100 * (1 - avg(rate(node_cpu_seconds_total{{mode="idle", source="{cluster_name}"}}[1m])))',
                    "format": "time_series",
                    "intervalFactor": 2,
                    "range": True,
                    "refId": "A",
                    "step": 60,
                    "target": "",
                }
            ],
            "title": "CPU busy",
            "type": "gauge",
        },
        {
            "datasource": {"type": "prometheus", "uid": "prometheus"},
            "fieldConfig": {
                "defaults": {
                    "color": {"mode": "palette-classic"},
                    "custom": {
                        "axisBorderShow": False,
                        "axisCenteredZero": False,
                        "axisColorMode": "text",
                        "axisLabel": "",
                        "axisPlacement": "auto",
                        "barAlignment": 0,
                        "drawStyle": "line",
                        "fillOpacity": 10,
                        "gradientMode": "none",
                        "hideFrom": {"legend": False, "tooltip": False, "viz": False},
                        "insertNulls": False,
                        "lineInterpolation": "linear",
                        "lineWidth": 2,
                        "pointSize": 5,
                        "scaleDistribution": {"type": "linear"},
                        "showPoints": "never",
                        "spanNulls": True,
                        "stacking": {"group": "A", "mode": "normal"},
                        "thresholdsStyle": {"mode": "off"},
                    },
                    "mappings": [],
                    "min": 0,
                    "thresholds": {
                        "mode": "absolute",
                        "steps": [
                            {"color": "green", "value": None},
                            {"color": "red", "value": 80},
                        ],
                    },
                    "unit": "bytes",
                },
                "overrides": [
                    {
                        "matcher": {
                            "id": "byName",
                            "options": 'node_memory_SwapFree{{source="172.17.0.1:9100",job="prometheus"}}',
                        },
                        "properties": [{"id": "unit", "value": "short"}],
                    }
                ],
            },
            "gridPos": {"h": 7, "w": 18, "x": 0, "y": 7},
            "id": 4,
            "options": {
                "legend": {
                    "calcs": [],
                    "displayMode": "list",
                    "placement": "bottom",
                    "showLegend": True,
                },
                "tooltip": {"mode": "multi", "sort": "none"},
            },
            "pluginVersion": "10.4.0",
            "targets": [
                {
                    "datasource": {"type": "prometheus", "uid": "prometheus"},
                    "expr": f'node_memory_MemTotal_bytes{{source="{cluster_name}"}} - node_memory_MemFree_bytes{{source="{cluster_name}"}} - node_memory_Buffers_bytes{{source="{cluster_name}"}} - node_memory_Cached_bytes{{source="{cluster_name}"}}',
                    "format": "time_series",
                    "hide": False,
                    "interval": "",
                    "intervalFactor": 2,
                    "legendFormat": "memory used",
                    "metric": "",
                    "refId": "C",
                    "step": 10,
                },
                {
                    "datasource": {"type": "prometheus", "uid": "prometheus"},
                    "expr": f'node_memory_Buffers_bytes{{source="{cluster_name}"}}',
                    "format": "time_series",
                    "interval": "",
                    "intervalFactor": 2,
                    "legendFormat": "memory buffers",
                    "metric": "",
                    "refId": "E",
                    "step": 10,
                },
                {
                    "datasource": {"type": "prometheus", "uid": "prometheus"},
                    "expr": f'node_memory_Cached_bytes{{source="{cluster_name}"}}',
                    "format": "time_series",
                    "intervalFactor": 2,
                    "legendFormat": "memory cached",
                    "metric": "",
                    "refId": "F",
                    "step": 10,
                },
                {
                    "datasource": {"type": "prometheus", "uid": "prometheus"},
                    "expr": f'node_memory_MemFree_bytes{{source="{cluster_name}"}}',
                    "format": "time_series",
                    "intervalFactor": 2,
                    "legendFormat": "memory free",
                    "metric": "",
                    "refId": "D",
                    "step": 10,
                },
            ],
            "title": "Memory Usage",
            "type": "timeseries",
        },
        {
            "datasource": {"type": "prometheus", "uid": "prometheus"},
            "fieldConfig": {
                "defaults": {
                    "color": {"mode": "thresholds"},
                    "mappings": [
                        {
                            "options": {"match": "None", "result": {"text": "N/A"}},
                            "type": "special",
                        }
                    ],
                    "max": 100,
                    "min": 0,
                    "thresholds": {
                        "mode": "absolute",
                        "steps": [
                            {"color": "rgba(50, 172, 45, 0.97)", "value": None},
                            {"color": "rgba(237, 129, 40, 0.89)", "value": 80},
                            {"color": "rgba(245, 54, 54, 0.9)", "value": 90},
                        ],
                    },
                    "unit": "percent",
                },
                "overrides": [],
            },
            "gridPos": {"h": 7, "w": 6, "x": 18, "y": 7},
            "hideTimeOverride": False,
            "id": 5,
            "maxDataPoints": 100,
            "options": {
                "minVizHeight": 75,
                "minVizWidth": 75,
                "orientation": "horizontal",
                "reduceOptions": {"calcs": ["mean"], "fields": "", "values": False},
                "showThresholdLabels": False,
                "showThresholdMarkers": True,
                "sizing": "auto",
            },
            "pluginVersion": "10.4.0",
            "targets": [
                {
                    "datasource": {"type": "prometheus", "uid": "prometheus"},
                    "expr": f'((node_memory_MemTotal_bytes{{source="{cluster_name}"}} - node_memory_MemFree_bytes{{source="{cluster_name}"}}  - node_memory_Buffers_bytes{{source="{cluster_name}"}} - node_memory_Cached_bytes{{source="{cluster_name}"}}) / node_memory_MemTotal_bytes{{source="{cluster_name}"}}) * 100',
                    "format": "time_series",
                    "intervalFactor": 2,
                    "refId": "A",
                    "step": 60,
                    "target": "",
                }
            ],
            "title": "Memory Usage",
            "type": "gauge",
        },
        {
            "datasource": {"type": "prometheus", "uid": "prometheus"},
            "fieldConfig": {
                "defaults": {
                    "color": {"mode": "palette-classic"},
                    "custom": {
                        "axisBorderShow": False,
                        "axisCenteredZero": False,
                        "axisColorMode": "text",
                        "axisLabel": "",
                        "axisPlacement": "auto",
                        "barAlignment": 0,
                        "drawStyle": "line",
                        "fillOpacity": 10,
                        "gradientMode": "none",
                        "hideFrom": {"legend": False, "tooltip": False, "viz": False},
                        "insertNulls": False,
                        "lineInterpolation": "linear",
                        "lineWidth": 2,
                        "pointSize": 5,
                        "scaleDistribution": {"type": "linear"},
                        "showPoints": "never",
                        "spanNulls": True,
                        "stacking": {"group": "A", "mode": "none"},
                        "thresholdsStyle": {"mode": "off"},
                    },
                    "mappings": [],
                    "thresholds": {
                        "mode": "absolute",
                        "steps": [
                            {"color": "green", "value": None},
                            {"color": "red", "value": 80},
                        ],
                    },
                    "unit": "bytes",
                },
                "overrides": [
                    {
                        "matcher": {
                            "id": "byName",
                            "options": '{{source="172.17.0.1:9100"}}',
                        },
                        "properties": [{"id": "unit", "value": "ms"}],
                    },
                    {
                        "matcher": {"id": "byName", "options": "io time"},
                        "properties": [{"id": "unit", "value": "ms"}],
                    },
                ],
            },
            "gridPos": {"h": 7, "w": 18, "x": 0, "y": 14},
            "id": 6,
            "options": {
                "legend": {
                    "calcs": [],
                    "displayMode": "list",
                    "placement": "bottom",
                    "showLegend": True,
                },
                "tooltip": {"mode": "multi", "sort": "none"},
            },
            "pluginVersion": "10.4.0",
            "targets": [
                {
                    "datasource": {"type": "prometheus", "uid": "prometheus"},
                    "expr": f'sum by (instance) (rate(node_nfsd_disk_bytes_read_total{{source="{cluster_name}"}}[2m]))',
                    "format": "time_series",
                    "hide": False,
                    "intervalFactor": 4,
                    "legendFormat": "read",
                    "refId": "A",
                    "step": 20,
                    "target": "",
                },
                {
                    "datasource": {"type": "prometheus", "uid": "prometheus"},
                    "expr": f'sum by (instance) (rate(node_nfsd_disk_bytes_written_total{{source="{cluster_name}"}}[2m]))',
                    "format": "time_series",
                    "intervalFactor": 4,
                    "legendFormat": "written",
                    "refId": "B",
                    "step": 20,
                },
                {
                    "datasource": {"type": "prometheus", "uid": "prometheus"},
                    "expr": f'sum by (instance) (rate(node_disk_io_time_seconds_total{{source="{cluster_name}"}}[2m]))',
                    "format": "time_series",
                    "intervalFactor": 4,
                    "legendFormat": "io time",
                    "refId": "C",
                    "step": 20,
                },
            ],
            "title": "Disk I/O",
            "type": "timeseries",
        },
        {
            "datasource": {"type": "prometheus", "uid": "prometheus"},
            "fieldConfig": {
                "defaults": {
                    "color": {"mode": "thresholds"},
                    "mappings": [
                        {
                            "options": {"match": "None", "result": {"text": "N/A"}},
                            "type": "special",
                        }
                    ],
                    "max": 1,
                    "min": 0,
                    "thresholds": {
                        "mode": "absolute",
                        "steps": [
                            {"color": "rgba(50, 172, 45, 0.97)", "value": None},
                            {"color": "rgba(237, 129, 40, 0.89)", "value": 0.75},
                            {"color": "rgba(245, 54, 54, 0.9)", "value": 0.9},
                        ],
                    },
                    "unit": "percentunit",
                },
                "overrides": [],
            },
            "gridPos": {"h": 7, "w": 6, "x": 18, "y": 14},
            "hideTimeOverride": False,
            "id": 7,
            "maxDataPoints": 100,
            "options": {
                "minVizHeight": 75,
                "minVizWidth": 75,
                "orientation": "horizontal",
                "reduceOptions": {
                    "calcs": ["lastNotNull"],
                    "fields": "",
                    "values": False,
                },
                "showThresholdLabels": False,
                "showThresholdMarkers": True,
                "sizing": "auto",
            },
            "pluginVersion": "10.4.0",
            "targets": [
                {
                    "datasource": {"type": "prometheus", "uid": "prometheus"},
                    "expr": f'(sum(node_filesystem_size_bytes{{device!="rootfs",source="{cluster_name}"}}) - sum(node_filesystem_free_bytes{{device!="rootfs",source="{cluster_name}"}})) / sum(node_filesystem_size_bytes{{device!="rootfs",source="{cluster_name}"}})',
                    "format": "time_series",
                    "intervalFactor": 2,
                    "refId": "A",
                    "step": 60,
                    "target": "",
                }
            ],
            "title": "Disk Space Usage",
            "type": "gauge",
        },
        {
            "datasource": {"type": "prometheus", "uid": "prometheus"},
            "fieldConfig": {
                "defaults": {
                    "color": {"mode": "palette-classic"},
                    "custom": {
                        "axisBorderShow": False,
                        "axisCenteredZero": False,
                        "axisColorMode": "text",
                        "axisLabel": "",
                        "axisPlacement": "auto",
                        "barAlignment": 0,
                        "drawStyle": "line",
                        "fillOpacity": 10,
                        "gradientMode": "none",
                        "hideFrom": {"legend": False, "tooltip": False, "viz": False},
                        "insertNulls": False,
                        "lineInterpolation": "linear",
                        "lineWidth": 2,
                        "pointSize": 5,
                        "scaleDistribution": {"type": "linear"},
                        "showPoints": "never",
                        "spanNulls": True,
                        "stacking": {"group": "A", "mode": "none"},
                        "thresholdsStyle": {"mode": "off"},
                    },
                    "mappings": [],
                    "thresholds": {
                        "mode": "absolute",
                        "steps": [
                            {"color": "green", "value": None},
                            {"color": "red", "value": 80},
                        ],
                    },
                    "unit": "bytes",
                },
                "overrides": [],
            },
            "gridPos": {"h": 7, "w": 12, "x": 0, "y": 21},
            "id": 8,
            "options": {
                "legend": {
                    "calcs": [],
                    "displayMode": "list",
                    "placement": "bottom",
                    "showLegend": True,
                },
                "tooltip": {"mode": "multi", "sort": "none"},
            },
            "pluginVersion": "10.4.0",
            "targets": [
                {
                    "datasource": {"type": "prometheus", "uid": "prometheus"},
                    "expr": f'rate(node_network_receive_bytes_total{{source="{cluster_name}",device!~"lo"}}[5m])',
                    "format": "time_series",
                    "hide": False,
                    "intervalFactor": 2,
                    "legendFormat": "{{device}}",
                    "refId": "A",
                    "step": 10,
                    "target": "",
                }
            ],
            "title": "Network Received",
            "type": "timeseries",
        },
        {
            "datasource": {"type": "prometheus", "uid": "prometheus"},
            "fieldConfig": {
                "defaults": {
                    "color": {"mode": "palette-classic"},
                    "custom": {
                        "axisBorderShow": False,
                        "axisCenteredZero": False,
                        "axisColorMode": "text",
                        "axisLabel": "",
                        "axisPlacement": "auto",
                        "barAlignment": 0,
                        "drawStyle": "line",
                        "fillOpacity": 10,
                        "gradientMode": "none",
                        "hideFrom": {"legend": False, "tooltip": False, "viz": False},
                        "insertNulls": False,
                        "lineInterpolation": "linear",
                        "lineWidth": 2,
                        "pointSize": 5,
                        "scaleDistribution": {"type": "linear"},
                        "showPoints": "never",
                        "spanNulls": True,
                        "stacking": {"group": "A", "mode": "none"},
                        "thresholdsStyle": {"mode": "off"},
                    },
                    "mappings": [],
                    "thresholds": {
                        "mode": "absolute",
                        "steps": [
                            {"color": "green", "value": None},
                            {"color": "red", "value": 80},
                        ],
                    },
                    "unit": "bytes",
                },
                "overrides": [],
            },
            "gridPos": {"h": 7, "w": 12, "x": 12, "y": 21},
            "id": 10,
            "options": {
                "legend": {
                    "calcs": [],
                    "displayMode": "list",
                    "placement": "bottom",
                    "showLegend": True,
                },
                "tooltip": {"mode": "multi", "sort": "none"},
            },
            "pluginVersion": "10.4.0",
            "targets": [
                {
                    "datasource": {"type": "prometheus", "uid": "prometheus"},
                    "expr": f'rate(node_network_transmit_bytes_total{{source="{cluster_name}",device!~"lo"}}[5m])',
                    "format": "time_series",
                    "hide": False,
                    "intervalFactor": 2,
                    "legendFormat": "{{device}}",
                    "refId": "B",
                    "step": 10,
                    "target": "",
                }
            ],
            "title": "Network Transmitted",
            "type": "timeseries",
        },
    ]
