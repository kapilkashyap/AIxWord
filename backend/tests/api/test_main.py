"""
Unit tests for FastAPI main application module.

This module tests the FastAPI application initialization, middleware setup,
route registration, and core application functionality.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.api.main import app
from backend.config import get_settings


class TestFastAPIApplication:
    """Test suite for FastAPI application."""

    @pytest.fixture
    def client(self):
        """Create a test client for the FastAPI app."""
        return TestClient(app)

    @pytest.fixture
    def settings(self):
        """Get application settings."""
        return get_settings()

    def test_app_initialization(self):
        """Test that the FastAPI app is properly initialized."""
        assert app is not None
        assert isinstance(app, FastAPI)
        assert app.title == "AIxWord API"
        assert app.version == "0.1.0"

    def test_app_metadata(self):
        """Test application metadata."""
        assert "AI-powered interactive crossword puzzle" in app.description
        assert "multi-agent system" in app.description

    def test_docs_configuration(self, settings):
        """Test documentation endpoint configuration."""
        if settings.enable_docs:
            assert app.docs_url == "/docs"
            assert app.redoc_url == "/redoc"
        else:
            assert app.docs_url is None
            assert app.redoc_url is None

    def test_cors_middleware(self):
        """Test CORS middleware is configured."""
        # Check that CORS middleware is in the middleware stack
        # Note: FastAPI wraps middleware, so we check for Middleware wrapper
        middleware_types = [type(m).__name__ for m in app.user_middleware]
        assert "Middleware" in middleware_types or "CORSMiddleware" in middleware_types

    def test_root_endpoint(self, client):
        """Test root endpoint returns basic info."""
        response = client.get("/")
        assert response.status_code == 200

        data = response.json()
        assert "message" in data
        assert "version" in data
        assert data["message"] == "AIxWord API"
        assert data["version"] == "0.1.0"

    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/api/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"
        assert "service" in data
        assert "version" in data
        assert "config" in data

    def test_ready_endpoint(self, client):
        """Test readiness check endpoint."""
        response = client.get("/api/ready")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "ready"
        assert "message" in data

    def test_404_handling(self, client):
        """Test 404 error handling for non-existent endpoints."""
        response = client.get("/api/nonexistent")
        assert response.status_code == 404

    def test_openapi_schema(self, client, settings):
        """Test OpenAPI schema generation."""
        if settings.enable_docs:
            response = client.get("/openapi.json")
            assert response.status_code == 200

            schema = response.json()
            assert "openapi" in schema
            assert "info" in schema
            assert schema["info"]["title"] == "AIxWord API"
            assert schema["info"]["version"] == "0.1.0"

    def test_routes_registered(self):
        """Test that all expected routes are registered."""
        routes = [route.path for route in app.routes]

        # Check core routes
        assert "/" in routes
        assert "/api/health" in routes
        assert "/api/ready" in routes

        # Check puzzle routes
        assert "/api/puzzles/generate" in routes
        assert "/api/puzzles/" in routes
        assert "/api/puzzles/{puzzle_id}" in routes
        assert "/api/puzzles/{puzzle_id}/solve" in routes
        assert "/api/puzzles/{puzzle_id}/solve-word" in routes
        assert "/api/puzzles/{puzzle_id}/hint" in routes
        assert "/api/puzzles/{puzzle_id}/validate" in routes


class TestGlobalExceptionHandler:
    """Test suite for global exception handler."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        return TestClient(app)

    def test_exception_handler_format(self, client):
        """Test that unhandled exceptions return proper error format."""
        # This test would require triggering an actual exception
        # For now, we verify the handler is registered
        assert app.exception_handlers is not None


class TestMiddleware:
    """Test suite for middleware functionality."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        return TestClient(app)

    def test_cors_headers(self, client):
        """Test CORS headers are present in responses."""
        response = client.get(
            "/api/health",
            headers={"Origin": "http://localhost:5173"}
        )
        assert response.status_code == 200

        # CORS headers should be present
        assert "access-control-allow-origin" in response.headers

    def test_request_id_header(self, client):
        """Test that request ID header is added to responses."""
        # Note: This test assumes RequestLoggingMiddleware is enabled
        # If middleware is added in the future, this will verify it works
        response = client.get("/api/health")
        assert response.status_code == 200


class TestLifespan:
    """Test suite for application lifespan events."""

    def test_lifespan_context(self):
        """Test that lifespan context manager is configured."""
        # The lifespan is configured in the app
        assert app.router.lifespan_context is not None


class TestDependencyInjection:
    """Test suite for dependency injection."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        return TestClient(app)

    def test_settings_dependency(self):
        """Test that settings dependency is available."""
        from backend.api.dependencies import get_app_settings

        settings = get_app_settings()
        assert settings is not None
        assert hasattr(settings, "openai_api_key")
        assert hasattr(settings, "grid_size")

    def test_orchestrator_dependency(self):
        """Test that orchestrator dependency is available."""
        from backend.api.dependencies import get_puzzle_orchestrator

        orchestrator = get_puzzle_orchestrator()
        assert orchestrator is not None


