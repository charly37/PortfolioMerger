# mainTrades.py

Creates a single output file with all trades from all brokers.

## Usage

```bash
python mainTrades.py --ibkr-file ./IBKRtrades.csv --cs-file ./CStrades.csv
```

## Arguments

- `--ibkr-file`: Interactive Brokers trades CSV file (required)
- `--cs-file`: Charles Schwab trades CSV file (required)

## Output Format

The output file combines trade data from both brokers into a single consolidated view.
