"""
Models module for ML Translation API.

This module provides comprehensive model management capabilities for the translation API,
including AWS S3 integration and Hugging Face model operations.

Classes:
    AWSServicesManager: Base class for managing AWS services, primarily S3 operations
        including bucket management, file/directory upload/download functionality.

    TranslationModelManager: Main model management class that handles:
        - Downloading pre-trained translation models from Hugging Face Hub
        - Converting PyTorch models to ONNX format for optimized inference
        - Storing and retrieving models from local filesystem or AWS S3
        - In-memory model caching for improved performance
        - Text translation inference with configurable parameters
        - Model metadata and configuration management

Key Features:
    - ONNX model conversion for faster inference and cross-platform compatibility
    - Automatic model caching to reduce memory overhead
    - Flexible storage modes (local filesystem or AWS S3)
    - Support for multiple translation language pairs
    - Prometheus metrics integration for monitoring
    - Graceful error handling and detailed logging

Usage:
    >>> from models import TranslationModelManager
    >>> manager = TranslationModelManager(
    ...     model_mappings={'en-fr': 'Helsinki-NLP/opus-mt-en-fr'},
    ...     model_storage_mode='local'
    ... )
    >>> manager.save_model('en-fr')
    >>> translation = manager.predict('en-fr', 'Hello world')
"""

from models.aws import AWSServicesManager
from models.management import TranslationModelManager

__all__ = [
    "AWSServicesManager",
    "TranslationModelManager"
]
