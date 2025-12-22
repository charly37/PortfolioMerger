to export all the positions from IBKR and CS to a single file

python mainBrokers.py --files ./CS.csv ./IBKR.csv --output holdings.csv

# Enable debug mode for detailed logging
python mainBrokers.py --files ./CS.csv ./IBKR.csv --debug

## Target Allocations

The output includes a `target` column that shows your target allocation for each stock. These targets are read from a `targets` file in JSON format:

```json
{
    "SHV": 10,
    "SHY": 11,
    "VTI": 5
}
```

The script will log an error for any stock that doesn't have a defined target.

## Export Instructions

to export from Charles Schwab your position as csv
follow the 3 steps in the picture
![ExportPositionCharlesSchwab](./documentation/ExportPositionCharlesSchwab.png)

to export from IBKR your position as csv
follow the 3 steps in the picture to open the export popup
![ExportPositionIBKR](./documentation/ExportPositionIbkr1.png)
then click on the button "Run" on the popup
![ExportPositionIBKR](./documentation/ExportPositionIbkr2.png)

To run the script to merge the positions from IBKR and CS
python mainBrokers.py --cs-file ./CS.csv --ibkr-file ./IBKR.csv

To run the script to merge the trades from IBKR and CS
python mainTrades.py --ibkr-file ./IBKRtrades.csv --cs-file ./CStrades.csv

