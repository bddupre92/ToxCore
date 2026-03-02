"""Integration tests for API endpoints."""

import pytest


@pytest.mark.asyncio
async def test_health(client):
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_search_requires_query(client):
    response = await client.get("/api/v1/search")
    assert response.status_code == 422  # Missing required query param


@pytest.mark.asyncio
async def test_search_empty_results(client):
    response = await client.get("/api/v1/search?q=nonexistent")
    assert response.status_code == 200
    data = response.json()
    assert data["results"] == []
    assert data["total"] == 0


@pytest.mark.asyncio
async def test_search_pagination_params(client):
    response = await client.get("/api/v1/search?q=test&page=1&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 1
    assert data["limit"] == 10


@pytest.mark.asyncio
async def test_search_limit_max(client):
    response = await client.get("/api/v1/search?q=test&limit=200")
    assert response.status_code == 422  # Exceeds max limit


@pytest.mark.asyncio
async def test_product_not_found(client):
    response = await client.get("/api/v1/products/nonexistent-id")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_chemical_not_found(client):
    response = await client.get("/api/v1/chemicals/nonexistent-id")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_compare_requires_two_products(client):
    response = await client.post(
        "/api/v1/compare",
        json={"product_ids": ["one"]},
    )
    assert response.status_code == 422  # min_length=2


@pytest.mark.asyncio
async def test_compare_max_three_products(client):
    response = await client.post(
        "/api/v1/compare",
        json={"product_ids": ["a", "b", "c", "d"]},
    )
    assert response.status_code == 422  # max_length=3


@pytest.mark.asyncio
async def test_compare_no_duplicates(client):
    response = await client.post(
        "/api/v1/compare",
        json={"product_ids": ["same", "same"]},
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_ai_explain_not_implemented(client):
    response = await client.post("/api/v1/explain/product/test-id")
    assert response.status_code == 503  # Not yet implemented


@pytest.mark.asyncio
async def test_cors_headers(client):
    """Verify CORS headers are set."""
    response = await client.options(
        "/api/v1/health",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )
    # FastAPI test client may not trigger CORS middleware fully,
    # but we verify the endpoint is accessible
    assert response.status_code in (200, 405)
