#!/usr/bin/env python3
"""
LendingClub Dataset Analyzer - Updated for accepted and rejected loan files
This script helps analyze large CSV files and create manageable samples
"""

import pandas as pd
import os
import sys

def get_file_info(filepath):
    """
    Get basic file information
    """
    if os.path.exists(filepath):
        size_bytes = os.path.getsize(filepath)
        size_mb = size_bytes / (1024 * 1024)
        size_gb = size_bytes / (1024 * 1024 * 1024)
        
        print(f"\n{'='*60}")
        print(f"FILE INFORMATION")
        print(f"{'='*60}")
        print(f"Filename: {os.path.basename(filepath)}")
        print(f"Size: {size_mb:.2f} MB ({size_gb:.3f} GB)")
        print(f"Full path: {filepath}")
        
        return True
    else:
        print(f"✗ File not found: {filepath}")
        return False

def analyze_csv_structure(filepath, nrows=1000):
    """
    Analyze the structure of a CSV file by reading first N rows
    """
    print(f"\n{'='*60}")
    print(f"ANALYZING: {os.path.basename(filepath)}")
    print(f"{'='*60}\n")
    
    try:
        # Read first N rows to understand structure
        print(f"Reading first {nrows} rows to analyze structure...")
        df_sample = pd.read_csv(filepath, nrows=nrows, low_memory=False)
        
        print(f"✓ File loaded successfully!")
        print(f"✓ Sample size: {len(df_sample)} rows")
        print(f"✓ Total columns: {len(df_sample.columns)}\n")
        
        # Display columns
        print("COLUMN NAMES:")
        print("-" * 60)
        for i, col in enumerate(df_sample.columns, 1):
            print(f"{i:3d}. {col}")
        
        print(f"\n{'='*60}")
        print("FIRST 3 ROWS:")
        print(f"{'='*60}")
        print(df_sample.head(3))
        
        print(f"\n{'='*60}")
        print("BASIC STATISTICS FOR NUMERIC COLUMNS:")
        print(f"{'='*60}")
        print(df_sample.describe())
        
        return df_sample
        
    except Exception as e:
        print(f"✗ Error reading file: {e}")
        return None

def identify_relevant_columns(df, file_type='accepted'):
    """
    Identify columns relevant to our loan approval system
    """
    print(f"\n{'='*60}")
    print(f"IDENTIFYING RELEVANT COLUMNS FOR OUR SCHEMA")
    print(f"{'='*60}\n")
    
    # Mapping of our schema to LendingClub columns
    if file_type == 'accepted':
        relevant_columns = {
            'Customer': {
                'emp_length': 'EmploymentLength',
                'annual_inc': 'AnnualIncome', 
                'fico_range_high': 'CreditScore (high)',
                'fico_range_low': 'CreditScore (low)',
                'emp_title': 'EmploymentTitle (optional)',
                'home_ownership': 'HomeOwnership (optional)',
                'verification_status': 'IncomeVerification (optional)'
            },
            'Loan': {
                'id': 'LoanID (unique identifier)',
                'member_id': 'CustomerID (link to customer)',
                'loan_amnt': 'LoanAmount',
                'int_rate': 'InterestRate',
                'purpose': 'LoanPurpose',
                'loan_status': 'LoanStatus',
                'issue_d': 'IssueDate',
                'term': 'LoanTerm',
                'grade': 'LoanGrade'
            },
            'Payment': {
                'last_pymnt_d': 'PaymentDate',
                'last_pymnt_amnt': 'AmountPaid',
                'total_pymnt': 'TotalPayment',
                'total_rec_prncp': 'PrincipalReceived',
                'total_rec_int': 'InterestReceived'
            },
            'RiskAssessment': {
                'dti': 'DTI (Debt-to-Income)',
                'delinq_2yrs': 'Delinquencies',
                'inq_last_6mths': 'CreditInquiries',
                'revol_util': 'RevolvingUtilization',
                'pub_rec': 'PublicRecords',
                'open_acc': 'OpenAccounts',
                'total_acc': 'TotalAccounts',
                'collections_12_mths_ex_med': 'Collections'
            }
        }
    else:  # rejected
        relevant_columns = {
            'Customer': {
                'Employment Length': 'EmploymentLength',
                'Annual Income': 'AnnualIncome',
                'Risk_Score': 'CreditScore'
            },
            'Loan': {
                'Amount Requested': 'LoanAmount',
                'Loan Title': 'LoanPurpose',
                'Application Date': 'ApplicationDate'
            },
            'RiskAssessment': {
                'Debt-To-Income Ratio': 'DTI',
                'Risk_Score': 'RiskScore'
            }
        }
    
    found_columns = []
    missing_columns = []
    
    for table, columns in relevant_columns.items():
        print(f"\n{table} Table:")
        print("-" * 40)
        for lc_col, our_col in columns.items():
            if lc_col in df.columns:
                found_columns.append(lc_col)
                # Show sample values
                sample_vals = df[lc_col].dropna().head(3).tolist()
                print(f"  ✓ {lc_col:25s} → {our_col}")
                print(f"    Sample values: {sample_vals}")
            else:
                missing_columns.append(lc_col)
                print(f"  ✗ {lc_col:25s} → {our_col} (NOT FOUND)")
    
    print(f"\n{'='*60}")
    print(f"SUMMARY")
    print(f"{'='*60}")
    print(f"✓ Found columns: {len(found_columns)}")
    print(f"✗ Missing columns: {len(missing_columns)}")
    
    if missing_columns:
        print(f"\nMissing columns: {', '.join(missing_columns)}")
    
    return found_columns

