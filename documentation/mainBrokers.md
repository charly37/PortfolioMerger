# mainBrokers.py

Creates a single output file with all positions from all brokers. Automatically detects whether files are from Charles Schwab or Interactive Brokers.

## Getting Input Files

Before running this script, you need to export your positions from your broker(s). See [Export Instructions](exportPosition.md) for detailed steps on how to export position files from Charles Schwab and Interactive Brokers.

## Usage

```bash
# Process multiple files (auto-detects CS or IBKR format)
python mainBrokers.py --files file1.csv file2.csv file3.csv --output holdings.csv

# With default output filename
python mainBrokers.py --files CS1.csv CS2.csv IBKR.csv

# Enable debug logging for troubleshooting
python mainBrokers.py --files file1.csv file2.csv --debug
```

## Arguments

- `--files`: List of CSV files to process (required) - automatically detects CS or IBKR format
- `--output`: Output file path (optional, default: `holdings.csv`)
- `--debug`: Enable debug logging level for detailed diagnostic information (optional)

## Output Format

The output CSV file contains the following columns:
- `ticker`: Stock symbol
- `description`: Description or note about the stock (from targets file)
- `nbShares`: Number of shares held
- `price`: Current share price
- `target`: Target allocation for the stock (from targets file)

## Targets File

The script reads target allocations from a `targets` file (JSON format) in the root directory. This file maps stock symbols to objects containing their target allocation weights and descriptive descriptions:

```json
{
    "SHV": {"target": 4.5, "description": "0-1 yr treas. ETF"},
    "SHY": {"target": 4.5, "description": "1-3 yr treas. ETF"},
    "VTI": {"target": 3, "description": "USA total market ETF"}
}
```

Each ticker has an object with:
- `target`: The target allocation percentage for the stock
- `description`: A description or note about the stock

If a stock is missing from the targets file, an error will be logged and both the target and description columns will be empty for that stock.
