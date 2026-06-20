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
    single_stocks = ['MSFT', 'SBIT', 'IBM', 'BILI', 'VEOEY', 'VEEV', 'NOW', 'AMZN', 'AMC', 'SPIP', 'BRK/B', 'GOOGL', 'CLSK','GOOG','DOCS','ADSK','WDAY','CRM']
    return aSymbol.upper() in single_stocks

def parse_arguments():
    parser = argparse.ArgumentParser(description='Process shares data from CS and IBKR.')
    parser.add_argument('--ibkr', type=str, default=None,
                      help='IBKR account positions CSV file')
    parser.add_argument('--cs', type=str, default=None,
                      help='Charles Schwab brokerage account positions CSV file')
    parser.add_argument('--ira', type=str, default=None,
                      help='IRA (Charles Schwab) account positions CSV file')
    parser.add_argument('--output', default='holdings.csv',
                      help='Output file path (default: holdings.csv)')
    parser.add_argument('--target', type=str, default='targets.json',
                      help='Target JSON file path (default: targets.json)')
    parser.add_argument('--fund-info', type=str, default='fund_info.json',
                      help='Fund info JSON file path for descriptions (default: fund_info.json)')
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

def load_fund_info(fund_info_file='fund_info.json'):
    """
    Load fund descriptions from fund_info JSON file.

    Args:
        fund_info_file: Path to the fund_info JSON file

    Returns:
        Dictionary mapping stock symbols to fund info objects
    """
    try:
        with open(fund_info_file, 'r') as f:
            fund_info = json.load(f)
        logging.info(f"Loaded {len(fund_info)} fund info entries from {fund_info_file}")
        return fund_info
    except FileNotFoundError:
        logging.warning(f"Fund info file '{fund_info_file}' not found. No descriptions will be added.")
        return {}
    except json.JSONDecodeError as e:
        logging.error(f"Error parsing fund info file: {e}")
        return {}

def validate_targets_sum(targets, target_field='target', account_label='global'):
    """
    Validate that the sum of all target values does not exceed 100.
    
    Args:
        targets: Dictionary mapping stock symbols to target objects
        target_field: The field name to use for the target value
        account_label: Human-readable label for the account (used in log messages)
        
    Returns:
        Boolean indicating if targets are valid
    """
    if not targets:
        logging.warning(f"[{account_label}] No targets to validate")
        return True
    
    try:
        # Convert all target values to float and sum them
        total = sum(float(value[target_field]) for value in targets.values() if value and target_field in value)
        logging.info(f"[{account_label}] Total target allocation: {total}%")
        
        if total > 100:
            logging.error(f"[{account_label}] Target allocation exceeds 100%: {total}%")
            return False
        elif total < 100:
            logging.warning(f"[{account_label}] Target allocation is less than 100%: {total}%")
        else:
            logging.info(f"[{account_label}] Target allocation is exactly 100%")
        
        return True
    except (ValueError, TypeError) as e:
        logging.error(f"[{account_label}] Error validating targets: {e}")
        return False
    
