.PHONY: test test-unit test-integration test-live test-chaos run-live clean

# Default test target runs unit and integration tests
test:
	python -m pytest -xvs tests/unit/ tests/integration/ --cov=fhir_pipeline --cov-report=term

# Run only unit tests
test-unit:
	python -m pytest -xvs tests/unit/ --cov=fhir_pipeline --cov-report=term

# Run integration tests
test-integration:
	python -m pytest -xvs tests/integration/ --cov=fhir_pipeline --cov-report=term

# Run live API tests (requires EPIC environment variables)
test-live:
	python -m pytest -xvs tests/live/

# Run chaos tests to verify resilience
test-chaos:
	python -m pytest -xvs tests/perf/chaos_test.py

# Run full pipeline with live test patient
run-live:
	./scripts/run_sandbox_smoke.sh

# Clean up output directories and test artifacts
clean:
	rm -rf local_output/
	rm -rf tests/perf/chaos_report.md
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf coverage.xml

# Install dependencies
install:
	pip install -r requirements.txt

# Run linting
lint:
	black .
	ruff check .

# Run full testing suite (except live tests)
test-all:
	python -m pytest -xvs tests/unit/ tests/integration/ tests/perf/ --cov=fhir_pipeline --cov-report=term 