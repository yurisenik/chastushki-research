from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_healthcheck():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_generate_pack_returns_ranked_candidates():
    payload = {
        "occasion": "юбилей",
        "target": "коллега Иван",
        "facts": ["любит рыбалку", "всегда шутит"],
        "tone": "funny",
        "boldness": 3,
        "safe_mode": True,
        "count": 6,
    }
    response = client.post("/v1/generate-pack", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["pack_id"]
    assert len(data["candidates"]) == 6
    assert data["candidates"][0]["score"] >= data["candidates"][-1]["score"]
    assert all(item["safe"] for item in data["candidates"])


def test_refine_returns_new_pack():
    generate = client.post(
        "/v1/generate-pack",
        json={
            "occasion": "день рождения",
            "target": "Мария",
            "facts": ["печет пироги", "любит баян"],
            "tone": "playful",
            "boldness": 2,
            "safe_mode": True,
            "count": 4,
        },
    )
    pack_id = generate.json()["pack_id"]

    refine = client.post("/v1/refine", json={"pack_id": pack_id, "action": "funnier"})
    assert refine.status_code == 200
    refined = refine.json()
    assert refined["source_pack_id"] == pack_id
    assert refined["pack_id"] != pack_id
    assert len(refined["candidates"]) == 4


def test_history_and_favorites_flow():
    created = client.post(
        "/v1/generate-pack",
        json={
            "occasion": "свадьба",
            "target": "молодожены",
            "facts": ["танцуют до утра"],
            "tone": "warm",
            "boldness": 1,
            "safe_mode": True,
            "count": 3,
        },
    ).json()

    history = client.get("/v1/history")
    assert history.status_code == 200
    assert any(item["pack_id"] == created["pack_id"] for item in history.json()["items"])

    favorite = client.post("/v1/favorites", json={"pack_id": created["pack_id"]})
    assert favorite.status_code == 200
    assert favorite.json()["pack_id"] == created["pack_id"]

    favorites = client.get("/v1/favorites")
    assert favorites.status_code == 200
    assert any(item["pack_id"] == created["pack_id"] for item in favorites.json()["items"])


def test_export_pack_as_text():
    created = client.post(
        "/v1/generate-pack",
        json={
            "occasion": "корпоратив",
            "target": "команда",
            "facts": ["закрыли релиз"],
            "tone": "funny",
            "boldness": 2,
            "safe_mode": True,
            "count": 3,
        },
    ).json()
    exported = client.get(f"/v1/export/{created['pack_id']}?format=text")
    assert exported.status_code == 200
    assert "text/plain" in exported.headers["content-type"]
    assert "На корпоратив" in exported.text


def test_guardrails_block_disallowed_content_when_safe_mode():
    response = client.post(
        "/v1/generate-pack",
        json={
            "occasion": "шутка",
            "target": "тест",
            "facts": ["badword"],
            "tone": "funny",
            "boldness": 5,
            "safe_mode": True,
            "count": 3,
        },
    )
    assert response.status_code == 422
    assert response.json()["detail"] == "unsafe_input"


def test_metrics_endpoint_tracks_core_actions():
    client.post(
        "/v1/generate-pack",
        json={
            "occasion": "праздник",
            "target": "друзья",
            "facts": ["поют вместе"],
            "tone": "funny",
            "boldness": 2,
            "safe_mode": True,
            "count": 3,
        },
    )
    metrics = client.get("/v1/metrics")
    assert metrics.status_code == 200
    payload = metrics.json()
    assert payload["generate_count"] >= 1
    assert "usable_output_rate" in payload


def test_cors_preflight_for_generate_pack():
    response = client.options(
        "/v1/generate-pack",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"
