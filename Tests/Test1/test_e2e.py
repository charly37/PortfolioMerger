#!/usr/bin/env python3
"""
End-to-end test for mainBrokers.py
Tests the script with cs1.csv, cs2.csv, and Ibkr1.csv files
"""

import subprocess
import os
import csv
import sys

def run_test():
    """Run the end-to-end test"""
    print("=" * 70)
    print("Running End-to-End Test for mainBrokers.py")
    print("=" * 70)
    
    # Define test files
    test_files = ['./cs1.csv', './cs2.csv', './Ibkr1.csv']
    output_file = './test_output.csv'
    reference_file = './holdings.csv'
    targets_file = './targets'
    
    # Verify test files exist
    print("\n1. Verifying test files exist...")
    for file in test_files:
        if os.path.exists(file):
            print(f"   ✓ {file} found")
        else:
            print(f"   ✗ {file} NOT found")
            return False
    
    # Run the main script with --files parameter
    print(f"\n2. Running mainBrokers.py with files: {', '.join(test_files)}")
    cmd = ['python3', '../../mainBrokers.py', '--files'] + test_files + ['--output', output_file, '--targets', targets_file]
    print(f"   Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        print(f"\n   Exit code: {result.returncode}")
        
        if result.stdout:
            print("\n   STDOUT:")
            for line in result.stdout.split('\n'):
                if line.strip():
                    print(f"   {line}")
        
        if result.stderr:
            print("\n   STDERR:")
            for line in result.stderr.split('\n'):
                if line.strip():
                    print(f"   {line}")
        
        if result.returncode != 0:
            print(f"\n   ✗ Script failed with exit code {result.returncode}")
            return False
            
    except subprocess.TimeoutExpired:
        print("\n   ✗ Script timeout after 30 seconds")
        return False
    except Exception as e:
        print(f"\n   ✗ Error running script: {e}")
        return False
    
    # Verify output file was created
    print(f"\n3. Verifying output file: {output_file}")
    if not os.path.exists(output_file):
        print(f"   ✗ Output file {output_file} was not created")
        return False
    print(f"   ✓ Output file created")
    
    # Read and validate output
    print(f"\n4. Validating output file contents...")
    try:
        with open(output_file, 'r') as f:
            reader = csv.reader(f)
            rows = list(reader)
            
            if len(rows) == 0:
                print("   ✗ Output file is empty")
                return False
            
            # Check header
            header = rows[0]
            expected_header = ['ticker', 'description', 'nbShares', 'price', 'currentAllocation', 'target']
            if header != expected_header:
                print(f"   ✗ Invalid header. Expected {expected_header}, got {header}")
                return False
            print(f"   ✓ Header is correct: {header}")
            
            # Check data rows
            data_rows = rows[1:]
            if len(data_rows) == 0:
                print("   ✗ No data rows in output")
                return False
            
            print(f"   ✓ Found {len(data_rows)} ticker(s) in output")
            
            # Display sample rows
            print("\n   Sample output (first 10 rows):")
            print(f"   {'Ticker':<10} {'Description':<20} {'Shares':<10} {'Price':<10} {'Current%':<10} {'Target%':<10}")
            print(f"   {'-'*10} {'-'*20} {'-'*10} {'-'*10} {'-'*10} {'-'*10}")
            for row in data_rows[:10]:
                if len(row) == 6:
                    print(f"   {row[0]:<10} {row[1]:<20} {row[2]:<10} {row[3]:<10} {row[4]:<10} {row[5]:<10}")
            
            if len(data_rows) > 10:
                print(f"   ... and {len(data_rows) - 10} more")
            
            # Validate data format
            invalid_rows = []
            for i, row in enumerate(data_rows, start=2):
                if len(row) != 6:
                    invalid_rows.append(f"Row {i}: Wrong number of columns ({len(row)})")
                    continue
                
                ticker, description, shares, price, current_allocation, target = row
                
                # Validate shares is a number
                try:
                    float(shares)
                except ValueError:
                    invalid_rows.append(f"Row {i}: Invalid shares value '{shares}'")
                
                # Validate price is a number
                try:
                    float(price)
                except ValueError:
                    invalid_rows.append(f"Row {i}: Invalid price value '{price}'")
                
                # Validate current allocation is a number
                try:
                    float(current_allocation)
                except ValueError:
                    invalid_rows.append(f"Row {i}: Invalid current allocation value '{current_allocation}'")
                
                # Validate target is a number or empty
                if target:
                    try:
                        float(target)
                    except ValueError:
                        invalid_rows.append(f"Row {i}: Invalid target value '{target}'")
            
            if invalid_rows:
                print(f"\n   ✗ Found {len(invalid_rows)} invalid row(s):")
                for err in invalid_rows[:5]:
                    print(f"      {err}")
                if len(invalid_rows) > 5:
                    print(f"      ... and {len(invalid_rows) - 5} more")
                return False
            
            print(f"   ✓ All {len(data_rows)} data rows are valid")
            
    except Exception as e:
        print(f"   ✗ Error reading output file: {e}")
        return False
    
    # Compare with reference file
    print(f"\n5. Comparing output with reference file: {reference_file}")
    
    if not os.path.exists(reference_file):
        print(f"   ⚠ Reference file {reference_file} does not exist - skipping comparison")
    else:
        try:
            # Read generated output
            with open(output_file, 'r') as f:
                generated_rows = list(csv.reader(f))
            
            # Read reference file
            with open(reference_file, 'r') as f:
                reference_rows = list(csv.reader(f))
            
            # Compare row counts
            if len(generated_rows) != len(reference_rows):
                print(f"   ⚠ Row count mismatch: generated={len(generated_rows)}, reference={len(reference_rows)}")
            else:
                print(f"   ✓ Row counts match: {len(generated_rows)} rows")
            
            # Compare headers
            if generated_rows[0] != reference_rows[0]:
                print(f"   ✗ Header mismatch:")
                print(f"      Generated: {generated_rows[0]}")
                print(f"      Reference: {reference_rows[0]}")
                return False
            
            print(f"   ✓ Headers match")
            
            # Sort data rows by ticker for comparison (excluding header)
            generated_data = sorted(generated_rows[1:], key=lambda x: x[0])
            reference_data = sorted(reference_rows[1:], key=lambda x: x[0])
            
            # Compare each row
            mismatches = []
            gen_dict = {row[0]: row for row in generated_data}
            ref_dict = {row[0]: row for row in reference_data}
            
            # Find tickers only in generated
            only_in_gen = set(gen_dict.keys()) - set(ref_dict.keys())
            # Find tickers only in reference
            only_in_ref = set(ref_dict.keys()) - set(gen_dict.keys())
            # Find tickers in both but with different values
            common_tickers = set(gen_dict.keys()) & set(ref_dict.keys())
            
            for ticker in sorted(common_tickers):
                if gen_dict[ticker] != ref_dict[ticker]:
                    mismatches.append({
                        'ticker': ticker,
                        'generated': gen_dict[ticker],
                        'reference': ref_dict[ticker]
                    })
            
            has_differences = len(only_in_gen) > 0 or len(only_in_ref) > 0 or len(mismatches) > 0
            
            if only_in_gen:
                print(f"   ⚠ Tickers only in generated output: {sorted(only_in_gen)}")
            
            if only_in_ref:
                print(f"   ⚠ Tickers only in reference file: {sorted(only_in_ref)}")
            
            if mismatches:
                print(f"   ✗ Found {len(mismatches)} ticker(s) with different values:")
                for mismatch in mismatches[:5]:
                    print(f"      {mismatch['ticker']}:")
                    print(f"         Generated: {mismatch['generated']}")
                    print(f"         Reference: {mismatch['reference']}")
                if len(mismatches) > 5:
                    print(f"      ... and {len(mismatches) - 5} more")
            
            if has_differences:
                return False
            
            print(f"   ✓ All data rows match the reference file")
            
        except Exception as e:
            print(f"   ✗ Error comparing files: {e}")
            return False
    
    # Clean up
    print(f"\n6. Cleaning up test output file...")
    try:
        os.remove(output_file)
        print(f"   ✓ Removed {output_file}")
    except Exception as e:
        print(f"   ⚠ Could not remove {output_file}: {e}")
    
    return True


if __name__ == "__main__":
    print()
    success = run_test()
    
    print("\n" + "=" * 70)
    if success:
        print("✓ END-TO-END TEST PASSED")
        print("=" * 70)
        sys.exit(0)
    else:
        print("✗ END-TO-END TEST FAILED")
        print("=" * 70)
        sys.exit(1)