if __name__ == "__main__":
    args = parse_arguments()

    setup_logging(debug=args.debug)
    logging.info("Starting PortfolioMerger - Merging positions from CS and IBKR")
    
    aTotalShares = []
    shares_by_account = {'ibkr': {}, 'cs': {}, 'ira': {}}

    # Load share infos from named account files
    if not any([args.ibkr, args.cs, args.ira]):
        logging.error("No files provided. Use --ibkr, --cs, and/or --ira to specify input files.")
        exit(1)

    if args.ibkr:
        logging.info(f"Loading IBKR file: {args.ibkr}")
        aTempShares = []
        loadSharesIBKR(aTempShares, args.ibkr)
        shares_by_account['ibkr'] = {s.symbol: s for s in aTempShares}
        aTotalShares = merge_lists(aTotalShares, aTempShares, merge_objects)
        logging.info(f"Total shares after merging IBKR file: {len(aTotalShares)}")

    if args.cs:
        logging.info(f"Loading CS file: {args.cs}")
        aTempShares = []
        loadSharesCs(aTempShares, args.cs)
        shares_by_account['cs'] = {s.symbol: s for s in aTempShares}
        aTotalShares = merge_lists(aTotalShares, aTempShares, merge_objects)
        logging.info(f"Total shares after merging CS file: {len(aTotalShares)}")

    if args.ira:
        logging.info(f"Loading IRA file: {args.ira}")
        aTempShares = []
        loadSharesCs(aTempShares, args.ira)
        shares_by_account['ira'] = {s.symbol: s for s in aTempShares}
        aTotalShares = merge_lists(aTotalShares, aTempShares, merge_objects)
        logging.info(f"Total shares after merging IRA file: {len(aTotalShares)}")

    # Determine which target field to use based on which accounts were provided
    accounts_provided = [a for a in ['ibkr', 'cs', 'ira'] if getattr(args, a)]
    if len(accounts_provided) == 1:
        target_field = f'target_{accounts_provided[0]}'
    else:
        target_field = 'target_global'

    # Load targets
    logging.info(f"Using target file: {args.target}, target field: {target_field}")
    targets = load_targets(args.target)
    # Fall back to 'target' if the resolved field is not present in the file (old format)
    sample = next(iter(targets.values()), {})
    if target_field not in sample and 'target' in sample:
        logging.info(f"Field '{target_field}' not found in targets file, falling back to 'target'")
        target_field = 'target'
    validate_targets_sum(targets, target_field, account_label='global')

    # Validate per-account allocations
    for account in ['ibkr', 'cs', 'ira']:
        acct_field = f'target_{account}'
        sample_acct = next(iter(targets.values()), {})
        if acct_field in sample_acct:
            validate_targets_sum(targets, acct_field, account_label=account.upper())

    # Load fund info (descriptions)
    logging.info(f"Using fund info file: {args.fund_info}")
    fund_info = load_fund_info(args.fund_info)
    
    # Calculate total and per-account portfolio values
    logging.info("Calculating portfolio values")
    total_portfolio_value = 0.0
    for aShare in aTotalShares:
        total_portfolio_value += aShare.nbShares * aShare.sharePrice

    portfolio_value_by_account = {}
    for account in ['ibkr', 'cs', 'ira']:
        portfolio_value_by_account[account] = sum(
            s.nbShares * s.sharePrice for s in shares_by_account[account].values()
        )

    logging.warning(f"Total Portfolio Value: ${total_portfolio_value:,.2f}")
    for account in ['ibkr', 'cs', 'ira']:
        logging.warning(f"  {account.upper()} Portfolio Value: ${portfolio_value_by_account[account]:,.2f}")

    # Write positions to file with allocation percentages
    logging.info(f"Writing positions to file: {args.output}")
    with open(args.output, 'w', newline='') as file2:
        writer = csv.writer(file2)
        field = [
            "ticker", "description", "sec_yield_30d", "ttm_yield",
            "nbShares", "nbShares_ibkr", "nbShares_cs", "nbShares_ira",
            "price",
            "currentAllocation", "currentAllocation_ibkr", "currentAllocation_cs", "currentAllocation_ira",
            "target_global", "target_ibkr", "target_cs", "target_ira",
            "sharesToTarget_ibkr", "sharesToTarget_cs", "sharesToTarget_ira"
        ]

        writer.writerow(field)
        for aShare in aTotalShares:
            target_obj = targets.get(aShare.symbol, {})
            fund_obj = fund_info.get(aShare.symbol, {})
            description_value = fund_obj.get('description', '') if fund_obj else ''
            sec_yield_30d_value = (fund_obj.get('sec_yield_30d', '') or '').replace('%', '') if fund_obj else ''
            ttm_yield_value = (fund_obj.get('ttm_yield', '') or '').replace('%', '') if fund_obj else ''

            # Total allocation
            holding_value = aShare.nbShares * aShare.sharePrice
            current_allocation = (holding_value / total_portfolio_value * 100) if total_portfolio_value > 0 else 0

            # Per-account data
            nb_by_acct = {}
            alloc_by_acct = {}
            shares_to_target_by_acct = {}
            for account in ['ibkr', 'cs', 'ira']:
                acct_share = shares_by_account[account].get(aShare.symbol)
                nb = acct_share.nbShares if acct_share else 0
                nb_by_acct[account] = nb
                acct_value = nb * aShare.sharePrice
                acct_total = portfolio_value_by_account[account]
                alloc_by_acct[account] = f"{(acct_value / acct_total * 100):.2f}" if acct_total > 0 else '0.00'
                acct_target = target_obj.get(f'target_{account}', '') if target_obj else ''
                if acct_target != '' and aShare.sharePrice > 0:
                    target_dollars = (float(acct_target) / 100) * acct_total
                    shares_needed = (target_dollars - acct_value) / aShare.sharePrice
                    shares_to_target_by_acct[account] = f"{shares_needed:.0f}"
                else:
                    shares_to_target_by_acct[account] = ''

            target_global = target_obj.get('target_global', target_obj.get('target', '')) if target_obj else ''
            target_ibkr   = target_obj.get('target_ibkr', '') if target_obj else ''
            target_cs     = target_obj.get('target_cs', '') if target_obj else ''
            target_ira    = target_obj.get('target_ira', '') if target_obj else ''

            if target_global == '':
                logging.error(f"Missing target for stock: {aShare.symbol}")

            writer.writerow([
                aShare.symbol, description_value, sec_yield_30d_value, ttm_yield_value,
                aShare.nbShares, nb_by_acct['ibkr'], nb_by_acct['cs'], nb_by_acct['ira'],
                aShare.sharePrice,
                f"{current_allocation:.2f}", alloc_by_acct['ibkr'], alloc_by_acct['cs'], alloc_by_acct['ira'],
                target_global, target_ibkr, target_cs, target_ira,
                shares_to_target_by_acct['ibkr'], shares_to_target_by_acct['cs'], shares_to_target_by_acct['ira']
            ])
    
    print(f"\nTotal Portfolio Value: ${total_portfolio_value:,.2f}")
