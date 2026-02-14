"""
Tests for the FastAPI endpoints.

Uses FastAPI's TestClient which simulates HTTP requests
without actually starting a server. We mock the ask_question
function so tests don't call the real AI pipeline.
"""

from unittest.mock import patch
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestHealthEndpoint:
    """Test the /api/health endpoint."""

    def test_health_returns_200(self):
        response = client.get("/api/health")
        assert response.status_code == 200

    def test_health_returns_status(self):
        response = client.get("/api/health")
        data = response.json()
        assert data["status"] == "healthy"


class TestAskEndpoint:
    """Test the /api/ask endpoint."""

    @patch("main.ask_question")
    def test_ask_returns_200(self, mock_ask):
        mock_ask.return_value = {
            "answer": "Test answer",
            "sources": [{"regulation": "SR 11-7", "page": 1, "content": "Test"}],
            "confidence": 0.95,
            "query_type": "LOOKUP",
            "verification": {"confidence": 0.95, "summary": "1/1 supported"},
        }

        response = client.post("/api/ask", json={"question": "Test question"})
        assert response.status_code == 200

    @patch("main.ask_question")
    def test_ask_returns_correct_structure(self, mock_ask):
        mock_ask.return_value = {
            "answer": "SR 11-7 requires validation...",
            "sources": [{"regulation": "SR 11-7", "page": 5, "content": "..."}],
            "confidence": 0.9,
            "query_type": "LOOKUP",
            "verification": {"confidence": 0.9},
        }

        response = client.post(
            "/api/ask",
            json={"question": "What does SR 11-7 require?"},
        )
        data = response.json()

        assert "answer" in data
        assert "sources" in data
        assert "confidence" in data
        assert "query_type" in data
        assert isinstance(data["sources"], list)
        assert isinstance(data["confidence"], float)

    def test_ask_rejects_empty_body(self):
        response = client.post("/api/ask", json={})
        assert response.status_code == 422  # Validation error

    def test_ask_rejects_missing_question(self):
        response = client.post("/api/ask", json={"wrong_field": "test"})
        assert response.status_code == 422
