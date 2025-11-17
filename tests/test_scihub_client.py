"""
Unit tests for the hybrid Sci-Hub client.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import PyPaperBot.scihub_client as scihub_client


class TestSciHubClient(unittest.TestCase):
    """Test cases for SciHubClient class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.client = scihub_client.SciHubClient(
            scihub_url="https://sci-hub.st",
            use_selenium=False,
            headless=True
        )
    
    def test_is_valid_pdf(self):
        """Test PDF validation."""
        # Valid PDF header
        valid_pdf = b'%PDF-1.4\n'
        self.assertTrue(self.client._is_valid_pdf(valid_pdf))
        
        # Invalid PDF (HTML)
        invalid_pdf = b'<html><body>Not a PDF</body></html>'
        self.assertFalse(self.client._is_valid_pdf(invalid_pdf))
        
        # Empty content
        self.assertFalse(self.client._is_valid_pdf(b''))
        self.assertFalse(self.client._is_valid_pdf(None))
    
    def test_is_error_page(self):
        """Test error page detection."""
        # Error page with "not yet available"
        error_html = "<html><body>Alas, the following paper is not yet available in my database</body></html>"
        self.assertTrue(self.client._is_error_page(error_html))
        
        # Error page with captcha
        captcha_html = "<html><body>Please complete the captcha</body></html>"
        self.assertTrue(self.client._is_error_page(captcha_html))
        
        # Valid HTML (no error indicators)
        valid_html = "<html><body><iframe src='pdf.pdf'></iframe></body></html>"
        self.assertFalse(self.client._is_error_page(valid_html))
        
        # None or non-string
        self.assertFalse(self.client._is_error_page(None))
        self.assertFalse(self.client._is_error_page(b'bytes'))
    
    @patch('PyPaperBot.scihub_client.requests.Session.get')
    def test_download_via_http_success(self, mock_get):
        """Test successful HTTP download."""
        # Mock successful PDF download
        mock_response = Mock()
        mock_response.headers = {'content-type': 'application/pdf'}
        mock_response.content = b'%PDF-1.4\nTest PDF content'
        mock_response.url = 'https://sci-hub.st/test.pdf'
        mock_get.return_value = mock_response
        
        pdf_content, source_url = self.client._download_via_http("10.1038/171737a0", is_doi=True)
        
        self.assertIsNotNone(pdf_content)
        self.assertEqual(pdf_content, b'%PDF-1.4\nTest PDF content')
        self.assertEqual(source_url, 'https://sci-hub.st/test.pdf')
    
    @patch('PyPaperBot.scihub_client.requests.Session.get')
    def test_download_via_http_error_page(self, mock_get):
        """Test HTTP download with error page."""
        # Mock error page response
        mock_response = Mock()
        mock_response.headers = {'content-type': 'text/html'}
        mock_response.text = "<html><body>Alas, the following paper is not yet available in my database</body></html>"
        mock_get.return_value = mock_response
        
        pdf_content, source_url = self.client._download_via_http("10.1002/ijop.70027", is_doi=True)
        
        self.assertIsNone(pdf_content)
        self.assertIsNone(source_url)
    
    def test_close(self):
        """Test client cleanup."""
        # Test with no driver
        self.client.close()
        self.assertIsNone(self.client.selenium_driver)
        
        # Test with mock driver
        mock_driver = Mock()
        self.client.selenium_driver = mock_driver
        self.client.close()
        mock_driver.quit.assert_called_once()
        self.assertIsNone(self.client.selenium_driver)


if __name__ == '__main__':
    unittest.main()

