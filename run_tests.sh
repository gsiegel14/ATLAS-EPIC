#!/bin/bash
# Comprehensive test script for FHIR pipeline

set -e  # Exit on any error

echo "===== Installing test dependencies ====="
pip install pytest pytest-cov pytest-asyncio responses delta-spark

echo "===== Running unit tests ====="
python -m pytest tests/unit -v

echo "===== Running integration tests ====="
python -m pytest fhir_pipeline/tests -v

echo "===== Running specific component tests ====="
# Test the transformer system
python -m pytest tests/unit/test_transforms.py -v

echo "===== Checking for circular imports ====="
python check_circular_imports.py

echo "===== Running coverage analysis ====="
python -m pytest --cov=fhir_pipeline --cov-report=term-missing tests/ fhir_pipeline/tests/

echo "===== All tests completed successfully! =====" 