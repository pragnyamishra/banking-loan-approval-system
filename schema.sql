-- ============================================================
-- Banking Loan Approval System - Database Schema
-- PostgreSQL 15+
-- ============================================================

-- Drop tables if they exist (for clean re-creation)
DROP TABLE IF EXISTS Payment CASCADE;
DROP TABLE IF EXISTS RiskAssessment CASCADE;
DROP TABLE IF EXISTS Loan CASCADE;
DROP TABLE IF EXISTS Customer CASCADE;

-- ============================================================
-- CUSTOMER TABLE
-- ============================================================
CREATE TABLE Customer (
    CustomerID SERIAL PRIMARY KEY,
    Name VARCHAR(100),
    AnnualIncome DECIMAL(12,2) NOT NULL,
    EmploymentLength INTEGER,
    CreditScore INTEGER NOT NULL CHECK (CreditScore BETWEEN 300 AND 850),
    HomeOwnership VARCHAR(20),
    State VARCHAR(2),
    VerificationStatus VARCHAR(30),
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for Customer table
CREATE INDEX idx_customer_credit_score ON Customer(CreditScore);
CREATE INDEX idx_customer_annual_income ON Customer(AnnualIncome);

-- ============================================================
-- LOAN TABLE
-- ============================================================
CREATE TABLE Loan (
    LoanID SERIAL PRIMARY KEY,
    CustomerID INTEGER NOT NULL,
    OriginalLoanID BIGINT UNIQUE NOT NULL,  -- Original 'id' from LendingClub
    LoanAmount DECIMAL(12,2) NOT NULL CHECK (LoanAmount > 0),
    InterestRate DECIMAL(5,2) NOT NULL CHECK (InterestRate >= 0),
    LoanPurpose VARCHAR(50) NOT NULL,
    LoanStatus VARCHAR(50) NOT NULL,
    LoanTerm INTEGER NOT NULL CHECK (LoanTerm IN (36, 60)),  -- 36 or 60 months
    LoanGrade VARCHAR(2),
    IssueDate DATE,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (CustomerID) REFERENCES Customer(CustomerID) ON DELETE RESTRICT ON UPDATE CASCADE
);

-- Indexes for Loan table
CREATE INDEX idx_loan_customer ON Loan(CustomerID);
CREATE INDEX idx_loan_status ON Loan(LoanStatus);
CREATE INDEX idx_loan_purpose ON Loan(LoanPurpose);
CREATE INDEX idx_loan_issue_date ON Loan(IssueDate);
CREATE INDEX idx_loan_original_id ON Loan(OriginalLoanID);

-- ============================================================
-- PAYMENT TABLE
-- ============================================================
CREATE TABLE Payment (
    PaymentID SERIAL PRIMARY KEY,
    LoanID INTEGER NOT NULL,
    PaymentDate DATE,
    AmountPaid DECIMAL(12,2) CHECK (AmountPaid >= 0),
    TotalPayment DECIMAL(12,2) NOT NULL CHECK (TotalPayment >= 0),
    PrincipalReceived DECIMAL(12,2) CHECK (PrincipalReceived >= 0),
    InterestReceived DECIMAL(12,2) CHECK (InterestReceived >= 0),
    PaymentStatus VARCHAR(20) DEFAULT 'Completed',
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (LoanID) REFERENCES Loan(LoanID) ON DELETE CASCADE ON UPDATE CASCADE
);

-- Indexes for Payment table
CREATE INDEX idx_payment_loan ON Payment(LoanID);
CREATE INDEX idx_payment_date ON Payment(PaymentDate);

-- ============================================================
-- RISK ASSESSMENT TABLE (Weak Entity - 1:1 with Loan)
-- ============================================================
CREATE TABLE RiskAssessment (
    RiskID SERIAL PRIMARY KEY,
    LoanID INTEGER NOT NULL UNIQUE,  -- UNIQUE enforces 1:1 relationship
    DTI DECIMAL(5,2) CHECK (DTI >= 0),  -- Debt-to-Income ratio
    Delinquencies INTEGER CHECK (Delinquencies >= 0),
    CreditInquiries INTEGER CHECK (CreditInquiries >= 0),
    RevolvingUtilization DECIMAL(5,2),
    PublicRecords INTEGER CHECK (PublicRecords >= 0),
    OpenAccounts INTEGER CHECK (OpenAccounts >= 0),
    TotalAccounts INTEGER CHECK (TotalAccounts >= 0),
    DefaultPrediction VARCHAR(10),  -- 'Yes' or 'No'
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (LoanID) REFERENCES Loan(LoanID) ON DELETE CASCADE ON UPDATE CASCADE
);

-- Indexes for RiskAssessment table
CREATE INDEX idx_risk_loan ON RiskAssessment(LoanID);
CREATE INDEX idx_risk_dti ON RiskAssessment(DTI);
CREATE INDEX idx_risk_default_pred ON RiskAssessment(DefaultPrediction);

-- ============================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================

-- View: Complete Loan Information with Customer Details
CREATE OR REPLACE VIEW vw_loan_details AS
SELECT 
    l.LoanID,
    l.OriginalLoanID,
    l.LoanAmount,
    l.InterestRate,
    l.LoanPurpose,
    l.LoanStatus,
    l.LoanTerm,
    l.LoanGrade,
    l.IssueDate,
    c.CustomerID,
    c.Name AS CustomerName,
    c.AnnualIncome,
    c.EmploymentLength,
    c.CreditScore,
    c.HomeOwnership,
    c.State,
    r.DTI,
    r.Delinquencies,
    r.DefaultPrediction
FROM Loan l
INNER JOIN Customer c ON l.CustomerID = c.CustomerID
LEFT JOIN RiskAssessment r ON l.LoanID = r.LoanID;

-- View: Payment Summary by Loan
CREATE OR REPLACE VIEW vw_payment_summary AS
SELECT 
    l.LoanID,
    l.OriginalLoanID,
    l.LoanAmount,
    l.LoanStatus,
    COUNT(p.PaymentID) AS TotalPayments,
    SUM(p.AmountPaid) AS TotalAmountPaid,
    SUM(p.PrincipalReceived) AS TotalPrincipalReceived,
    SUM(p.InterestReceived) AS TotalInterestReceived,
    MAX(p.PaymentDate) AS LastPaymentDate
FROM Loan l
LEFT JOIN Payment p ON l.LoanID = p.LoanID
GROUP BY l.LoanID, l.OriginalLoanID, l.LoanAmount, l.LoanStatus;

-- View: High-Risk Loans
CREATE OR REPLACE VIEW vw_high_risk_loans AS
SELECT 
    l.LoanID,
    l.OriginalLoanID,
    l.LoanAmount,
    l.LoanStatus,
    c.CustomerName,
    c.CreditScore,
    r.DTI,
    r.Delinquencies,
    r.DefaultPrediction
FROM vw_loan_details l
JOIN Customer c ON l.CustomerID = c.CustomerID
JOIN RiskAssessment r ON l.LoanID = r.LoanID
WHERE r.DefaultPrediction = 'Yes' 
   OR r.DTI > 30 
   OR r.Delinquencies > 0
   OR c.CreditScore < 650;

-- ============================================================
-- SAMPLE COMPLEX QUERIES (For Testing)
-- ============================================================

-- Query 1: Loans by Status with Customer Info
-- SELECT * FROM vw_loan_details WHERE LoanStatus = 'Current' LIMIT 10;

-- Query 2: Payment Summary
-- SELECT * FROM vw_payment_summary WHERE LoanStatus = 'Fully Paid' LIMIT 10;

-- Query 3: High-Risk Loans
-- SELECT * FROM vw_high_risk_loans LIMIT 10;

-- Query 4: Average Loan Amount by Purpose
-- SELECT LoanPurpose, AVG(LoanAmount) AS AvgAmount, COUNT(*) AS TotalLoans
-- FROM Loan GROUP BY LoanPurpose ORDER BY AvgAmount DESC;

-- Query 5: Customer Risk Profile
-- SELECT c.CustomerID, c.Name, c.CreditScore, AVG(r.DTI) AS AvgDTI, COUNT(l.LoanID) AS TotalLoans
-- FROM Customer c
-- INNER JOIN Loan l ON c.CustomerID = l.CustomerID
-- LEFT JOIN RiskAssessment r ON l.LoanID = r.LoanID
-- GROUP BY c.CustomerID, c.Name, c.CreditScore
-- ORDER BY c.CreditScore ASC;

-- ============================================================
-- GRANT PERMISSIONS (Adjust as needed)
-- ============================================================
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO your_username;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO your_username;

-- ============================================================
-- VERIFICATION QUERIES
-- ============================================================

-- Check table structure
-- SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';

-- Check foreign key constraints
-- SELECT
--     tc.table_name, 
--     tc.constraint_name, 
--     tc.constraint_type,
--     kcu.column_name,
--     ccu.table_name AS foreign_table_name,
--     ccu.column_name AS foreign_column_name
-- FROM information_schema.table_constraints AS tc 
-- JOIN information_schema.key_column_usage AS kcu
--   ON tc.constraint_name = kcu.constraint_name
-- JOIN information_schema.constraint_column_usage AS ccu
--   ON ccu.constraint_name = tc.constraint_name
-- WHERE tc.constraint_type = 'FOREIGN KEY';

COMMENT ON TABLE Customer IS 'Stores customer information including income, employment, and credit score';
COMMENT ON TABLE Loan IS 'Stores loan details including amount, interest rate, purpose, and status';
COMMENT ON TABLE Payment IS 'Stores payment history for each loan';
COMMENT ON TABLE RiskAssessment IS 'Stores risk metrics for each loan (1:1 relationship with Loan)';
