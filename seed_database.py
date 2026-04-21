#!/usr/bin/env python3
"""
Database Seeding Script
Loads preprocessed CSV files into PostgreSQL database
"""

import psycopg2
import pandas as pd
import os
import sys
from datetime import datetime

class DatabaseSeeder:
    def __init__(self, db_config):
        """Initialize database connection"""
        self.db_config = db_config
        self.conn = None
        self.cursor = None
    
    def connect(self):
        """Connect to PostgreSQL database"""
        try:
            self.conn = psycopg2.connect(**self.db_config)
            self.cursor = self.conn.cursor()
            print("✓ Connected to PostgreSQL database")
            return True
        except Exception as e:
            print(f"✗ Error connecting to database: {e}")
            return False
    
    def close(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        print("✓ Database connection closed")
    
    def seed_customers(self, csv_file):
        """Seed Customer table"""
        print("\n" + "-"*60)
        print("Seeding Customer table...")
        print("-"*60)
        
        df = pd.read_csv(csv_file)
        print(f"Loading {len(df):,} customer records...")
        
        insert_query = """
        INSERT INTO Customer (
            CustomerID, Name, AnnualIncome, EmploymentLength, 
            CreditScore, HomeOwnership, State, VerificationStatus
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        success_count = 0
        for _, row in df.iterrows():
            try:
                self.cursor.execute(insert_query, (
                    row['CustomerID'],
                    row['Name'],
                    row['AnnualIncome'],
                    row['EmploymentLength'] if pd.notna(row['EmploymentLength']) else None,
                    row['CreditScore'],
                    row['HomeOwnership'],
                    row['State'],
                    row['VerificationStatus']
                ))
                success_count += 1
            except Exception as e:
                print(f"  ✗ Error inserting customer {row['CustomerID']}: {e}")
        
        self.conn.commit()
        print(f"✓ Inserted {success_count:,} customer records")
        return success_count
    
    def seed_loans(self, csv_file):
        """Seed Loan table"""
        print("\n" + "-"*60)
        print("Seeding Loan table...")
        print("-"*60)
        
        df = pd.read_csv(csv_file)
        print(f"Loading {len(df):,} loan records...")
        
        insert_query = """
        INSERT INTO Loan (
            LoanID, CustomerID, OriginalLoanID, LoanAmount, 
            InterestRate, LoanPurpose, LoanStatus, LoanTerm, 
            LoanGrade, IssueDate
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        success_count = 0
        for _, row in df.iterrows():
            try:
                self.cursor.execute(insert_query, (
                    row['LoanID'],
                    row['CustomerID'],
                    row['OriginalLoanID'],
                    row['LoanAmount'],
                    row['InterestRate'],
                    row['LoanPurpose'],
                    row['LoanStatus'],
                    row['LoanTerm'],
                    row['LoanGrade'],
                    row['IssueDate'] if pd.notna(row['IssueDate']) else None
                ))
                success_count += 1
            except Exception as e:
                print(f"  ✗ Error inserting loan {row['LoanID']}: {e}")
        
        self.conn.commit()
        print(f"✓ Inserted {success_count:,} loan records")
        return success_count
    
    def seed_payments(self, csv_file):
        """Seed Payment table"""
        print("\n" + "-"*60)
        print("Seeding Payment table...")
        print("-"*60)
        
        df = pd.read_csv(csv_file)
        print(f"Loading {len(df):,} payment records...")
        
        insert_query = """
        INSERT INTO Payment (
            PaymentID, LoanID, PaymentDate, AmountPaid, 
            TotalPayment, PrincipalReceived, InterestReceived, PaymentStatus
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        success_count = 0
        for _, row in df.iterrows():
            try:
                self.cursor.execute(insert_query, (
                    row['PaymentID'],
                    row['LoanID'],
                    row['PaymentDate'] if pd.notna(row['PaymentDate']) else None,
                    row['AmountPaid'] if pd.notna(row['AmountPaid']) else None,
                    row['TotalPayment'],
                    row['PrincipalReceived'] if pd.notna(row['PrincipalReceived']) else None,
                    row['InterestReceived'] if pd.notna(row['InterestReceived']) else None,
                    row['PaymentStatus']
                ))
                success_count += 1
            except Exception as e:
                print(f"  ✗ Error inserting payment {row['PaymentID']}: {e}")
        
        self.conn.commit()
        print(f"✓ Inserted {success_count:,} payment records")
        return success_count
    
    def seed_risk_assessments(self, csv_file):
        """Seed RiskAssessment table"""
        print("\n" + "-"*60)
        print("Seeding RiskAssessment table...")
        print("-"*60)
        
        df = pd.read_csv(csv_file)
        print(f"Loading {len(df):,} risk assessment records...")
        
        insert_query = """
        INSERT INTO RiskAssessment (
            RiskID, LoanID, DTI, Delinquencies, CreditInquiries,
            RevolvingUtilization, PublicRecords, OpenAccounts, 
            TotalAccounts, DefaultPrediction
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        success_count = 0
        for _, row in df.iterrows():
            try:
                self.cursor.execute(insert_query, (
                    row['RiskID'],
                    row['LoanID'],
                    row['DTI'] if pd.notna(row['DTI']) else None,
                    row['Delinquencies'] if pd.notna(row['Delinquencies']) else None,
                    row['CreditInquiries'] if pd.notna(row['CreditInquiries']) else None,
                    row['RevolvingUtilization'] if pd.notna(row['RevolvingUtilization']) else None,
                    row['PublicRecords'] if pd.notna(row['PublicRecords']) else None,
                    row['OpenAccounts'] if pd.notna(row['OpenAccounts']) else None,
                    row['TotalAccounts'] if pd.notna(row['TotalAccounts']) else None,
                    row['DefaultPrediction']
                ))
                success_count += 1
            except Exception as e:
                print(f"  ✗ Error inserting risk assessment {row['RiskID']}: {e}")
        
        self.conn.commit()
        print(f"✓ Inserted {success_count:,} risk assessment records")
        return success_count
    
    def verify_data(self):
        """Verify data was loaded correctly"""
        print("\n" + "="*60)
        print("DATA VERIFICATION")
        print("="*60)
        
        tables = ['Customer', 'Loan', 'Payment', 'RiskAssessment']
        
        for table in tables:
            self.cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = self.cursor.fetchone()[0]
            print(f"✓ {table}: {count:,} records")
        
        # Verify foreign key relationships
        print("\n" + "-"*60)
        print("Verifying foreign key relationships...")
        print("-"*60)
        
        # Check loans have valid customers
        self.cursor.execute("""
            SELECT COUNT(*) FROM Loan l 
            LEFT JOIN Customer c ON l.CustomerID = c.CustomerID 
            WHERE c.CustomerID IS NULL
        """)
        orphan_loans = self.cursor.fetchone()[0]
        print(f"✓ Orphan loans (no customer): {orphan_loans}")
        
        # Check payments have valid loans
        self.cursor.execute("""
            SELECT COUNT(*) FROM Payment p 
            LEFT JOIN Loan l ON p.LoanID = l.LoanID 
            WHERE l.LoanID IS NULL
        """)
        orphan_payments = self.cursor.fetchone()[0]
        print(f"✓ Orphan payments (no loan): {orphan_payments}")
        
        # Check risk assessments have valid loans
        self.cursor.execute("""
            SELECT COUNT(*) FROM RiskAssessment r 
            LEFT JOIN Loan l ON r.LoanID = l.LoanID 
            WHERE l.LoanID IS NULL
        """)
        orphan_risks = self.cursor.fetchone()[0]
        print(f"✓ Orphan risk assessments (no loan): {orphan_risks}")
        
        # Sample query - Loan details with customer info
        print("\n" + "-"*60)
        print("Sample Query: Loan details with customer info (first 3)")
        print("-"*60)
        
        self.cursor.execute("""
            SELECT 
                l.LoanID, l.LoanAmount, l.InterestRate, l.LoanStatus,
                c.Name, c.AnnualIncome, c.CreditScore
            FROM Loan l
            INNER JOIN Customer c ON l.CustomerID = c.CustomerID
            LIMIT 3
        """)
        
        results = self.cursor.fetchall()
        for row in results:
            print(f"  Loan #{row[0]}: ${row[1]:,.2f} @ {row[2]}% - {row[3]}")
            print(f"    Customer: {row[4]} (Income: ${row[5]:,.2f}, Score: {row[6]})")

def main():
    """Main seeding function"""
    print("="*60)
    print("DATABASE SEEDING SCRIPT")
    print("="*60)
    
    # Database configuration
    # Update these values for your PostgreSQL setup
    db_config = {
        'host': 'localhost',
        'port': 5432,
        'database': 'loan_approval_db',
        'user': 'pragnya',
        'password': ''  # Change this to your password
    }
    
    # CSV file locations
    data_dir = "/Users/pragnya/Documents/Fundamental of DB/project/loan-approval-system/data/processed"
    csv_files = {
        'customers': os.path.join(data_dir, 'customers.csv'),
        'loans': os.path.join(data_dir, 'loans.csv'),
        'payments': os.path.join(data_dir, 'payments.csv'),
        'risk_assessments': os.path.join(data_dir, 'risk_assessments.csv')
    }
    
    # Check if files exist
    print("\nChecking for CSV files...")
    for name, filepath in csv_files.items():
        if os.path.exists(filepath):
            size = os.path.getsize(filepath) / 1024  # KB
            print(f"✓ {name}.csv found ({size:.2f} KB)")
        else:
            print(f"✗ {name}.csv NOT FOUND at {filepath}")
            sys.exit(1)
    
    # Initialize seeder
    seeder = DatabaseSeeder(db_config)
    
    # Connect to database
    if not seeder.connect():
        print("\n✗ Failed to connect to database. Please check:")
        print("  1. PostgreSQL is running")
        print("  2. Database 'loan_approval_db' exists")
        print("  3. Username and password are correct")
        sys.exit(1)
    
    try:
        start_time = datetime.now()
        
        # Seed tables in order (respecting foreign keys)
        total_records = 0
        total_records += seeder.seed_customers(csv_files['customers'])
        total_records += seeder.seed_loans(csv_files['loans'])
        total_records += seeder.seed_payments(csv_files['payments'])
        total_records += seeder.seed_risk_assessments(csv_files['risk_assessments'])
        
        # Verify data
        seeder.verify_data()
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print("\n" + "="*60)
        print("SEEDING COMPLETE!")
        print("="*60)
        print(f"✓ Total records inserted: {total_records:,}")
        print(f"✓ Time taken: {duration:.2f} seconds")
        print("\nDatabase is ready for use!")
        
    except Exception as e:
        print(f"\n✗ Error during seeding: {e}")
        import traceback
        traceback.print_exc()
        seeder.conn.rollback()
    
    finally:
        seeder.close()

if __name__ == "__main__":
    main()
