import re
import csv
import os
import argparse
import logging
import json

# Custom exception for options
class OptionDetectedException(Exception):
    """Raised when an option symbol is detected and should be skipped"""
    pass

# Custom exception for empty lines
class EmptyLineException(Exception):
    """Raised when an empty line is encountered and should be skipped"""
    pass

# Custom exception for single stocks
class SingleStockDetectedException(Exception):
    """Raised when a single stock is detected and should be skipped"""
    pass

# Set up logging configuration at the start of your script
def setup_logging(log_file='trades.log', debug=False):  
    # Full path for log file
    log_path = os.path.join("./", log_file)
    
    # Set log level based on debug flag
    log_level = logging.DEBUG if debug else logging.WARN
    
    # Configure logging
    logging.basicConfig(
        level=log_level,
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

def isItOption(aSymbol):
    # Matches option format: "SPY 12/19/2025 550.00 P"
    return bool(re.fullmatch(r"[A-Z]+\s+\d{1,2}/\d{1,2}/\d{4}\s+\d+\.\d{2}\s+[PC]", aSymbol))

def isItASingleStock(aSymbol):
    single_stocks = ['BILI', 'VEOEY', 'RGTZ', 'PDBA', 'AMZN', 'AMC', 'SPIP', 'BRK/B', 'GOOGL', 'CLSK','GOOG']
    return aSymbol.upper() in single_stocks

def parse_arguments():
    parser = argparse.ArgumentParser(description='Process shares data from CS and IBKR.')
    parser.add_argument('--files', nargs='+',
                      help='List of files to process (auto-detects CS or IBKR format)')
    parser.add_argument('--output', default='holdings.csv',
                      help='Output file path (default: holdings.csv)')
    parser.add_argument('--targets', default='targets',
                      help='Targets file path (default: targets)')
    parser.add_argument('--debug', action='store_true',
                      help='Enable debug logging level')
    return parser.parse_args()

def parseLineCs(aLine):
    # Ignore empty lines
    if not aLine or all(not cell.strip() for cell in aLine):
        raise EmptyLineException("Empty line")
    
    try:
        aTicker = aLine[0]
        logging.debug(f"Processing CS ticker: {aTicker}")
        if isItOption(aTicker):
            logging.debug(f"Skipping option: {aTicker}")
            raise OptionDetectedException(f"Option detected: {aTicker}")
        if isItASingleStock(aTicker):
            logging.debug(f"Skipping single stock: {aTicker}")
            raise SingleStockDetectedException(f"Single stock detected: {aTicker}")
        if not isItProperSymbol(aTicker):
            logging.debug(f"Invalid symbol: {aTicker}")
            raise ValueError(f"Invalid symbol: {aTicker}")
        aNewShare = aShare(aTicker)
        aNewShare.nbShares = int(aLine[3])
        logging.debug(f"aNewShare.nbShares: {aNewShare.nbShares}")
        aNewShare.sharePrice = float(aLine[4][1:])
        return aNewShare
    except OptionDetectedException as e:
        raise e
    except Exception as e:
        raise e

def parseLineCs2(aLine):
    """Parse CS file with new format (2026+) where shares are at index 2 and price at index 3"""
    # Ignore empty lines
    if not aLine or all(not cell.strip() for cell in aLine):
        raise EmptyLineException("Empty line")
    
    try:
        aTicker = aLine[0]
        logging.debug(f"Processing CS ticker (new format): {aTicker}")
        if isItOption(aTicker):
            logging.debug(f"Skipping option: {aTicker}")
            raise OptionDetectedException(f"Option detected: {aTicker}")
        if isItASingleStock(aTicker):
            logging.debug(f"Skipping single stock: {aTicker}")
            raise SingleStockDetectedException(f"Single stock detected: {aTicker}")
        if not isItProperSymbol(aTicker):
            logging.debug(f"Invalid symbol: {aTicker}")
            raise ValueError(f"Invalid symbol: {aTicker}")
        aNewShare = aShare(aTicker)
        aNewShare.nbShares = int(aLine[2])  # New format: shares at index 2
        logging.debug(f"aNewShare.nbShares: {aNewShare.nbShares}")
        aNewShare.sharePrice = float(aLine[3])  # New format: price at index 3
        return aNewShare
    except OptionDetectedException as e:
        raise e
    except Exception as e:
        raise e


def loadSharesCs(ioaShares, filename):
    with open(filename, newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in spamreader:
            try:    
                aNewShare1 = parseLineCs2(row)
                ioaShares.append(aNewShare1)
            except OptionDetectedException as e:
                logging.info(e)
            except SingleStockDetectedException as e:
                logging.info(e)
            except EmptyLineException:
                logging.debug("Skipping empty line")
            except:
                logging.error(f"Error in CS file with row: {row}")

def parseLineIBKR(aLine):
    # Ignore empty lines
    if not aLine or all(not cell.strip() for cell in aLine):
        raise EmptyLineException("Empty line")
    
    try:
        aTicker = aLine[0].strip('\"')
        logging.debug(f"Processing IBKR ticker: {aTicker}")
        if isItOption(aTicker):
            logging.debug(f"Skipping option: {aTicker}")
            raise OptionDetectedException(f"Option detected: {aTicker}")
        if isItASingleStock(aTicker):
            logging.debug(f"Skipping single stock: {aTicker}")
            raise SingleStockDetectedException(f"Single stock detected: {aTicker}")
        if not isItProperSymbol(aTicker):
            logging.debug(f"Invalid symbol: {aTicker}")
            raise ValueError(f"Invalid symbol: {aTicker}")
        
        aNewShare = aShare(aTicker)
        aNewShare.nbShares = int(aLine[1].strip('\"'))
        # Some holdings are only on IBKR so if we don't get the price from there file we miss it in the final output
        aIbkrSharePrice = float(aLine[2].strip('\"'))
        aNewShare.sharePrice = aIbkrSharePrice
        return aNewShare
    except (OptionDetectedException, SingleStockDetectedException):
        raise
    except Exception as e:
        raise e

def loadSharesIBKR(ioaShares, filename):
    with open(filename, newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in spamreader:
            try:
                aNewShare = parseLineIBKR(row)
                ioaShares.append(aNewShare)
            except OptionDetectedException as e:
                logging.info(e)
            except SingleStockDetectedException as e:
                logging.info(e)
            except EmptyLineException:
                logging.debug("Skipping empty line")
            except:
                logging.error(f"Error in IBKR file with row: {row}")

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

def load_targets(targets_file='targets'):
    """
    Load targets from JSON file.
    
    Args:
        targets_file: Path to the targets JSON file
        
    Returns:
        Dictionary mapping stock symbols to target values
    """
    try:
        with open(targets_file, 'r') as f:
            targets = json.load(f)
        logging.info(f"Loaded {len(targets)} targets from {targets_file}")
        return targets
    except FileNotFoundError:
        logging.warning(f"Targets file '{targets_file}' not found. No targets will be added.")
        return {}
    except json.JSONDecodeError as e:
        logging.error(f"Error parsing targets file: {e}")
        return {}

def validate_targets_sum(targets):
    """
    Validate that the sum of all target values does not exceed 100.
    
    Args:
        targets: Dictionary mapping stock symbols to target objects with 'target' and 'description' fields
        
    Returns:
        Boolean indicating if targets are valid
    """
    if not targets:
        logging.warning("No targets to validate")
        return True
    
    try:
        # Convert all target values to float and sum them
        total = sum(float(value['target']) for value in targets.values() if value and 'target' in value)
        logging.info(f"Total target allocation: {total}%")
        
        if total > 100:
            logging.error(f"Target allocation exceeds 100%: {total}%")
            return False
        elif total < 100:
            logging.warning(f"Target allocation is less than 100%: {total}%")
        else:
            logging.info(f"Target allocation is exactly 100%")
        
        return True
    except (ValueError, TypeError) as e:
        logging.error(f"Error validating targets: {e}")
        return False
    
if __name__ == "__main__":
    args = parse_arguments()

    setup_logging(debug=args.debug)
    logging.info("Starting PortfolioMerger - Merging positions from CS and IBKR")
    
    aSharesIBKR = []
    aTotalShares = []

    # Use generic file loading if --files is provided
    if args.files:
        logging.info("Loading share infos from provided files (auto-detecting format)")
        for file_path in args.files:
            logging.debug(f"Loading share infos from file: {file_path}")
            aTempShares = []
            load_shares_generic(aTempShares, file_path)
            aTotalShares = merge_lists(aTotalShares, aTempShares, merge_objects)
            logging.info(f"Total shares after merging file {file_path}: {len(aTotalShares)}")
    else:
        # Legacy mode: use separate CS and IBKR files
        logging.info("Loading CS share infos")
        aCsFiles = args.cs_files
        for cs_file in aCsFiles:   
            logging.info(f"Loading CS share infos from file: {cs_file}") 
            aTempShares = []
            loadSharesCs(aTempShares, cs_file)
            aTotalShares = merge_lists(aTotalShares, aTempShares, merge_objects)
            logging.info(f"Total shares after merging file {cs_file}: {len(aTotalShares)}")

        logging.info("Loading IBKR share info")
        loadSharesIBKR(aSharesIBKR, args.ibkr_file)

        aTotalShares = merge_lists(aTotalShares, aSharesIBKR, merge_objects)

    aTotalShares = merge_lists(aTotalShares, aSharesIBKR, merge_objects)

    # Load targets
    targets = load_targets(args.targets)
    validate_targets_sum(targets)
    
    # Calculate total portfolio value first
    logging.info("Calculating total portfolio value")
    total_portfolio_value = 0.0
    for aShare in aTotalShares:
        holding_value = aShare.nbShares * aShare.sharePrice
        total_portfolio_value += holding_value
    
    logging.warning(f"Total Portfolio Value: ${total_portfolio_value:,.2f}")
    
    # Write positions to file with allocation percentages
    logging.info(f"Writing positions to file: {args.output}")
    with open(args.output, 'w', newline='') as file2:
        writer = csv.writer(file2)
        field = ["ticker", "description", "nbShares", "price", "currentAllocation", "target", "sharesToTarget"]
        
        writer.writerow(field)
        for aShare in aTotalShares:
            target_obj = targets.get(aShare.symbol, {})
            target_value = target_obj.get('target', '') if target_obj else ''
            description_value = target_obj.get('description', '') if target_obj else ''
            if target_value == '':
                logging.error(f"Missing target for stock: {aShare.symbol}")
            
            # Calculate current allocation percentage
            holding_value = aShare.nbShares * aShare.sharePrice
            current_allocation = (holding_value / total_portfolio_value * 100) if total_portfolio_value > 0 else 0
            
            # Calculate shares needed to reach target allocation
            shares_to_target = ''
            if target_value != '' and aShare.sharePrice > 0:
                target_value_dollars = (float(target_value) / 100) * total_portfolio_value
                current_value_dollars = holding_value
                difference_dollars = target_value_dollars - current_value_dollars
                shares_needed = difference_dollars / aShare.sharePrice
                shares_to_target = f"{shares_needed:.0f}"
            
            writer.writerow([aShare.symbol, description_value, aShare.nbShares, aShare.sharePrice, 
                           f"{current_allocation:.2f}", target_value, shares_to_target])
    
    print(f"\nTotal Portfolio Value: ${total_portfolio_value:,.2f}")
