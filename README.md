# 🏦 Banking Loan Approval System

A complete web-based loan portfolio management system built with Flask and PostgreSQL, featuring real-time analytics, risk assessment, and payment tracking.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-336791.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 📸 Screenshots

### Executive Dashboard
*Professional banking interface with real-time KPIs and data flow visualization*

### Features Overview
- 💼 **Customer Management**: Track 9,992+ customer profiles with credit scores and demographics
- 💰 **Loan Portfolio**: Manage complete loan lifecycle from application to payment
- 📊 **Risk Assessment**: 1:1 risk evaluation for every loan with DTI and delinquency tracking
- 💳 **Payment Tracking**: Complete transaction history with principal/interest breakdown
- 📈 **Analytics Dashboard**: Interactive charts showing portfolio performance

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- PostgreSQL 15 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/banking-loan-system.git
   cd banking-loan-system
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Activate virtual environment
   # On Mac/Linux:
   source venv/bin/activate
   
   # On Windows:
   venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.template .env
   
   # Edit .env and update these values:
   # DB_USER=your_postgres_username
   # DB_PASSWORD=your_postgres_password
   ```

5. **Create PostgreSQL database**
   ```bash
   # Connect to PostgreSQL
   psql -U postgres
   
   # Create database
   CREATE DATABASE loan_approval_db;
   \q
   ```

6. **Load database schema**
   ```bash
   psql -U postgres -d loan_approval_db -f schema.sql
   ```

7. **Process and load sample data**
   ```bash
   # Process the LendingClub dataset
   python data_preprocessing.py
   
   # Load data into database
   python seed_database.py
   ```

8. **Run the application**
   ```bash
   python app.py
   ```

9. **Open your browser**
   ```
   http://localhost:5000
   ```

---

## 🗄️ Database Schema

### Entity Relationship Overview

```
Customer (9,992 records)
    ↓ (1:N)
Loan (9,992 records)
    ↓ (1:1)              ↓ (1:N)
RiskAssessment       Payment (9,983 records)
(9,992 records)
```

### Tables

#### Customer
- Stores customer demographics, income, credit scores
- Primary Key: `CustomerID`

#### Loan
- Loan details, amounts, rates, status
- Primary Key: `LoanID`
- Foreign Key: `CustomerID` → Customer

#### RiskAssessment
- Risk metrics for each loan (1:1 relationship)
- Primary Key: `RiskID`
- Foreign Key: `LoanID` → Loan (UNIQUE)

#### Payment
- Transaction history for each loan
- Primary Key: `PaymentID`
- Foreign Key: `LoanID` → Loan

---

## 🎨 Features

### Dashboard
- Real-time portfolio KPIs
- Data flow visualization showing table relationships
- Interactive charts (Chart.js)
- Business intelligence insights

### Customer Management
- Browse 9,992+ customers
- Search and filter functionality
- Customer profile with complete loan history
- Credit score tracking

### Loan Portfolio
- Filter by status (Current, Fully Paid, Charged Off)
- Filter by purpose (Debt Consolidation, Credit Card, etc.)
- Detailed loan view with risk assessment
- Customer information integration

### Payment Tracking
- Complete payment transaction history
- Principal and interest breakdown
- Payment summaries by loan
- Date-based tracking

### Analytics
- Loan distribution charts
- Credit score analysis
- Risk assessment metrics
- Default prediction insights

---

## 🛠️ Technology Stack

### Backend
- **Flask 3.0** - Python web framework
- **PostgreSQL 15** - Relational database
- **psycopg2** - PostgreSQL adapter
- **pandas** - Data processing

### Frontend
- **Bootstrap 5** - UI framework
- **Chart.js** - Data visualization
- **DataTables** - Interactive tables
- **Font Awesome** - Icons

### Data Source
- **LendingClub Dataset** - 9,992 real loan records (2007-2018)

---

## 📊 Sample Queries

### View all high-risk loans
```sql
SELECT * FROM vw_high_risk_loans 
ORDER BY DTI DESC 
LIMIT 20;
```

### Analyze loan performance by purpose
```sql
SELECT 
    LoanPurpose,
    COUNT(*) as TotalLoans,
    AVG(LoanAmount) as AvgAmount,
    AVG(InterestRate) as AvgRate
FROM Loan
GROUP BY LoanPurpose
ORDER BY TotalLoans DESC;
```

### Customer risk profile
```sql
SELECT 
    c.CustomerID,
    c.Name,
    c.CreditScore,
    COUNT(l.LoanID) as TotalLoans,
    AVG(r.DTI) as AvgDTI
FROM Customer c
INNER JOIN Loan l ON c.CustomerID = l.CustomerID
LEFT JOIN RiskAssessment r ON l.LoanID = r.LoanID
GROUP BY c.CustomerID, c.Name, c.CreditScore
ORDER BY c.CreditScore ASC;
```

---

## 📁 Project Structure

```
banking-loan-system/
├── app.py                      # Main Flask application
├── config.py                   # Configuration settings
├── database.py                 # Database connection module
├── schema.sql                  # PostgreSQL schema
├── data_preprocessing.py       # Data transformation script
├── seed_database.py            # Database seeding script
├── requirements.txt            # Python dependencies
├── .env.template               # Environment variables template
├── .gitignore                  # Git ignore rules
├── README.md                   # This file
├── data/
│   └── processed/              # Processed CSV files (not in repo)
├── templates/                  # HTML templates
│   ├── base.html
│   ├── dashboard.html
│   ├── error.html
│   ├── customers/
│   ├── loans/
│   ├── payments/
│   └── analytics/
└── static/                     # Static files
    ├── css/
    │   └── style.css
    └── js/
        └── main.js
```

---

## 🔒 Security Notes

- Never commit `.env` file with real credentials
- Use environment variables for sensitive data
- Change `SECRET_KEY` in production
- Use proper PostgreSQL user permissions
- Enable SSL for production database connections

---

## 🚀 Deployment

### Heroku
```bash
# Add Procfile
echo "web: gunicorn app:app" > Procfile

# Add runtime.txt
echo "python-3.10.0" > runtime.txt

# Install gunicorn
pip install gunicorn
pip freeze > requirements.txt

# Deploy
heroku create your-app-name
heroku addons:create heroku-postgresql:mini
git push heroku main
```

### Railway
1. Connect your GitHub repository
2. Add PostgreSQL database
3. Set environment variables
4. Deploy automatically

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 👥 Team

**Group 9 - Database Systems Project**

- Mohan Kalyan Guntupalli
- Pragnya Mishra
- Sneha Yarrapothu
- Yuktha Nagalla

**Course**: CSCE 5350 - Database Systems  
**University**: University of North Texas

---

## 🙏 Acknowledgments

- Dataset: LendingClub Loan Data from Kaggle
- Instructor: [Your Professor's Name]
- Course: CSCE 5350 - Database Systems

---

## 📞 Support

For issues or questions:
1. Check the [Issues](https://github.com/YOUR_USERNAME/banking-loan-system/issues) page
2. Review the documentation
3. Contact team members

---

## 🔄 Updates

### Version 1.0 (Current)
- ✅ Complete loan management system
- ✅ 9,992 real loan records
- ✅ Professional UI/UX
- ✅ Interactive analytics
- ✅ Database relationship visualization

---

**⭐ Star this repository if you found it helpful!**
