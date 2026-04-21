"""
Banking Loan Approval System - Main Flask Application
Group 9: Mohan, Pragnya, Sneha, Yuktha
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from database import get_db
from config import config
import os

app = Flask(__name__)
app.config.from_object(config['development'])

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_pagination_info(page, total_count, per_page=20):
    """Calculate pagination information"""
    total_pages = (total_count + per_page - 1) // per_page
    offset = (page - 1) * per_page
    
    return {
        'page': page,
        'per_page': per_page,
        'total_pages': total_pages,
        'total_count': total_count,
        'offset': offset,
        'has_prev': page > 1,
        'has_next': page < total_pages
    }

# ============================================================
# HOME & DASHBOARD ROUTES
# ============================================================

@app.route('/')
def index():
    """Homepage - Dashboard"""
    db = get_db()
    if not db:
        return render_template('error.html', error="Database connection failed"), 500
    
    try:
        # Get summary statistics
        stats = {}
        
        # Total customers
        result = db.execute_one("SELECT COUNT(*) as count FROM Customer")
        stats['total_customers'] = result['count'] if result else 0
        
        # Total loans
        result = db.execute_one("SELECT COUNT(*) as count FROM Loan")
        stats['total_loans'] = result['count'] if result else 0
        
        # Total loan amount
        result = db.execute_one("SELECT SUM(LoanAmount) as total FROM Loan")
        stats['total_loan_amount'] = float(result['total']) if result and result['total'] else 0
        
        # Average interest rate
        result = db.execute_one("SELECT AVG(InterestRate) as avg_rate FROM Loan")
        stats['avg_interest_rate'] = float(result['avg_rate']) if result and result['avg_rate'] else 0
        
        # Loan status distribution
        loan_status = db.execute_query("""
            SELECT LoanStatus, COUNT(*) as count 
            FROM Loan 
            GROUP BY LoanStatus 
            ORDER BY count DESC
        """)
        
        # Loan purpose distribution
        loan_purpose = db.execute_query("""
            SELECT LoanPurpose, COUNT(*) as count 
            FROM Loan 
            GROUP BY LoanPurpose 
            ORDER BY count DESC 
            LIMIT 10
        """)
        
        # High risk loans count
        result = db.execute_one("""
            SELECT COUNT(*) as count 
            FROM RiskAssessment 
            WHERE DefaultPrediction = 'Yes'
        """)
        stats['high_risk_loans'] = result['count'] if result else 0
        
        # Recent loans
        recent_loans = db.execute_query("""
            SELECT 
                l.LoanID, l.LoanAmount, l.InterestRate, l.LoanStatus, l.IssueDate,
                c.Name as CustomerName, c.CreditScore
            FROM Loan l
            INNER JOIN Customer c ON l.CustomerID = c.CustomerID
            ORDER BY l.LoanID DESC
            LIMIT 10
        """)
        
    except Exception as e:
        print(f"Error fetching dashboard data: {e}")
        return render_template('error.html', error=str(e)), 500
    finally:
        db.close()
    
    return render_template('dashboard.html', 
                         stats=stats,
                         loan_status=loan_status,
                         loan_purpose=loan_purpose,
                         recent_loans=recent_loans)

# ============================================================
# CUSTOMER ROUTES
# ============================================================

@app.route('/customers')
def customers():
    """List all customers"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    db = get_db()
    if not db:
        return render_template('error.html', error="Database connection failed"), 500
    
    try:
        # Count total customers (for pagination)
        if search:
            count_query = """
                SELECT COUNT(*) as count FROM Customer 
                WHERE Name ILIKE %s OR State ILIKE %s
            """
            result = db.execute_one(count_query, (f'%{search}%', f'%{search}%'))
        else:
            result = db.execute_one("SELECT COUNT(*) as count FROM Customer")
        
        total_count = result['count'] if result else 0
        pagination = get_pagination_info(page, total_count)
        
        # Fetch customers
        if search:
            query = """
                SELECT * FROM Customer 
                WHERE Name ILIKE %s OR State ILIKE %s
                ORDER BY CustomerID DESC
                LIMIT %s OFFSET %s
            """
            customers_list = db.execute_query(query, (f'%{search}%', f'%{search}%', 
                                                       pagination['per_page'], pagination['offset']))
        else:
            query = """
                SELECT * FROM Customer 
                ORDER BY CustomerID DESC
                LIMIT %s OFFSET %s
            """
            customers_list = db.execute_query(query, (pagination['per_page'], pagination['offset']))
        
    except Exception as e:
        print(f"Error fetching customers: {e}")
        return render_template('error.html', error=str(e)), 500
    finally:
        db.close()
    
    return render_template('customers/list.html', 
                         customers=customers_list,
                         pagination=pagination,
                         search=search)

