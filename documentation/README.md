to export all the positions from IBKR and CS to a single file

python mainBrokers.py --cs-file ./CS.csv --ibkr-file ./IBKR.csv

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

