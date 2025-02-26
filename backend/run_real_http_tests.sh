#!/bin/bash
# Script to run real HTTP tests for the parser service

# Ensure we're in the backend directory
cd "$(dirname "$0")"

# Install test dependencies if needed
if [ "$1" == "--install" ]; then
    echo "Installing test dependencies..."
    pip install -r test_requirements.txt
fi

# Run only the real HTTP tests
echo "Running real HTTP tests for parser service..."
python -m pytest tests/test_real_http_requests.py -v

# Exit with the pytest exit code
exit $? 