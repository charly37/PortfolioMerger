import re
import csv
import os
import argparse
import logging

print("Starting PortfolioMerger - Merging positions from CS and IBKR")

# Set up logging configuration at the start of your script
def setup_logging(log_file='trades.log'):  
    # Full path for log file
    log_path = os.path.join("./", log_file)
    
    # Configure logging
    logging.basicConfig(
        level=logging.WARN,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_path),
            logging.StreamHandler()  # This will also print to console
        ]
    )

class aShare:
    def __init__(self, aSymbol):
        self.symbol = aSymbol
        self.nbShares = 0
        self.sharePrice = 0
        self.value = 0

    def __str__(self):
        return f"{self.symbol}({self.nbShares};{self.sharePrice})"

def isItProperSymbol(aSymbol):
    return bool(re.fullmatch(r"[A-Za-z]{2,5}|\w+\/\w+", aSymbol))

def parse_arguments():
    parser = argparse.ArgumentParser(description='Process shares data from CS and IBKR.')
    parser.add_argument('--cs-files', nargs='+', default=['CS.csv'],
                      help='List of paths to the CS holdings CSV files (default: CS.csv)')
    parser.add_argument('--ibkr-file', default='IBKR.csv',
                      help='Path to the IBKR holdings CSV file (default: IBKR.csv)')
    parser.add_argument('--files', nargs='+',
                      help='List of files to process (auto-detects CS or IBKR format)')
    parser.add_argument('--output', default='holdings.csv',
                      help='Output file path (default: holdings.csv)')
    return parser.parse_args()


