"""
Court Scraper Service
Handles web scraping from eCourts portal and other court websites
"""

import os
import time
import logging
import requests
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from .captcha_solver import CaptchaSolver

logger = logging.getLogger(__name__)

class CourtScraper:
    """Main court scraper class"""
    
    def __init__(self):
        self.base_url = os.getenv('ECOURTS_BASE_URL', 'https://services.ecourts.gov.in/ecourtindia_v6/')
        self.timeout = int(os.getenv('REQUEST_TIMEOUT', '30'))
        self.max_retries = int(os.getenv('MAX_RETRIES', '3'))
        self.captcha_solver = CaptchaSolver()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': os.getenv('USER_AGENT', 
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        })
        
    def _get_driver(self):
        """Initialize and return Chrome WebDriver"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument(f'--user-agent={self.session.headers["User-Agent"]}')
        
        try:
            driver = webdriver.Chrome(
                ChromeDriverManager().install(),
                options=chrome_options
            )
            return driver
        except Exception as e:
            logger.error(f"Failed to initialize Chrome driver: {str(e)}")
            raise
    
    def search_case(self, court_name, case_type, case_number, filing_year):
        """
        Search for a case in the court system
        
        Args:
            court_name (str): Name of the court
            case_type (str): Type of case (civil, criminal, etc.)
            case_number (str): Case number
            filing_year (int): Year when case was filed
            
        Returns:
            dict: Search result with case information
        """
        logger.info(f"Searching case: {case_type} {case_number}/{filing_year} in {court_name}")
        
        try:
            # Use eCourts district portal for standardized access
            return self._search_ecourts_district(court_name, case_type, case_number, filing_year)
        except Exception as e:
            logger.error(f"Error searching case: {str(e)}")
            return {
                'status': 'error',
                'message': f'Error searching case: {str(e)}'
            }
    
    def _search_ecourts_district(self, court_name, case_type, case_number, filing_year):
        """Search case in eCourts district portal"""
        driver = None
        try:
            driver = self._get_driver()
            
            # Navigate to eCourts services
            search_url = urljoin(self.base_url, '?p=casestatus')
            driver.get(search_url)
            
            # Wait for page to load
            WebDriverWait(driver, self.timeout).until(
                EC.presence_of_element_located((By.NAME, "state_code"))
            )
            
            # Select state (defaulting to Delhi for demo)
            state_select = Select(driver.find_element(By.NAME, "state_code"))
            state_select.select_by_visible_text("Delhi")
            
            # Wait for district dropdown to populate
            time.sleep(2)
            
            # Select district
            district_select = Select(driver.find_element(By.NAME, "dist_code"))
            district_select.select_by_index(1)  # Select first available district
            
            # Wait for court complex dropdown
            time.sleep(2)
            
            # Select court complex
            complex_select = Select(driver.find_element(By.NAME, "court_complex_code"))
            complex_select.select_by_index(1)  # Select first available complex
            
            # Wait for establishment dropdown
            time.sleep(2)
            
            # Select establishment
            establishment_select = Select(driver.find_element(By.NAME, "court_code"))
            establishment_select.select_by_index(1)  # Select first available establishment
            
            # Click on Case Number tab
            case_number_tab = driver.find_element(By.XPATH, "//a[contains(text(), 'Case Number')]")
            case_number_tab.click()
            
            time.sleep(1)
            
            # Fill case search form
            case_type_select = Select(driver.find_element(By.NAME, "case_type"))
            try:
                # Try to find matching case type
                case_type_select.select_by_visible_text(case_type.title())
            except:
                # If exact match not found, select first option
                case_type_select.select_by_index(1)
            
            # Enter case number
            case_number_input = driver.find_element(By.NAME, "case_no")
            case_number_input.clear()
            case_number_input.send_keys(str(case_number))
            
            # Enter filing year
            year_input = driver.find_element(By.NAME, "case_year")
            year_input.clear()
            year_input.send_keys(str(filing_year))
            
            # Handle CAPTCHA
            captcha_solved = self._solve_captcha(driver)
            if not captcha_solved:
                return {
                    'status': 'error',
                    'message': 'Failed to solve CAPTCHA'
                }
            
            # Submit form
            submit_button = driver.find_element(By.XPATH, "//input[@value='Go']")
            submit_button.click()
            
            # Wait for results
            time.sleep(3)
            
            # Check for results
            try:
                # Look for case results table
                results_table = driver.find_element(By.XPATH, "//table[contains(@class, 'case_details') or contains(@id, 'case')]")
                return self._parse_case_results(driver, court_name)
            except NoSuchElementException:
                # Check for "No records found" message
                page_source = driver.page_source.lower()
                if 'no record found' in page_source or 'no case found' in page_source:
                    return {
                        'status': 'not_found',
                        'message': 'No case found with the provided details'
                    }
                else:
                    return {
                        'status': 'error',
                        'message': 'Unexpected response from court website'
                    }
        
        except TimeoutException:
            logger.error("Timeout while searching case")
            return {
                'status': 'error',
                'message': 'Timeout while searching case. Court website may be slow.'
            }
        except Exception as e:
            logger.error(f"Error in eCourts search: {str(e)}")
            return {
                'status': 'error',
                'message': f'Error searching case: {str(e)}'
            }
        finally:
            if driver:
                driver.quit()
    
    def _solve_captcha(self, driver):
        """Solve CAPTCHA on the page"""
        try:
            # Find CAPTCHA image
            captcha_img = driver.find_element(By.XPATH, "//img[contains(@src, 'captcha') or contains(@alt, 'captcha')]")
            captcha_url = captcha_img.get_attribute('src')
            
            # Get CAPTCHA solution
            captcha_text = self.captcha_solver.solve_captcha(captcha_url)
            
            if captcha_text:
                # Find CAPTCHA input field
                captcha_input = driver.find_element(By.NAME, "captcha_code")
                captcha_input.clear()
                captcha_input.send_keys(captcha_text)
                return True
            else:
                logger.error("Failed to solve CAPTCHA")
                return False
                
        except Exception as e:
            logger.error(f"Error solving CAPTCHA: {str(e)}")
            return False
    
    def _parse_case_results(self, driver, court_name):
        """Parse case results from the webpage"""
        try:
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            # Extract case information
            case_data = {
                'cnr_number': self._extract_text(soup, ['cnr', 'case number registry']),
                'case_title': self._extract_text(soup, ['case title', 'title']),
                'petitioner': self._extract_text(soup, ['petitioner', 'plaintiff', 'complainant']),
                'respondent': self._extract_text(soup, ['respondent', 'defendant', 'accused']),
                'filing_date': self._extract_date(soup, ['filing date', 'date of filing']),
                'next_hearing': self._extract_date(soup, ['next hearing', 'next date', 'hearing date']),
                'status': self._extract_text(soup, ['status', 'case status']),
                'judge_name': self._extract_text(soup, ['judge', 'presiding officer']),
                'orders': self._extract_orders(soup)
            }
            
            # Clean up the data
            case_data = {k: v for k, v in case_data.items() if v}
            
            if not case_data.get('case_title') and not case_data.get('petitioner'):
                return {
                    'status': 'not_found',
                    'message': 'Case not found or no data available'
                }
            
            return {
                'status': 'success',
                'data': case_data
            }
            
        except Exception as e:
            logger.error(f"Error parsing case results: {str(e)}")
            return {
                'status': 'error',
                'message': 'Error parsing case information'
            }
    
    def _extract_text(self, soup, keywords):
        """Extract text based on keywords"""
        for keyword in keywords:
            # Look for table cells containing the keyword
            cells = soup.find_all(['td', 'th', 'div', 'span'], 
                                string=lambda text: text and keyword.lower() in text.lower())
            for cell in cells:
                # Get the next sibling or parent's next sibling
                next_cell = cell.find_next_sibling() or cell.parent.find_next_sibling()
                if next_cell:
                    text = next_cell.get_text(strip=True)
                    if text and text != ':':
                        return text
        return None
    
    def _extract_date(self, soup, keywords):
        """Extract and format date"""
        date_text = self._extract_text(soup, keywords)
        if date_text:
            try:
                # Try different date formats
                for fmt in ['%d-%m-%Y', '%d/%m/%Y', '%Y-%m-%d', '%d.%m.%Y']:
                    try:
                        date_obj = datetime.strptime(date_text, fmt)
                        return date_obj.strftime('%Y-%m-%d')
                    except ValueError:
                        continue
            except:
                pass
        return None
    
    def _extract_orders(self, soup):
        """Extract order/judgment information"""
        orders = []
        
        # Look for PDF links or order information
        pdf_links = soup.find_all('a', href=lambda href: href and '.pdf' in href.lower())
        
        for link in pdf_links:
            order_text = link.get_text(strip=True)
            if order_text:
                order = {
                    'type': self._classify_order_type(order_text),
                    'pdf_url': urljoin(self.base_url, link.get('href')),
                    'date': self._extract_order_date(link)
                }
                orders.append(order)
        
        return orders[:5]  # Limit to 5 most recent orders
    
    def _classify_order_type(self, text):
        """Classify order type based on text"""
        text_lower = text.lower()
        if 'judgment' in text_lower or 'judgement' in text_lower:
            return 'Judgment'
        elif 'interim' in text_lower:
            return 'Interim Order'
        elif 'final' in text_lower:
            return 'Final Order'
        else:
            return 'Order'
    
    def _extract_order_date(self, link_element):
        """Extract date from order link or surrounding text"""
        # Look for date patterns in the link text or nearby elements
        text = link_element.get_text()
        parent = link_element.parent
        
        if parent:
            text += ' ' + parent.get_text()
        
        # Simple date extraction (can be improved)
        import re
        date_pattern = r'\d{1,2}[-/\.]\d{1,2}[-/\.]\d{4}'
        match = re.search(date_pattern, text)
        
        if match:
            date_str = match.group()
            try:
                # Try different formats
                for fmt in ['%d-%m-%Y', '%d/%m/%Y', '%d.%m.%Y']:
                    try:
                        date_obj = datetime.strptime(date_str, fmt)
                        return date_obj.strftime('%Y-%m-%d')
                    except ValueError:
                        continue
            except:
                pass
        
        return None
    
    def download_pdf(self, pdf_url, order_id):
        """Download PDF file from court website"""
        try:
            # Create download directory
            download_dir = os.getenv('PDF_STORAGE_PATH', 'downloads/pdfs/')
            os.makedirs(download_dir, exist_ok=True)
            
            # Generate filename
            filename = f"order_{order_id}_{int(time.time())}.pdf"
            filepath = os.path.join(download_dir, filename)
            
            # Download the PDF
            response = self.session.get(pdf_url, timeout=self.timeout, stream=True)
            response.raise_for_status()
            
            # Check content type
            content_type = response.headers.get('content-type', '').lower()
            if 'pdf' not in content_type:
                logger.warning(f"Downloaded file may not be PDF: {content_type}")
            
            # Save the file
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Check file size
            file_size = os.path.getsize(filepath)
            max_size = int(os.getenv('MAX_PDF_SIZE_MB', '50')) * 1024 * 1024
            
            if file_size > max_size:
                os.remove(filepath)
                logger.error(f"PDF file too large: {file_size} bytes")
                return None
            
            logger.info(f"PDF downloaded successfully: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error downloading PDF: {str(e)}")
            return None