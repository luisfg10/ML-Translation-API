"""
Application module for ML Translation API.

This module contains the complete FastAPI application setup for the translation API,
providing RESTful endpoints for text translation using pre-trained transformer models.

The module exports a single FastAPI application instance configured with:
- RESTful API endpoints for translation services
- Prometheus metrics integration for monitoring
- Comprehensive request/response validation using Pydantic schemas
- Health check and model information endpoints
- Batch and single text translation capabilities

API Endpoints:
    GET /: Root endpoint returning basic API information
    GET /health: Health check endpoint for service monitoring
    GET /models: Returns information about loaded translation models
    POST /predict/{translation_pair}: Translation endpoint for specific language pairs
    GET /metrics: Prometheus metrics endpoint (auto-generated)

Key Features:
    - Support for multiple translation language pairs (en-es, en-fr, de-en, etc.)
    - Batch translation processing for improved efficiency
    - ONNX-optimized models for fast inference performance
    - Real-time monitoring with Prometheus metrics integration
    - Configurable translation parameters (beam search, max length, etc.)
    - Comprehensive error handling and validation
    - Model caching for improved response times

Exported Objects:
    app: FastAPI application instance ready for deployment

Example Usage:
    >>> from app import app
    >>> # Run with uvicorn
    >>> # uvicorn app:app --host 0.0.0.0 --port 8000
"""

from app.definition import app

__all__ = ["app"]
