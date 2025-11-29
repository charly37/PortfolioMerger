# PortfolioMerger

Portfolio management tool for merging positions and trades from multiple brokers.

## Scripts

### mainBrokers.py
Creates a single output file with all positions from all brokers. Automatically detects whether files are from Charles Schwab or Interactive Brokers.

**Usage:**
```bash
# Process multiple files (auto-detects CS or IBKR format)
python mainBrokers.py --files file1.csv file2.csv file3.csv --output holdings.csv

# With default output filename
python mainBrokers.py --files CS1.csv CS2.csv IBKR.csv
```

**Arguments:**
- `--files`: List of CSV files to process (required) - automatically detects CS or IBKR format
- `--output`: Output file path (optional, default: `holdings.csv`)

### mainTrades.py
Creates a single output file with all trades from all brokers.

## Testing

### Running All Tests

Run all end-to-end tests from the root directory:

```bash
python3 run_all_tests.py
```

This will automatically discover and run all tests in the `Tests/` folder.

### Running Individual Tests

To run a specific test:

```bash
cd Tests/Test1
python3 test_e2e.py
```

### Test Structure

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

### Adding New Tests

1. Create a new folder under `Tests/` (e.g., `Tests/Test2/`)
2. Add a `test_e2e.py` script
3. Include test input files and expected output
4. Run `python3 run_all_tests.py` to verify

The global test runner will automatically discover and execute your new test.