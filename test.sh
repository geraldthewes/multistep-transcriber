#!/bin/bash

# Run unit tests
echo "Running unit tests..."

# Test 1: Run python -m unittest test_transcriber.py
echo "Testing test_transcriber.py..."
if python -m unittest test_transcriber.py; then
    echo "✓ test_transcriber.py passed"
else
    echo "✗ test_transcriber.py failed"
    exit 1
fi

# Test 2: Run python -m unittest mst/steps/tests/test_helpers.py
echo "Testing mst/steps/tests/test_helpers.py..."
if python -m unittest mst/steps/tests/test_helpers.py; then
    echo "✓ mst/steps/tests/test_helpers.py passed"
else
    echo "✗ mst/steps/tests/test_helpers.py failed"
    exit 1
fi

# If all tests pass, create the Python wheel
echo "All tests passed. Creating Python wheel..."
if python -m build; then
    echo "✓ Python wheel created successfully"
    echo "Wheel file(s) created in dist/ directory"
else
    echo "✗ Failed to create Python wheel"
    exit 1
fi