@app.route('/customers/<int:customer_id>')
def customer_detail(customer_id):
    """View customer details"""
    db = get_db()
    if not db:
        return render_template('error.html', error="Database connection failed"), 500
    
    try:
        # Get customer info
        customer = db.execute_one("""
            SELECT * FROM Customer WHERE CustomerID = %s
        """, (customer_id,))
        
        if not customer:
            return render_template('error.html', error="Customer not found"), 404
        
        # Get customer's loans
        loans = db.execute_query("""
            SELECT * FROM Loan WHERE CustomerID = %s ORDER BY LoanID DESC
        """, (customer_id,))
        
        # Get loan statistics for this customer
        stats = db.execute_one("""
            SELECT 
                COUNT(*) as total_loans,
                SUM(LoanAmount) as total_amount,
                AVG(InterestRate) as avg_rate
            FROM Loan
            WHERE CustomerID = %s
        """, (customer_id,))
        
    except Exception as e:
        print(f"Error fetching customer details: {e}")
        return render_template('error.html', error=str(e)), 500
    finally:
        db.close()
    
    return render_template('customers/detail.html', 
                         customer=customer,
                         loans=loans,
                         stats=stats)

# ============================================================
# LOAN ROUTES
# ============================================================

@app.route('/loans')
def loans():
    """List all loans"""
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    purpose_filter = request.args.get('purpose', '')
    
    db = get_db()
    if not db:
        return render_template('error.html', error="Database connection failed"), 500
    
    try:
        # Build WHERE clause based on filters
        where_clauses = []
        params = []
        
        if status_filter:
            where_clauses.append("l.LoanStatus = %s")
            params.append(status_filter)
        
        if purpose_filter:
            where_clauses.append("l.LoanPurpose = %s")
            params.append(purpose_filter)
        
        where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
        
        # Count total loans
        count_query = f"SELECT COUNT(*) as count FROM Loan l {where_sql}"
        result = db.execute_one(count_query, tuple(params))
        total_count = result['count'] if result else 0
        pagination = get_pagination_info(page, total_count)
        
        # Fetch loans with customer info
        query = f"""
            SELECT 
                l.*, c.Name as CustomerName, c.CreditScore, c.AnnualIncome
            FROM Loan l
            INNER JOIN Customer c ON l.CustomerID = c.CustomerID
            {where_sql}
            ORDER BY l.LoanID DESC
            LIMIT %s OFFSET %s
        """
        params.extend([pagination['per_page'], pagination['offset']])
        loans_list = db.execute_query(query, tuple(params))
        
        # Get distinct statuses and purposes for filter dropdowns
        statuses = db.execute_query("SELECT DISTINCT LoanStatus FROM Loan ORDER BY LoanStatus")
        purposes = db.execute_query("SELECT DISTINCT LoanPurpose FROM Loan ORDER BY LoanPurpose")
        
    except Exception as e:
        print(f"Error fetching loans: {e}")
        return render_template('error.html', error=str(e)), 500
    finally:
        db.close()
    
    return render_template('loans/list.html',
                         loans=loans_list,
                         pagination=pagination,
                         statuses=statuses,
                         purposes=purposes,
                         status_filter=status_filter,
                         purpose_filter=purpose_filter)

@app.route('/loans/<int:loan_id>')
def loan_detail(loan_id):
    """View loan details"""
    db = get_db()
    if not db:
        return render_template('error.html', error="Database connection failed"), 500
    
    try:
        # Get loan info with customer details
        loan = db.execute_one("""
            SELECT 
                l.*, c.Name as CustomerName, c.AnnualIncome, c.CreditScore,
                c.EmploymentLength, c.HomeOwnership, c.State
            FROM Loan l
            INNER JOIN Customer c ON l.CustomerID = c.CustomerID
            WHERE l.LoanID = %s
        """, (loan_id,))
        
        if not loan:
            return render_template('error.html', error="Loan not found"), 404
        
        # Get risk assessment
        risk = db.execute_one("""
            SELECT * FROM RiskAssessment WHERE LoanID = %s
        """, (loan_id,))
        
        # Get payments
        payments = db.execute_query("""
            SELECT * FROM Payment WHERE LoanID = %s ORDER BY PaymentDate DESC
        """, (loan_id,))
        
        # Calculate payment summary
        payment_summary = db.execute_one("""
            SELECT 
                COUNT(*) as total_payments,
                SUM(AmountPaid) as total_paid,
                SUM(PrincipalReceived) as total_principal,
                SUM(InterestReceived) as total_interest
            FROM Payment
            WHERE LoanID = %s
        """, (loan_id,))
        
    except Exception as e:
        print(f"Error fetching loan details: {e}")
        return render_template('error.html', error=str(e)), 500
    finally:
        db.close()
    
    return render_template('loans/detail.html',
                         loan=loan,
                         risk=risk,
                         payments=payments,
                         payment_summary=payment_summary)

