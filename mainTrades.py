import re
import csv
import argparse
import logging
from datetime import datetime

# Set up logging configuration
def setup_logging(log_file='trades.log', debug=False):
    log_level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

class aTrx:
    def __init__(self) -> None:
        self.symbol=""
        self.provider=""
        self.action=""
        self.dateWithTime=""
        self.quantity=0
        self.paidByUnit=0
        

def isItProperSymbol(aSymbol):
    return bool(re.fullmatch(r"[A-Za-z]{2,4}|\w+\/\w+", aSymbol))

def loadTrxIBKR(ioaTrxs):
    with open('IBKRtrades.csv', newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        next(spamreader)  # Skip the header row
        for row in spamreader:
            if row[3].strip('\"') == "ExchTrade":
                aNewTrx = aTrx()
                aNewTrx.symbol = row[0].strip('\"')
                aNewTrx.provider = "IBKR"
                aAction = row[6].strip('\"')
                if aAction == "BUY":
                    aNewTrx.action = "B"
                elif aAction == "SELL":
                    aNewTrx.action = "S"
                else:
                    logging.error(f"Unknown action: {aAction}")
                    raise Exception(f"Unknown action: {aAction}")
                # Convert the datetime string to a datetime object
                datetime_str = row[1].strip('\"').replace(';', '')  # Remove the semicolon
                aNewTrx.dateWithTime = datetime.strptime(datetime_str, '%Y%m%d%H%M%S')
                aNewTrx.quantity = int(row[4].strip('\"'))
                aNewTrx.paidByUnit = float(row[5].strip('\"'))
                ioaTrxs.append(aNewTrx)   
            else:
                logging.debug(f"Skipping {row[3]}") 

def loadTrxCS(ioaTrxs):
    with open('CStrades.csv', newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        next(spamreader)  # Skip the header row
        #"Date","Action","Symbol","Description","Quantity","Price","Fees & Comm","Amount"
        #"12/04/2024","Cash Dividend","BND","VANGUARD TOTAL BOND MARKET ETF","","","","$7.36"
        #"12/04/2024","Buy","VT","VANGUARD TOTAL WORLD STOCK ETF","2","$122.80","","-$245.60"
        for row in spamreader:
            aAction = row[1].strip('\"')
            logging.debug(f"Action: {aAction}")
            if aAction == "Buy" or aAction == "Sell":
                aNewTrx = aTrx()
                aNewTrx.symbol = row[2].strip('\"')
                aNewTrx.provider = "CS"
                if aAction == "Buy":
                    aNewTrx.action = "B"
                elif aAction == "Sell":
                    aNewTrx.action = "S"
                else:
                    logging.error(f"Unknown action: {aAction}")
                    raise Exception(f"Unknown action: {aAction}")
                # Convert the datetime string to a datetime object
                datetime_str = row[0].strip('\"')
                aNewTrx.dateWithTime = datetime.strptime(datetime_str, '%m/%d/%Y')
                aNewTrx.quantity = int(row[4].strip('\"'))
                aNewTrx.paidByUnit = float(row[5].strip('\"')[1:])
                ioaTrxs.append(aNewTrx)   
            else:
                logging.debug(f"Skipping {row[1]}") 




# Add argument parser setup at the beginning
parser = argparse.ArgumentParser(description='Process trading transactions from different sources.')
parser.add_argument('--ibkr-file', type=str, default='IBKRtrades.csv',
                   help='Path to IBKR trades CSV file (default: IBKRtrades.csv)')
parser.add_argument('--cs-file', type=str, default='CStrades.csv',
                   help='Path to CS trades CSV file (default: CStrades.csv)')
parser.add_argument('--output', type=str, default='transactions.csv',
                   help='Output file name (default: transactions.csv)')
parser.add_argument('--debug', action='store_true',
                   help='Enable debug logging')
args = parser.parse_args()

setup_logging(debug=args.debug)
logging.info("Starting transaction processing")

aTotalTrxs = []

logging.info("Loading IBKR trades")
loadTrxIBKR(aTotalTrxs)
logging.info("Loading CS trades")
loadTrxCS(aTotalTrxs)

aOutputFileName = args.output
logging.info(f"Writing {aOutputFileName}!")
with open(aOutputFileName, 'w', newline='') as file2:
    writer = csv.writer(file2)
    field = ["symbol", "provider", "action", "dateWithTime", "quantity", "paidByUnit"]
    
    writer.writerow(field)
    for aTrx in aTotalTrxs:
        writer.writerow([aTrx.symbol, aTrx.provider, aTrx.action, aTrx.dateWithTime, aTrx.quantity, aTrx.paidByUnit])