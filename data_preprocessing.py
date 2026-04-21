#!/usr/bin/env python3
"""
Data Preprocessing Script
Transforms LendingClub dataset into our 4-table schema
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os
import sys

def clean_percentage(value):
    """Convert percentage string to float (e.g., '15.5%' -> 15.5)"""
    if pd.isna(value):
        return None
    if isinstance(value, str) and '%' in value:
        return float(value.replace('%', ''))
    return float(value)

def clean_employment_length(emp_length):
    """Convert employment length string to years"""
    if pd.isna(emp_length):
        return None
    if isinstance(emp_length, (int, float)):
        return int(emp_length)
    
    emp_length = str(emp_length).strip()
    if emp_length == 'n/a' or emp_length == '':
        return None
    if '< 1' in emp_length:
        return 0
    if '10+' in emp_length:
        return 10
    
    # Extract number from strings like "3 years", "5 years"
    try:
        return int(''.join(filter(str.isdigit, emp_length)))
    except:
        return None

def clean_term(term):
    """Extract term in months from string like '36 months'"""
    if pd.isna(term):
        return 36  # Default
    try:
        return int(''.join(filter(str.isdigit, str(term))))
    except:
        return 36

def determine_default_prediction(loan_status):
    """Determine if loan is predicted to default based on status"""
    default_statuses = [
        'Charged Off',
        'Default',
        'Does not meet the credit policy. Status:Charged Off',
        'Late (31-120 days)',
        'Late (16-30 days)'
    ]
    return 'Yes' if loan_status in default_statuses else 'No'

def parse_date(date_str):
    """Parse date in format 'Dec-2015' to YYYY-MM-DD"""
    if pd.isna(date_str) or date_str == '':
        return None
    try:
        # Parse 'Dec-2015' format
        dt = pd.to_datetime(date_str, format='%b-%Y')
        return dt.strftime('%Y-%m-%d')
    except:
        try:
            # Try standard format
            dt = pd.to_datetime(date_str)
            return dt.strftime('%Y-%m-%d')
        except:
            return None

def preprocess_data(input_file, output_dir):
    """
    Main preprocessing function
    """
    print("="*60)
    print("LENDINGCLUB DATA PREPROCESSING")
    print("="*60)
    
    # Read data
    print(f"\nReading data from: {input_file}")
    df = pd.read_csv(input_file, low_memory=False)
    print(f"✓ Loaded {len(df):,} rows with {len(df.columns)} columns")
    
    # ========================================
    # 1. CUSTOMER TABLE
    # ========================================
    print("\n" + "-"*60)
    print("Processing Customer table...")
    print("-"*60)
    
    # Create unique customer records
    # Since member_id is all NaN, we'll use loan id to create synthetic customer IDs
    # Each loan will have a unique customer for this demo
    
    customers = pd.DataFrame({
        'Name': df['id'].apply(lambda x: f'Customer_{x}'),  # Synthetic names
        'AnnualIncome': df['annual_inc'],
        'EmploymentLength': df['emp_length'].apply(clean_employment_length),
        'CreditScore': ((df['fico_range_low'] + df['fico_range_high']) / 2).astype(int),
        'HomeOwnership': df['home_ownership'],
        'State': df['addr_state'],
        'VerificationStatus': df['verification_status']
    })
    
    # Remove duplicates and nulls
    customers = customers.dropna(subset=['AnnualIncome', 'CreditScore'])
    customers.insert(0, 'CustomerID', range(1, len(customers) + 1))
    
    print(f"✓ Created {len(customers):,} customer records")
    print(f"  - Average Annual Income: ${customers['AnnualIncome'].mean():,.2f}")
    print(f"  - Average Credit Score: {customers['CreditScore'].mean():.0f}")
    print(f"  - Employment Length (avg): {customers['EmploymentLength'].mean():.1f} years")
    
    # ========================================
    # 2. LOAN TABLE
    # ========================================
    print("\n" + "-"*60)
    print("Processing Loan table...")
    print("-"*60)
    
    loans = pd.DataFrame({
        'CustomerID': range(1, len(df) + 1),  # Links to customer (1:1 for this demo)
        'OriginalLoanID': df['id'],
        'LoanAmount': df['loan_amnt'],
        'InterestRate': df['int_rate'].apply(clean_percentage),
        'LoanPurpose': df['purpose'],
        'LoanStatus': df['loan_status'],
        'LoanTerm': df['term'].apply(clean_term),
        'LoanGrade': df['grade'],
        'IssueDate': df['issue_d'].apply(parse_date)
    })
    
    # Remove rows with missing critical data
    loans = loans.dropna(subset=['LoanAmount', 'InterestRate', 'LoanPurpose'])
    loans.insert(0, 'LoanID', range(1, len(loans) + 1))
    
    print(f"✓ Created {len(loans):,} loan records")
    print(f"  - Average Loan Amount: ${loans['LoanAmount'].mean():,.2f}")
    print(f"  - Average Interest Rate: {loans['InterestRate'].mean():.2f}%")
    print(f"  - Loan Status Distribution:")
    for status, count in loans['LoanStatus'].value_counts().head(5).items():
        print(f"    • {status}: {count:,}")
    
    # ========================================
    # 3. PAYMENT TABLE
    # ========================================
    print("\n" + "-"*60)
    print("Processing Payment table...")
    print("-"*60)
    
    payments = pd.DataFrame({
        'LoanID': range(1, len(df) + 1),
        'PaymentDate': df['last_pymnt_d'].apply(parse_date),
        'AmountPaid': df['last_pymnt_amnt'],
        'TotalPayment': df['total_pymnt'],
        'PrincipalReceived': df['total_rec_prncp'],
        'InterestReceived': df['total_rec_int'],
        'PaymentStatus': 'Completed'
    })
    
    # Only keep rows where there's actual payment data
    payments = payments[payments['TotalPayment'] > 0]
    payments.insert(0, 'PaymentID', range(1, len(payments) + 1))
    
    print(f"✓ Created {len(payments):,} payment records")
    print(f"  - Average Payment Amount: ${payments['AmountPaid'].mean():,.2f}")
    print(f"  - Average Total Payment: ${payments['TotalPayment'].mean():,.2f}")
    
    # ========================================
    # 4. RISK ASSESSMENT TABLE
    # ========================================
    print("\n" + "-"*60)
    print("Processing RiskAssessment table...")
    print("-"*60)
    
    risk_assessments = pd.DataFrame({
        'LoanID': range(1, len(df) + 1),
        'DTI': df['dti'],
        'Delinquencies': df['delinq_2yrs'],
        'CreditInquiries': df['inq_last_6mths'],
        'RevolvingUtilization': df['revol_util'].apply(clean_percentage),
        'PublicRecords': df['pub_rec'],
        'OpenAccounts': df['open_acc'],
        'TotalAccounts': df['total_acc'],
        'DefaultPrediction': df['loan_status'].apply(determine_default_prediction)
    })
    
    # Remove rows with all null risk data
    risk_assessments = risk_assessments.dropna(subset=['DTI', 'Delinquencies'], how='all')
    risk_assessments.insert(0, 'RiskID', range(1, len(risk_assessments) + 1))
    
    print(f"✓ Created {len(risk_assessments):,} risk assessment records")
    print(f"  - Average DTI: {risk_assessments['DTI'].mean():.2f}%")
    print(f"  - Average Delinquencies: {risk_assessments['Delinquencies'].mean():.2f}")
    print(f"  - Default Prediction:")
    for pred, count in risk_assessments['DefaultPrediction'].value_counts().items():
        print(f"    • {pred}: {count:,}")
    
    # ========================================
    # 5. SAVE TO CSV FILES
    # ========================================
    print("\n" + "="*60)
    print("SAVING PROCESSED DATA")
    print("="*60)
    
    os.makedirs(output_dir, exist_ok=True)
    
    files = {
        'customers.csv': customers,
        'loans.csv': loans,
        'payments.csv': payments,
        'risk_assessments.csv': risk_assessments
    }
    
    for filename, dataframe in files.items():
        filepath = os.path.join(output_dir, filename)
        dataframe.to_csv(filepath, index=False)
        file_size = os.path.getsize(filepath) / 1024  # KB
        print(f"✓ Saved {filename}: {len(dataframe):,} rows ({file_size:.2f} KB)")
    
    # ========================================
    # 6. DATA VALIDATION
    # ========================================
    print("\n" + "="*60)
    print("DATA VALIDATION")
    print("="*60)
    
    print(f"\n✓ CustomerID range: 1 to {len(customers)}")
    print(f"✓ LoanID range: 1 to {len(loans)}")
    print(f"✓ All loans have corresponding customers: {loans['CustomerID'].max() <= len(customers)}")
    print(f"✓ All payments reference valid loans: {payments['LoanID'].max() <= len(loans)}")
    print(f"✓ All risk assessments reference valid loans: {risk_assessments['LoanID'].max() <= len(loans)}")
    
    print("\n" + "="*60)
    print("PREPROCESSING COMPLETE!")
    print("="*60)
    print(f"\nProcessed files saved to: {output_dir}/")
    print("\nNext steps:")
    print("1. Create database: createdb loan_approval_db")
    print("2. Run schema: psql -d loan_approval_db -f schema.sql")
    print("3. Load data: python seed_database.py")

if __name__ == "__main__":
    # Configuration
    input_file = "/mnt/user-data/uploads/accepted_loans_sample_10000.csv"
    output_dir = "/home/claude/data/processed"
    
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    if len(sys.argv) > 2:
        output_dir = sys.argv[2]
    
    # Run preprocessing
    preprocess_data(input_file, output_dir)
