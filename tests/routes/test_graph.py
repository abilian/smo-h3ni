import json

from unittest.mock import patch


TEST_GRAPH = json.dumps({
  "hdaGraph": {
    "imVersion": "0.4.0",
    "id": "test-graph",
    "version": "1.0.0",
    "designer": "NTUA",
    "hdaGraphIntent": {
      "security": {
        "enabled": False
      },
      "highAvailability": {
        "enabled": False
      },
      "highPerformance": {
        "enabled": False
      },
      "energyEfficiency": {
        "enabled": False
      }
    },
    "description": "Test graph",
    "services": [
      {
        "id": "test-vo",
        "deployment": {
          "trigger": {
            "event": {
              "condition": "ANY",
              "events": [
                {
                  "id": "main-event",
                  "source": [
                    {
                      "serviceId": "vo",
                      "metricId": "vo-metric"
                    }
                  ],
                  "condition": {
                    "promQuery": "absent(up{prometheus=\"kc1/kube-prometheus-operator\"})",
                    "gracePeriod": "2m",
                    "description": "High vo-metric"
                  }
                }
              ]
            }
          },
          "intent": {
            "network": {
              "deviceProximity": {
                "enabled": False
              },
              "latencies": []
            },
            "compute": {
              "cpu": "light",
              "ram": "light",
              "storage": "light",
              "gpu": {
                "enabled": False
              }
            },
            "coLocation": [],
            "connectionPoints": [],
            "metrics": []
          }
        },
        "artifact": {
          "ociImage": "oci://example.com/test/test-vo",
          "ociConfig": {
            "type": "VO",
            "implementer": "WOT"
          },
          "ociRun": {
            "name": "HELM",
            "version": "v3"
          },
          "valuesOverwrite": {
            "voDescriptorOverwrite": {},
            "voChartOverwrite": {}
          }
        }
      }
    ]
  }
})


def test_graph_lifecycle(client):
    graph_name = 'test-graph'
    project = 'test-project'

    with patch('services.hdag.graph_service.helm_install_artifact') as mock_install, \
         patch('services.hdag.graph_service.helm_uninstall_graph') as mock_uninstall:

        mock_install.return_value = None
        mock_uninstall.return_value = None

        deploy_payload = {'hdaGraph': {'name': graph_name, 'description': 'test graph'}}
        deploy_resp = client.post(f'/project/{project}/graphs', json=deploy_payload)
        assert deploy_resp.status_code == 200

        fetch_resp = client.get(f'/graphs/{graph_name}')
        assert fetch_resp.status_code == 200
        data = fetch_resp.json
        assert data['name'] == graph_name
        assert data['project'] == project

        stop_resp = client.get(f'/graphs/{graph_name}/stop')
        assert stop_resp.status_code == 200

        start_resp = client.get(f'/graphs/{graph_name}/start')
        assert start_resp.status_code == 200

        delete_resp = client.delete(f'/graphs/{graph_name}')
        assert delete_resp.status_code == 200

        fetch_after_delete = client.get(f'/graphs/{graph_name}')
        assert fetch_after_delete.status_code == 404
