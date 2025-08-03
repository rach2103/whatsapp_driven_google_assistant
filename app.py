"""
Court Data Fetcher & Mini-Dashboard
Main Flask application file
"""

import os
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///court_data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

# Initialize models with the db instance
import models
models.db = db

# Import models after db initialization
from models import Query, Case, Order

# Import services
from services.court_scraper import CourtScraper
from services.captcha_solver import CaptchaSolver

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.getenv('LOG_FILE', 'logs/court_fetcher.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize services
court_scraper = CourtScraper()
captcha_solver = CaptchaSolver()

@app.route('/')
def index():
    """Main dashboard page"""
    try:
        # Get recent queries for dashboard
        recent_queries = Query.query.order_by(Query.timestamp.desc()).limit(10).all()
        
        # Get statistics
        total_queries = Query.query.count()
        successful_queries = Query.query.filter_by(search_status='success').count()
        success_rate = (successful_queries / total_queries * 100) if total_queries > 0 else 0
        
        stats = {
            'total_queries': total_queries,
            'successful_queries': successful_queries,
            'success_rate': round(success_rate, 2),
            'recent_queries': recent_queries
        }
        
        return render_template('index.html', stats=stats)
    except Exception as e:
        logger.error(f"Error loading dashboard: {str(e)}")
        flash('Error loading dashboard. Please try again.', 'error')
        return render_template('index.html', stats={})

@app.route('/search')
def search_form():
    """Case search form page"""
    return render_template('search.html')

@app.route('/api/search', methods=['POST'])
def api_search():
    """API endpoint for case search"""
    try:
        # Get form data
        data = request.get_json() if request.is_json else request.form
        
        court_name = data.get('court', '').strip()
        case_type = data.get('case_type', '').strip()
        case_number = data.get('case_number', '').strip()
        filing_year = data.get('filing_year', '').strip()
        
        # Validate input
        if not all([court_name, case_type, case_number, filing_year]):
            return jsonify({
                'status': 'error',
                'message': 'All fields are required'
            }), 400
        
        try:
            filing_year = int(filing_year)
            if filing_year < 1950 or filing_year > datetime.now().year:
                raise ValueError("Invalid year")
        except ValueError:
            return jsonify({
                'status': 'error',
                'message': 'Invalid filing year'
            }), 400
        
        # Log the query
        query = Query(
            court_name=court_name,
            case_type=case_type,
            case_number=case_number,
            filing_year=filing_year,
            search_status='pending'
        )
        db.session.add(query)
        db.session.commit()
        
        logger.info(f"Starting case search: {case_type} {case_number}/{filing_year} in {court_name}")
        
        # Perform the search
        try:
            result = court_scraper.search_case(
                court_name=court_name,
                case_type=case_type,
                case_number=case_number,
                filing_year=filing_year
            )
            
            if result['status'] == 'success':
                # Update query status
                query.search_status = 'success'
                query.response_data = json.dumps(result['data'])
                
                # Save case data
                case_data = result['data']
                case = Case(
                    query_id=query.id,
                    cnr_number=case_data.get('cnr_number'),
                    case_title=case_data.get('case_title'),
                    petitioner=case_data.get('petitioner'),
                    respondent=case_data.get('respondent'),
                    filing_date=datetime.strptime(case_data.get('filing_date'), '%Y-%m-%d').date() if case_data.get('filing_date') else None,
                    next_hearing_date=datetime.strptime(case_data.get('next_hearing'), '%Y-%m-%d').date() if case_data.get('next_hearing') else None,
                    case_status=case_data.get('status'),
                    court_name=court_name,
                    judge_name=case_data.get('judge_name')
                )
                db.session.add(case)
                db.session.flush()  # Get the case ID
                
                # Save orders
                for order_data in case_data.get('orders', []):
                    order = Order(
                        case_id=case.id,
                        order_date=datetime.strptime(order_data.get('date'), '%Y-%m-%d').date() if order_data.get('date') else None,
                        order_type=order_data.get('type'),
                        pdf_url=order_data.get('pdf_url')
                    )
                    db.session.add(order)
                
                db.session.commit()
                logger.info(f"Case search successful: {case_type} {case_number}/{filing_year}")
                
                return jsonify(result)
            else:
                # Update query with error
                query.search_status = 'failed'
                query.error_message = result.get('message', 'Unknown error')
                db.session.commit()
                
                logger.warning(f"Case search failed: {result.get('message')}")
                return jsonify(result), 404
                
        except Exception as scraping_error:
            # Update query with error
            query.search_status = 'error'
            query.error_message = str(scraping_error)
            db.session.commit()
            
            logger.error(f"Scraping error: {str(scraping_error)}")
            return jsonify({
                'status': 'error',
                'message': 'Error fetching case data. Please try again.'
            }), 500
    
    except Exception as e:
        logger.error(f"API search error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Internal server error'
        }), 500

