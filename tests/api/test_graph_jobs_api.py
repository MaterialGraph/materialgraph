import uuid


def test_create_graph_job_is_not_publicly_available(client):
    response = client.post(
        "/api/v1/graph-jobs",
        json={
            "job_type": "build_graph",
            "payload_json": {},
        },
    )

    assert response.status_code == 404


def test_list_graph_jobs_is_not_publicly_available(client):
    response = client.get("/api/v1/graph-jobs")

    assert response.status_code == 404


def test_get_graph_job_by_id_is_not_publicly_available(client):
    job_id = uuid.uuid4()

    response = client.get(f"/api/v1/graph-jobs/{job_id}")

    assert response.status_code == 404


def test_graph_jobs_are_absent_from_openapi_schema(client):
    response = client.get("/openapi.json")

    assert response.status_code == 200

    paths = response.json()["paths"]
    assert not any("graph-jobs" in path for path in paths)