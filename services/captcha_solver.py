"""
CAPTCHA Solver Service
Handles CAPTCHA solving using 2captcha service and fallback methods
"""

import os
import time
import logging
import requests
from PIL import Image
import io
import base64

logger = logging.getLogger(__name__)

class CaptchaSolver:
    """CAPTCHA solving service"""
    
    def __init__(self):
        self.api_key = os.getenv('TWOCAPTCHA_API_KEY')
        self.base_url = 'http://2captcha.com'
        self.timeout = 120  # Maximum time to wait for CAPTCHA solution
        self.retry_limit = int(os.getenv('CAPTCHA_RETRY_LIMIT', '3'))
        
    def solve_captcha(self, captcha_url_or_image):
        """
        Solve CAPTCHA using available methods
        
        Args:
            captcha_url_or_image: URL to CAPTCHA image or image data
            
        Returns:
            str: Solved CAPTCHA text or None if failed
        """
        if not self.api_key:
            logger.warning("No 2captcha API key provided, using fallback methods")
            return self._fallback_solve(captcha_url_or_image)
        
        try:
            return self._solve_with_2captcha(captcha_url_or_image)
        except Exception as e:
            logger.error(f"2captcha solving failed: {str(e)}")
            return self._fallback_solve(captcha_url_or_image)
    
    def _solve_with_2captcha(self, captcha_url_or_image):
        """Solve CAPTCHA using 2captcha service"""
        try:
            # Get image data
            if captcha_url_or_image.startswith('http'):
                response = requests.get(captcha_url_or_image, timeout=30)
                response.raise_for_status()
                image_data = response.content
            else:
                # Assume it's base64 encoded image
                image_data = base64.b64decode(captcha_url_or_image)
            
            # Submit CAPTCHA to 2captcha
            submit_url = f"{self.base_url}/in.php"
            files = {'file': ('captcha.png', image_data, 'image/png')}
            data = {
                'key': self.api_key,
                'method': 'post',
                'json': 1
            }
            
            response = requests.post(submit_url, files=files, data=data, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            if result['status'] != 1:
                raise Exception(f"2captcha submission failed: {result.get('error_text', 'Unknown error')}")
            
            captcha_id = result['request']
            logger.info(f"CAPTCHA submitted to 2captcha with ID: {captcha_id}")
            
            # Wait for solution
            return self._get_2captcha_result(captcha_id)
            
        except Exception as e:
            logger.error(f"Error in 2captcha solving: {str(e)}")
            raise
    
    def _get_2captcha_result(self, captcha_id):
        """Get CAPTCHA solution from 2captcha"""
        result_url = f"{self.base_url}/res.php"
        params = {
            'key': self.api_key,
            'action': 'get',
            'id': captcha_id,
            'json': 1
        }
        
        start_time = time.time()
        while time.time() - start_time < self.timeout:
            try:
                response = requests.get(result_url, params=params, timeout=30)
                response.raise_for_status()
                result = response.json()
                
                if result['status'] == 1:
                    captcha_text = result['request']
                    logger.info(f"CAPTCHA solved: {captcha_text}")
                    return captcha_text
                elif result['error_text'] == 'CAPCHA_NOT_READY':
                    time.sleep(5)  # Wait before next attempt
                    continue
                else:
                    raise Exception(f"2captcha error: {result.get('error_text', 'Unknown error')}")
                    
            except requests.RequestException as e:
                logger.error(f"Error getting 2captcha result: {str(e)}")
                time.sleep(5)
                continue
        
        raise Exception("Timeout waiting for CAPTCHA solution")
    
    def _fallback_solve(self, captcha_url_or_image):
        """
        Fallback CAPTCHA solving methods
        This is a placeholder for alternative methods like:
        - Local OCR
        - Manual input prompt
        - Other CAPTCHA services
        """
        logger.info("Using fallback CAPTCHA solving method")
        
        try:
            # Try simple OCR for basic CAPTCHAs
            return self._simple_ocr_solve(captcha_url_or_image)
        except Exception as e:
            logger.error(f"Fallback CAPTCHA solving failed: {str(e)}")
            return None
    
    def _simple_ocr_solve(self, captcha_url_or_image):
        """
        Simple OCR-based CAPTCHA solving for basic text CAPTCHAs
        This is a basic implementation and may not work for complex CAPTCHAs
        """
        try:
            # This would require additional OCR libraries like pytesseract
            # For now, return None to indicate failure
            logger.warning("Simple OCR solving not implemented")
            return None
            
        except Exception as e:
            logger.error(f"OCR solving error: {str(e)}")
            return None
    
    def manual_captcha_prompt(self, captcha_url):
        """
        Fallback method to prompt user for manual CAPTCHA entry
        This would be used in development/testing scenarios
        """
        try:
            print(f"\nPlease solve the CAPTCHA manually:")
            print(f"CAPTCHA URL: {captcha_url}")
            print("Open the URL in your browser and enter the CAPTCHA text below:")
            
            captcha_text = input("Enter CAPTCHA text: ").strip()
            
            if captcha_text:
                logger.info("Manual CAPTCHA entry received")
                return captcha_text
            else:
                logger.warning("No CAPTCHA text entered")
                return None
                
        except Exception as e:
            logger.error(f"Manual CAPTCHA prompt error: {str(e)}")
            return None
    
    def validate_captcha_text(self, text):
        """
        Validate CAPTCHA text format
        
        Args:
            text (str): CAPTCHA text to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        if not text or not isinstance(text, str):
            return False
        
        # Remove whitespace
        text = text.strip()
        
        # Basic validation - should be 4-8 characters
        if len(text) < 3 or len(text) > 10:
            return False
        
        # Should contain only alphanumeric characters
        if not text.isalnum():
            return False
        
        return True
    
    def get_captcha_image_info(self, captcha_url):
        """
        Get information about CAPTCHA image
        
        Args:
            captcha_url (str): URL to CAPTCHA image
            
        Returns:
            dict: Image information
        """
        try:
            response = requests.get(captcha_url, timeout=30)
            response.raise_for_status()
            
            # Load image
            image = Image.open(io.BytesIO(response.content))
            
            return {
                'size': image.size,
                'format': image.format,
                'mode': image.mode,
                'file_size': len(response.content)
            }
            
        except Exception as e:
            logger.error(f"Error getting CAPTCHA image info: {str(e)}")
            return None