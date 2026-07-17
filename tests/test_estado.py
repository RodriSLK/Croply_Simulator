from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


def _crear_parcela(client: TestClient) -> None:
	payload = {
		"parcela": {
			"id": 1,
			"nombre": "Parcela Norte",
			"latitud": -32.89,
			"longitud": -68.84,
			"controlador": {
				"id": 3,
				"ip": "192.168.0.10",
				"estado": "TRANSMITIENDO",
				"sensores": [
					{"id": 10, "tipo": "TEMP_HUME_AMBIENTAL"},
					{"id": 11, "tipo": "HUMEDAD_SUELO"},
					{"id": 12, "tipo": "RADIACION_SOLAR"},
					{"id": 13, "tipo": "PRECIPITACION"},
					{"id": 14, "tipo": "PH"},
				],
			},
		}
	}
	assert client.post("/parcelas", json=payload).status_code == 201


def test_estado_parcela_nueva_devuelve_null_en_lecturas() -> None:
	client = TestClient(app)
	_crear_parcela(client)

	response = client.get("/parcelas/1/estado")

	assert response.status_code == 200
	body = response.json()
	assert body["parcela_id"] == 1
	assert body["controladores"][0]["sensores"][0]["valor_actual"] is None
	assert body["controladores"][0]["sensores"][0]["fecha_ultima_lectura"] is None


def test_estado_parcela_inexistente_devuelve_404() -> None:
	client = TestClient(app)

	response = client.get("/parcelas/999/estado")

	assert response.status_code == 404