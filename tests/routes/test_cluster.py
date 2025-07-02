def test_get_clusters(client):
    """Test retrieving a list of clusters."""

    response = client.get("/clusters/")

    assert response.status_code == 200

    data = response.get_json()

    cluster_names = {cluster['name'] for cluster in data}

    assert 'test-cluster-1' in cluster_names
    assert 'test-cluster-2' in cluster_names

    cluster_1 = next(c for c in data if c['name'] == 'test-cluster-1')
    assert cluster_1['available_cpu'] == 12.0
    assert cluster_1['availability'] is True
