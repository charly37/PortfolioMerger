# PortfolioMerger

Portfolio management tool for merging positions and trades from multiple brokers.

## Scripts

### mainBrokers.py
Merges position files from multiple brokers (Charles Schwab and Interactive Brokers) into a single consolidated output file. Automatically detects broker format and enriches data with target allocations and descriptions.

[Full Documentation](documentation/mainBrokers.md)

### mainTrades.py
Merges trade history files from multiple brokers into a single consolidated output file.

[Full Documentation](documentation/mainTrades.md)

## Testing

End-to-end tests are available to verify the functionality of the scripts. Run all tests with `python3 run_all_tests.py`.

[Full Testing Documentation](documentation/testing.md)