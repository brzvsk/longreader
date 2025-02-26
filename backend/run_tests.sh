#!/bin/bash
# Script to run parser service tests

# Ensure we're in the backend directory
cd "$(dirname "$0")"

# Install test dependencies if needed
if [ "$1" == "--install" ]; then
    echo "Installing test dependencies..."
    pip install -r test_requirements.txt
fi

# Run the tests
echo "Running parser service tests..."
python -m pytest tests/ -v

# Exit with the pytest exit code
exit $? 