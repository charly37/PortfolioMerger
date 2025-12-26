# Testing

## Running All Tests

Run all end-to-end tests from the root directory:

```bash
python3 run_all_tests.py
```

This will automatically discover and run all tests in the `Tests/` folder.

## Running Individual Tests

To run a specific test:

```bash
cd Tests/Test1
python3 test_e2e.py
```

## Test Structure

Tests are organized in the `Tests/` directory:

```
Tests/
├── Test1/
│   ├── test_e2e.py       # End-to-end test script
│   ├── cs1.csv            # Test input: Charles Schwab file 1
│   ├── cs2.csv            # Test input: Charles Schwab file 2
│   ├── Ibkr1.csv          # Test input: Interactive Brokers file
│   └── holdings.csv       # Expected output (reference file)
```

## Adding New Tests

1. Create a new folder under `Tests/` (e.g., `Tests/Test2/`)
2. Add a `test_e2e.py` script
3. Include test input files and expected output
4. Run `python3 run_all_tests.py` to verify

The global test runner will automatically discover and execute your new test.