def loadSharesCs(ioaShares, filename):
    with open(filename, newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in spamreader:
            try:    
                aTicker = row[0]
                logging.debug(f"Processing CS ticker: {aTicker}")
                if not isItProperSymbol(aTicker):
                    logging.error(f"Invalid symbol: {aTicker}")
                    raise ValueError(f"Invalid symbol: {aTicker}")
                aNewShare = aShare(aTicker)
                aNewShare.nbShares = int(row[3])
                logging.debug(f"aNewShare.nbShares: {aNewShare.nbShares}")
                aNewShare.sharePrice = float(row[4][1:])
                ioaShares.append(aNewShare)
            except:
                logging.error(f"Error in CS file with row: {row}")

def loadSharesIBKR(ioaShares, filename):
    with open(filename, newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in spamreader:
            try:    
                aNewShare = aShare(row[0].strip('\"'))
                aNewShare.nbShares = int(row[1].strip('\"'))
                #Some holdings are only on IBKR so if we don t get the price from there file we miss it in the final output
                aIbkrSharePrice = float(row[2].strip('\"'))
                aNewShare.sharePrice = aIbkrSharePrice
                ioaShares.append(aNewShare)   
            except:
                logging.error(f"Error in IBKR filewith row: {row}")

def detect_file_type(filename):
    """
    Detect if a CSV file is from CS or IBKR by examining its header or structure.
    
    Args:
        filename: Path to the CSV file
        
    Returns:
        'cs' for Charles Schwab files, 'ibkr' for Interactive Brokers files
    """
    logging.debug(f"Starting file type detection for: {filename}")
    
    with open(filename, 'r', newline='') as csvfile:
        # Read first line to detect format
        first_line = csvfile.readline().strip()
        logging.debug(f"First line: {first_line}")
        
        # Check if first line starts with "Positions for account Brokerage" (CS format)
        if first_line.startswith("Positions for account") or first_line.startswith('"Positions for account'):
            logging.debug(f"Detected CS format (first line starts with 'Positions for account')")
            return 'cs'
        
        # Check if first line starts with "Symbol" (IBKR format)
        if first_line.startswith('"Symbol"') or first_line.startswith('Symbol'):
            logging.debug(f"Detected IBKR format (first line starts with 'Symbol')")
            return 'ibkr'
    
    # Unable to detect file type - raise an error
    error_msg = f"Unable to detect file type for {filename}. File must start with either 'Positions for account Brokerage' (CS) or '\"Symbol\"' (IBKR)"
    logging.error(error_msg)
    raise ValueError(error_msg)

def load_shares_generic(ioaShares, filename):
    """
    Generic function to load shares from a file, automatically detecting the format.
    
    Args:
        ioaShares: List to append share objects to
        filename: Path to the CSV file
    """
    file_type = detect_file_type(filename)
    logging.info(f"Detected file type '{file_type}' for {filename}")
    
    if file_type == 'cs':
        loadSharesCs(ioaShares, filename)
    else:
        loadSharesIBKR(ioaShares, filename)

# Custom merge function
def merge_objects(iShare1, iShare2):
    if iShare1 and iShare2:  # Both objects exist
        aMergedShare = aShare(iShare1.symbol)
        aMergedShare.nbShares = iShare1.nbShares + iShare2.nbShares  
        #Verify if we have a price for both stock
        if iShare1.sharePrice and iShare2.sharePrice:
            if not prices_within_range(iShare1.sharePrice, iShare2.sharePrice):
                logging.error(f"Prices for {iShare1.symbol} are not within range: {iShare1.sharePrice} vs {iShare2.sharePrice}")
                raise ValueError(f"Prices for {iShare1.symbol} are not within range: {iShare1.sharePrice} vs {iShare2.sharePrice}")
            else:
                logging.info(f"Prices for {iShare1.symbol} are within range: {iShare1.sharePrice} vs {iShare2.sharePrice}")
                aMergedShare.sharePrice = iShare1.sharePrice
        return aMergedShare
    elif iShare1:  # Only iShare1 exists
        return iShare1
    elif iShare2:  # Only iShare2 exists
        return iShare2

# Function to merge two lists with unmatched objects
def merge_lists(list1, list2, merge_func):
    # Create dictionaries for quick lookup by 'id'
    dict1 = {obj.symbol: obj for obj in list1}
    dict2 = {obj.symbol: obj for obj in list2}
    
    # Union of all keys from both lists
    all_ids = set(dict1.keys()).union(dict2.keys())
    
    merged_list = []
    for obj_id in all_ids:
        merged_obj = merge_func(dict1.get(obj_id), dict2.get(obj_id))
        if merged_obj:
            merged_list.append(merged_obj)
    
    return merged_list

def prices_within_range(price1, price2, percent_range=10):
    """
    Check if two prices are within a specified percentage range of each other.
    
    Args:
        price1: First price
        price2: Second price
        percent_range: Percentage range allowed (default 10%)
        
    Returns:
        Boolean indicating if prices are within range
    """
    if price1 == 0 or price2 == 0:  # Avoid division by zero
        return price1 == price2
    
    # Calculate percentage difference relative to the average
    avg_price = (price1 + price2) / 2
    difference = abs(price1 - price2)
    percent_diff = (difference / avg_price) * 100
    
    return percent_diff <= percent_range
    
if __name__ == "__main__":
    args = parse_arguments()

    setup_logging()
    
    aSharesIBKR = []
    aTotalShares = []

    # Use generic file loading if --files is provided
    if args.files:
        print("Loading share infos from provided files (auto-detecting format)")
        for file_path in args.files:
            print(f"Loading share infos from file: {file_path}")
            aTempShares = []
            load_shares_generic(aTempShares, file_path)
            aTotalShares = merge_lists(aTotalShares, aTempShares, merge_objects)
            print(f"Total shares after merging file {file_path}: {len(aTotalShares)}")
    else:
        # Legacy mode: use separate CS and IBKR files
        print("Loading CS share infos")
        aCsFiles = args.cs_files
        for cs_file in aCsFiles:   
            print(f"Loading CS share infos from file: {cs_file}") 
            aTempShares = []
            loadSharesCs(aTempShares, cs_file)
            aTotalShares = merge_lists(aTotalShares, aTempShares, merge_objects)
            print(f"Total shares after merging file {cs_file}: {len(aTotalShares)}")

        print("Loading IBKR share info")
        loadSharesIBKR(aSharesIBKR, args.ibkr_file)

        aTotalShares = merge_lists(aTotalShares, aSharesIBKR, merge_objects)

    aTotalShares = merge_lists(aTotalShares, aSharesIBKR, merge_objects)

    logging.info(f"Writing positions to file: {args.output}")
    with open(args.output, 'w', newline='') as file2:
        writer = csv.writer(file2)
        field = ["ticker", "nbShares", "price"]
        
        writer.writerow(field)
        for aShare in aTotalShares:
            writer.writerow([aShare.symbol, aShare.nbShares, aShare.sharePrice])
