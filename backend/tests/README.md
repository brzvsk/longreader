# Parser Service Tests

This directory contains tests for the parser service, which is responsible for extracting content from web pages.

## Setup

1. Install test dependencies:
   ```
   pip install -r ../test_requirements.txt
   ```

2. Run tests:
   ```
   pytest -v
   ```

## Test Structure

- `conftest.py`: Contains shared fixtures for testing
- `test_parser_service.py`: Tests for the parser service
- `fixtures/`: Helper functions and utilities for testing
- `test_data/`: Test data including HTML samples and expected results

## Adding New Test Cases

1. Add a real URL to the `TEST_URLS` dictionary in `download_test_samples.py`
2. Run the script to download the HTML content:
   ```
   python download_test_samples.py
   ```
3. Add a new test case in `test_parser_service.py`

## Test Data

The test data is organized as follows:

- `html_samples/`: Contains HTML content from real articles
- `expected_results/`: Contains expected parsing results

## Mocking Strategy

The tests use `pytest-httpx` to mock HTTP responses, returning predefined HTML content instead of making real network requests.

## Running Specific Tests

To run a specific test:
```
pytest -v tests/test_parser_service.py::test_parser_service_basic
```

To run tests with a specific marker:
```
pytest -v -m "integration"
``` 