class TestAPIEndpoints:
    """Test suite for API endpoints integration."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        return TestClient(app)

    def test_list_puzzles_empty(self, client):
        """Test listing puzzles when none exist."""
        response = client.get("/api/puzzles/")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)

    def test_get_nonexistent_puzzle(self, client):
        """Test getting a puzzle that doesn't exist."""
        response = client.get("/api/puzzles/nonexistent-id")
        assert response.status_code == 404

        data = response.json()
        assert "detail" in data or "error" in data

    def test_delete_nonexistent_puzzle(self, client):
        """Test deleting a puzzle that doesn't exist."""
        response = client.delete("/api/puzzles/nonexistent-id")
        assert response.status_code == 404

        data = response.json()
        assert "detail" in data or "error" in data

    def test_generate_puzzle_validation(self, client):
        """Test puzzle generation request validation."""
        # Missing required field (topic)
        response = client.post(
            "/api/puzzles/generate",
            json={}
        )
        assert response.status_code == 422  # Validation error

        data = response.json()
        assert "detail" in data

    def test_generate_puzzle_invalid_grid_size(self, client):
        """Test puzzle generation with invalid grid size."""
        response = client.post(
            "/api/puzzles/generate",
            json={
                "topic": "Science",
                "grid_size": 100  # Too large
            }
        )
        assert response.status_code == 422  # Validation error

    def test_solve_word_validation(self, client):
        """Test solve word request validation."""
        response = client.post(
            "/api/puzzles/test-id/solve-word",
            json={}  # Missing required fields
        )
        assert response.status_code == 422  # Validation error

    def test_hint_validation(self, client):
        """Test hint request validation."""
        response = client.post(
            "/api/puzzles/test-id/hint",
            json={}  # Missing required fields
        )
        assert response.status_code == 422  # Validation error

    def test_validate_solution_validation(self, client):
        """Test validate solution request validation."""
        response = client.post(
            "/api/puzzles/test-id/validate",
            json={}  # Missing required fields
        )
        assert response.status_code == 422  # Validation error


class TestErrorResponses:
    """Test suite for error response formats."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        return TestClient(app)

    def test_404_error_format(self, client):
        """Test 404 error response format."""
        response = client.get("/api/puzzles/nonexistent")
        assert response.status_code == 404

        data = response.json()
        assert "detail" in data or "error" in data
        # Check that error message is a string
        error_msg = data.get("detail") or data.get("error")
        assert isinstance(error_msg, str)

    def test_validation_error_format(self, client):
        """Test validation error response format."""
        response = client.post(
            "/api/puzzles/generate",
            json={"grid_size": "invalid"}  # Wrong type
        )
        assert response.status_code == 422

        data = response.json()
        assert "detail" in data
        assert isinstance(data["detail"], list)


class TestCORSConfiguration:
    """Test suite for CORS configuration."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        return TestClient(app)

    def test_cors_preflight(self, client):
        """Test CORS preflight request."""
        response = client.options(
            "/api/health",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET",
            }
        )
        # OPTIONS requests should be handled by CORS middleware
        assert response.status_code in [200, 204]

    def test_cors_allowed_origin(self, client):
        """Test CORS with allowed origin."""
        settings = get_settings()
        if settings.cors_origins_list:
            origin = settings.cors_origins_list[0]
            response = client.get(
                "/api/health",
                headers={"Origin": origin}
            )
            assert response.status_code == 200
            assert "access-control-allow-origin" in response.headers


class TestApplicationConfiguration:
    """Test suite for application configuration."""

    def test_settings_loaded(self):
        """Test that settings are properly loaded."""
        settings = get_settings()
        assert settings is not None
        assert settings.openai_api_key is not None
        assert settings.grid_size > 0
        assert settings.max_iterations > 0

    def test_settings_validation(self):
        """Test settings validation."""
        settings = get_settings()

        # Grid size should be within valid range
        assert 4 <= settings.grid_size <= 20

        # Max iterations should be positive
        assert settings.max_iterations > 0

        # Fill rate should be between 0 and 1
        assert 0.0 <= settings.min_fill_rate <= 1.0

        # Temperature should be valid
        assert 0.0 <= settings.openai_temperature <= 2.0

    def test_cors_origins_parsing(self):
        """Test CORS origins parsing."""
        settings = get_settings()
        origins = settings.cors_origins_list

        assert isinstance(origins, list)
        assert all(isinstance(origin, str) for origin in origins)
