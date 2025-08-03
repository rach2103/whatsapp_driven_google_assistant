"""
Database models for Court Data Fetcher
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

# Database instance - will be initialized in app.py
db = None

class Query(db.Model):
    """Model for storing search queries"""
    __tablename__ = 'queries'
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    court_name = db.Column(db.String(200), nullable=False)
    case_type = db.Column(db.String(100), nullable=False)
    case_number = db.Column(db.String(100), nullable=False)
    filing_year = db.Column(db.Integer, nullable=False)
    search_status = db.Column(db.String(50), nullable=False)  # pending, success, failed, error
    response_data = db.Column(db.Text)  # JSON string of response data
    error_message = db.Column(db.Text)
    
    # Relationship to cases
    cases = db.relationship('Case', backref='query', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Query {self.case_type} {self.case_number}/{self.filing_year}>'
    
    def to_dict(self):
        """Convert query to dictionary"""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'court_name': self.court_name,
            'case_type': self.case_type,
            'case_number': self.case_number,
            'filing_year': self.filing_year,
            'search_status': self.search_status,
            'error_message': self.error_message
        }

class Case(db.Model):
    """Model for storing case information"""
    __tablename__ = 'cases'
    
    id = db.Column(db.Integer, primary_key=True)
    query_id = db.Column(db.Integer, db.ForeignKey('queries.id'), nullable=False)
    cnr_number = db.Column(db.String(50))  # Case Number Registry
    case_title = db.Column(db.String(500))
    petitioner = db.Column(db.String(300))
    respondent = db.Column(db.String(300))
    filing_date = db.Column(db.Date)
    next_hearing_date = db.Column(db.Date)
    case_status = db.Column(db.String(100))
    court_name = db.Column(db.String(200))
    judge_name = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to orders
    orders = db.relationship('Order', backref='case', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Case {self.case_title}>'
    
    def to_dict(self):
        """Convert case to dictionary"""
        return {
            'id': self.id,
            'cnr_number': self.cnr_number,
            'case_title': self.case_title,
            'petitioner': self.petitioner,
            'respondent': self.respondent,
            'filing_date': self.filing_date.isoformat() if self.filing_date else None,
            'next_hearing_date': self.next_hearing_date.isoformat() if self.next_hearing_date else None,
            'case_status': self.case_status,
            'court_name': self.court_name,
            'judge_name': self.judge_name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'orders': [order.to_dict() for order in self.orders]
        }

class Order(db.Model):
    """Model for storing court orders and judgments"""
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('cases.id'), nullable=False)
    order_date = db.Column(db.Date)
    order_type = db.Column(db.String(100))  # Order, Judgment, Interim Order, etc.
    pdf_url = db.Column(db.String(500))  # Original URL from court website
    pdf_downloaded = db.Column(db.Boolean, default=False)
    local_pdf_path = db.Column(db.String(500))  # Local file path after download
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Order {self.order_type} - {self.order_date}>'
    
    def to_dict(self):
        """Convert order to dictionary"""
        return {
            'id': self.id,
            'case_id': self.case_id,
            'order_date': self.order_date.isoformat() if self.order_date else None,
            'order_type': self.order_type,
            'pdf_url': self.pdf_url,
            'pdf_downloaded': self.pdf_downloaded,
            'local_pdf_path': self.local_pdf_path,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class SearchStats(db.Model):
    """Model for storing search statistics"""
    __tablename__ = 'search_stats'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, default=datetime.utcnow().date, nullable=False)
    total_searches = db.Column(db.Integer, default=0)
    successful_searches = db.Column(db.Integer, default=0)
    failed_searches = db.Column(db.Integer, default=0)
    error_searches = db.Column(db.Integer, default=0)
    unique_courts = db.Column(db.Integer, default=0)
    avg_response_time = db.Column(db.Float)  # in seconds
    
    def __repr__(self):
        return f'<SearchStats {self.date}>'
    
    def to_dict(self):
        """Convert stats to dictionary"""
        return {
            'id': self.id,
            'date': self.date.isoformat() if self.date else None,
            'total_searches': self.total_searches,
            'successful_searches': self.successful_searches,
            'failed_searches': self.failed_searches,
            'error_searches': self.error_searches,
            'unique_courts': self.unique_courts,
            'avg_response_time': self.avg_response_time
        }