def create_stratified_sample(filepath, output_path, sample_size=10000, random_state=42):
    """
    Create a stratified random sample from a large CSV file
    Reads in chunks to handle large files efficiently
    """
    print(f"\n{'='*60}")
    print(f"CREATING STRATIFIED SAMPLE")
    print(f"{'='*60}\n")
    print(f"Target sample size: {sample_size:,} rows")
    print(f"This will take a few minutes for large files...")
    print(f"Reading data in chunks...\n")
    
    try:
        # First, count total rows to calculate sampling ratio
        print("Step 1: Counting total rows...")
        total_rows = 0
        chunksize = 50000
        
        for i, chunk in enumerate(pd.read_csv(filepath, chunksize=chunksize, low_memory=False), 1):
            total_rows += len(chunk)
            if i % 10 == 0:
                print(f"  Processed {total_rows:,} rows...")
        
        print(f"✓ Total rows in dataset: {total_rows:,}\n")
        
        # Calculate sampling ratio
        if total_rows <= sample_size:
            print(f"⚠ Dataset has fewer rows than requested sample size.")
            print(f"  Using all {total_rows:,} rows")
            sampling_ratio = 1.0
        else:
            sampling_ratio = sample_size / total_rows
            print(f"Sampling ratio: {sampling_ratio:.4f} ({sampling_ratio*100:.2f}%)")
        
        # Read and sample in chunks
        print(f"\nStep 2: Creating sample...")
        sampled_chunks = []
        
        for i, chunk in enumerate(pd.read_csv(filepath, chunksize=chunksize, low_memory=False), 1):
            # Sample from this chunk
            chunk_sample = chunk.sample(frac=sampling_ratio, random_state=random_state)
            sampled_chunks.append(chunk_sample)
            
            if i % 10 == 0:
                print(f"  Sampled chunk {i} ({len(sampled_chunks)} chunks collected)")
        
        # Combine all sampled chunks
        print(f"\nStep 3: Combining samples...")
        df_sample = pd.concat(sampled_chunks, ignore_index=True)
        
        # If we got more than needed, take exact sample size
        if len(df_sample) > sample_size:
            df_sample = df_sample.sample(n=sample_size, random_state=random_state)
        
        print(f"✓ Final sample size: {len(df_sample):,} rows")
        
        # Save sample
        print(f"\nStep 4: Saving to file...")
        df_sample.to_csv(output_path, index=False)
        
        file_size = os.path.getsize(output_path) / (1024 * 1024)
        print(f"✓ Sample saved to: {output_path}")
        print(f"✓ Sample file size: {file_size:.2f} MB\n")
        
        return df_sample
        
    except Exception as e:
        print(f"✗ Error creating sample: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """
    Main execution flow
    """
    print("\n" + "="*60)
    print("LENDINGCLUB DATASET ANALYZER")
    print("For accepted_2007_to_2018Q4.csv and rejected_2007_to_2018Q4.csv")
    print("="*60)
    
    # Check if directory path is provided
    if len(sys.argv) < 2:
        print("\nUsage: python analyze_dataset.py <path_to_directory_with_csv_files>")
        print("\nExample:")
        print("  python analyze_dataset.py /mnt/user-data/uploads/")
        print("\nThe script will look for:")
        print("  - accepted_2007_to_2018Q4.csv")
        print("  - rejected_2007_to_2018Q4.csv")
        sys.exit(1)
    
    data_dir = sys.argv[1]
    
    # Define file paths
    accepted_file = os.path.join(data_dir, "accepted_2007_to_2018Q4.csv")
    rejected_file = os.path.join(data_dir, "rejected_2007_to_2018Q4.csv")
    
    # Check which files exist
    print("\nChecking for dataset files...")
    accepted_exists = get_file_info(accepted_file)
    rejected_exists = get_file_info(rejected_file)
    
    if not accepted_exists and not rejected_exists:
        print("\n✗ No dataset files found in the specified directory!")
        print("\nPlease ensure the directory contains:")
        print("  - accepted_2007_to_2018Q4.csv")
        print("  - rejected_2007_to_2018Q4.csv")
        sys.exit(1)
    
    # Recommend using accepted loans
    print("\n" + "="*60)
    print("RECOMMENDATION")
    print("="*60)
    print("\nFor this project, we recommend using the ACCEPTED loans file because:")
    print("  ✓ Contains complete loan lifecycle data (approval, payments, outcomes)")
    print("  ✓ Has risk assessment details (DTI, delinquencies, credit inquiries)")
    print("  ✓ Includes payment history (critical for Payment table)")
    print("  ✓ More columns relevant to our 4-table schema")
    print("\nThe REJECTED loans file has limited information (mostly just")
    print("application details without loan outcomes or payment data).")
    
    # Choose which file to analyze
    print("\n" + "="*60)
    print("SELECT FILE TO ANALYZE")
    print("="*60)
    
    if accepted_exists and rejected_exists:
        print("\n1. Analyze ACCEPTED loans (RECOMMENDED)")
        print("2. Analyze REJECTED loans")
        print("3. Analyze BOTH files")
        choice = input("\nEnter your choice (1-3, default=1): ").strip() or '1'
    elif accepted_exists:
        print("\nOnly accepted loans file found. Using that.")
        choice = '1'
    else:
        print("\nOnly rejected loans file found. Using that.")
        choice = '2'
    
    files_to_analyze = []
    if choice == '1':
        files_to_analyze = [('accepted', accepted_file)]
    elif choice == '2':
        files_to_analyze = [('rejected', rejected_file)]
    elif choice == '3':
        files_to_analyze = [('accepted', accepted_file), ('rejected', rejected_file)]
    
    # Analyze each file
    for file_type, filepath in files_to_analyze:
        print("\n" + "="*60)
        print(f"ANALYZING {file_type.upper()} LOANS FILE")
        print("="*60)
        
        # Analyze structure with first 1000 rows
        df_sample = analyze_csv_structure(filepath, nrows=1000)
        
        if df_sample is None:
            print(f"\n✗ Failed to analyze {file_type} file. Skipping.")
            continue
        
        # Identify relevant columns
        relevant_cols = identify_relevant_columns(df_sample, file_type)
        
        # Ask if user wants to create sample
        print("\n" + "="*60)
        print("SAMPLE CREATION")
        print("="*60)
        
        create_sample_choice = input(f"\nCreate a sample from {file_type} loans? (y/n, default=y): ").strip().lower() or 'y'
        
        if create_sample_choice == 'y':
            sample_size = input("\nEnter sample size (default: 10000): ").strip()
            sample_size = int(sample_size) if sample_size else 10000
            
            output_file = os.path.join(data_dir, f"{file_type}_loans_sample_{sample_size}.csv")
            
            df_final_sample = create_stratified_sample(filepath, output_file, sample_size)
            
            if df_final_sample is not None:
                print("\n" + "="*60)
                print("SAMPLE CREATED SUCCESSFULLY!")
                print("="*60)
                print(f"\n✓ Sample file: {output_file}")
                print(f"✓ Rows: {len(df_final_sample):,}")
                print(f"✓ Columns: {len(df_final_sample.columns)}")
                
                # Show sample of the data
                print(f"\n{'='*60}")
                print("SAMPLE DATA PREVIEW:")
                print(f"{'='*60}")
                print(df_final_sample.head(3))
                
                print(f"\n{'='*60}")
                print("NEXT STEPS")
                print(f"{'='*60}")
                print(f"\n1. Upload this file to Claude:")
                print(f"   {output_file}")
                print(f"\n2. I will then generate:")
                print(f"   ✓ SQL schema tailored to your data")
                print(f"   ✓ Data transformation scripts")
                print(f"   ✓ Complete Flask application")
                print(f"   ✓ Frontend templates")
                print(f"   ✓ Testing framework")
    
    print("\n" + "="*60)
    print("ANALYSIS COMPLETE!")
    print("="*60)

if __name__ == "__main__":
    main()