@app.route('/case/<int:case_id>')
def view_case(case_id):
    """View detailed case information"""
    try:
        case = Case.query.get_or_404(case_id)
        orders = Order.query.filter_by(case_id=case_id).order_by(Order.order_date.desc()).all()
        
        return render_template('case_detail.html', case=case, orders=orders)
    except Exception as e:
        logger.error(f"Error viewing case {case_id}: {str(e)}")
        flash('Error loading case details.', 'error')
        return redirect(url_for('index'))

@app.route('/download/order/<int:order_id>')
def download_order(order_id):
    """Download order/judgment PDF"""
    try:
        order = Order.query.get_or_404(order_id)
        
        if order.local_pdf_path and os.path.exists(order.local_pdf_path):
            return send_file(order.local_pdf_path, as_attachment=True)
        elif order.pdf_url:
            # Download and serve the PDF
            pdf_path = court_scraper.download_pdf(order.pdf_url, order_id)
            if pdf_path:
                order.local_pdf_path = pdf_path
                order.pdf_downloaded = True
                db.session.commit()
                return send_file(pdf_path, as_attachment=True)
        
        flash('PDF not available for download.', 'error')
        return redirect(url_for('view_case', case_id=order.case_id))
    
    except Exception as e:
        logger.error(f"Error downloading order {order_id}: {str(e)}")
        flash('Error downloading PDF.', 'error')
        return redirect(url_for('index'))

@app.route('/api/courts')
def api_courts():
    """Get list of available courts"""
    courts = [
        {'id': 'delhi_district', 'name': 'Delhi District Courts'},
        {'id': 'mumbai_district', 'name': 'Mumbai District Courts'},
        {'id': 'bangalore_district', 'name': 'Bangalore District Courts'},
        {'id': 'chennai_district', 'name': 'Chennai District Courts'},
        {'id': 'kolkata_district', 'name': 'Kolkata District Courts'},
        {'id': 'hyderabad_district', 'name': 'Hyderabad District Courts'},
    ]
    return jsonify(courts)

@app.route('/api/case-types')
def api_case_types():
    """Get list of case types"""
    case_types = [
        {'id': 'civil', 'name': 'Civil Cases'},
        {'id': 'criminal', 'name': 'Criminal Cases'},
        {'id': 'family', 'name': 'Family Cases'},
        {'id': 'commercial', 'name': 'Commercial Cases'},
        {'id': 'writ', 'name': 'Writ Petitions'},
        {'id': 'appeal', 'name': 'Appeals'},
        {'id': 'revision', 'name': 'Revision Petitions'},
        {'id': 'misc', 'name': 'Miscellaneous Cases'},
    ]
    return jsonify(case_types)

@app.route('/history')
def search_history():
    """View search history"""
    try:
        page = request.args.get('page', 1, type=int)
        queries = Query.query.order_by(Query.timestamp.desc()).paginate(
            page=page, per_page=20, error_out=False
        )
        return render_template('history.html', queries=queries)
    except Exception as e:
        logger.error(f"Error loading history: {str(e)}")
        flash('Error loading search history.', 'error')
        return redirect(url_for('index'))

@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', 
                         error_code=404, 
                         error_message="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('error.html', 
                         error_code=500, 
                         error_message="Internal server error"), 500

# Create tables on startup
def create_tables():
    """Create database tables"""
    try:
        with app.app_context():
            db.create_all()
            logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")

# Call create_tables when module is imported
create_tables()

if __name__ == '__main__':
    # Ensure required directories exist
    os.makedirs('logs', exist_ok=True)
    os.makedirs('downloads/pdfs', exist_ok=True)
    
    # Run the application
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
        debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    )