from fastapi.testclient import TestClient

from app.main import app


def test_root_serves_the_simulator_panel() -> None:
	with TestClient(app) as client:
		response = client.get("/")

	assert response.status_code == 200
	assert "text/html" in response.headers["content-type"]
	assert "Croply Simulator" in response.text


def test_static_index_is_served_from_static_files() -> None:
	with TestClient(app) as client:
		response = client.get("/static/index.html")

	assert response.status_code == 200
	assert "text/html" in response.headers["content-type"]
	assert "panel" in response.text.lower() or "estado global" in response.text.lower()