# ============================================================
# PAYMENT ROUTES
# ============================================================

@app.route('/payments')
def payments():
    """List all payments"""
    page = request.args.get('page', 1, type=int)
    
    db = get_db()
    if not db:
        return render_template('error.html', error="Database connection failed"), 500
    
    try:
        # Count total payments
        result = db.execute_one("SELECT COUNT(*) as count FROM Payment")
        total_count = result['count'] if result else 0
        pagination = get_pagination_info(page, total_count)
        
        # Fetch payments with loan info
        query = """
            SELECT 
                p.*, l.OriginalLoanID, l.LoanAmount, l.LoanStatus,
                c.Name as CustomerName
            FROM Payment p
            INNER JOIN Loan l ON p.LoanID = l.LoanID
            INNER JOIN Customer c ON l.CustomerID = c.CustomerID
            ORDER BY p.PaymentDate DESC, p.PaymentID DESC
            LIMIT %s OFFSET %s
        """
        payments_list = db.execute_query(query, (pagination['per_page'], pagination['offset']))
        
    except Exception as e:
        print(f"Error fetching payments: {e}")
        return render_template('error.html', error=str(e)), 500
    finally:
        db.close()
    
    return render_template('payments/list.html',
                         payments=payments_list,
                         pagination=pagination)

# ============================================================
# ANALYTICS ROUTES
# ============================================================

@app.route('/analytics')
def analytics():
    """Analytics dashboard"""
    db = get_db()
    if not db:
        return render_template('error.html', error="Database connection failed"), 500
    
    try:
        # Loan amount by purpose
        loan_by_purpose = db.execute_query("""
            SELECT LoanPurpose, 
                   COUNT(*) as count,
                   SUM(LoanAmount) as total_amount,
                   AVG(LoanAmount) as avg_amount
            FROM Loan
            GROUP BY LoanPurpose
            ORDER BY total_amount DESC
        """)
        
        # Loans by status
        loan_by_status = db.execute_query("""
            SELECT LoanStatus, COUNT(*) as count
            FROM Loan
            GROUP BY LoanStatus
            ORDER BY count DESC
        """)
        
        # Credit score distribution
        credit_score_dist = db.execute_query("""
            SELECT 
                CASE 
                    WHEN CreditScore < 600 THEN 'Poor (< 600)'
                    WHEN CreditScore < 650 THEN 'Fair (600-649)'
                    WHEN CreditScore < 700 THEN 'Good (650-699)'
                    WHEN CreditScore < 750 THEN 'Very Good (700-749)'
                    ELSE 'Excellent (750+)'
                END as score_range,
                COUNT(*) as count
            FROM Customer
            GROUP BY score_range
            ORDER BY MIN(CreditScore)
        """)
        
        # Default prediction analysis
        default_analysis = db.execute_query("""
            SELECT 
                r.DefaultPrediction,
                COUNT(*) as count,
                AVG(r.DTI) as avg_dti,
                AVG(c.CreditScore) as avg_credit_score
            FROM RiskAssessment r
            INNER JOIN Loan l ON r.LoanID = l.LoanID
            INNER JOIN Customer c ON l.CustomerID = c.CustomerID
            GROUP BY r.DefaultPrediction
        """)
        
    except Exception as e:
        print(f"Error fetching analytics: {e}")
        return render_template('error.html', error=str(e)), 500
    finally:
        db.close()
    
    return render_template('analytics/dashboard.html',
                         loan_by_purpose=loan_by_purpose,
                         loan_by_status=loan_by_status,
                         credit_score_dist=credit_score_dist,
                         default_analysis=default_analysis)

# ============================================================
# API ROUTES (JSON)
# ============================================================

@app.route('/api/stats')
def api_stats():
    """Get dashboard statistics as JSON"""
    db = get_db()
    if not db:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        stats = {}
        result = db.execute_one("SELECT COUNT(*) as count FROM Customer")
        stats['total_customers'] = result['count']
        
        result = db.execute_one("SELECT COUNT(*) as count FROM Loan")
        stats['total_loans'] = result['count']
        
        result = db.execute_one("SELECT SUM(LoanAmount) as total FROM Loan")
        stats['total_loan_amount'] = float(result['total']) if result['total'] else 0
        
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

# ============================================================
# ERROR HANDLERS
# ============================================================

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error="Page not found"), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template('error.html', error="Internal server error"), 500

# ============================================================
# MAIN
# ============================================================

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
