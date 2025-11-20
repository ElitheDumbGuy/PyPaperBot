"""
Unit tests for the hybrid Sci-Hub client.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import extractors.scihub as scihub_client

class TestSciHubClient(unittest.TestCase):
    """Test cases for SciHubClient class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.client = scihub_client.SciHubClient(
            scihub_url="https://sci-hub.st",
            use_selenium=False,
            headless=True
        )
        self.mirror_config = {"url": "https://sci-hub.st", "method": "GET"}
    
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
    
    @patch('extractors.scihub.requests.Session.get')
    def test_download_via_http_success(self, mock_get):
        """Test successful HTTP download."""
        # Mock successful PDF download (first HTML, then PDF)
        
        # 1. HTML Page response
        mock_html = Mock()
        mock_html.status_code = 200
        mock_html.headers = {'content-type': 'text/html'}
        mock_html.content = b'<html><div id="article"><iframe src="https://sci-hub.st/downloads/paper.pdf"></iframe></div></html>'
        mock_html.url = 'https://sci-hub.st/10.1038/171737a0'

        # 2. PDF File response
        mock_pdf = Mock()
        mock_pdf.status_code = 200
        mock_pdf.headers = {'content-type': 'application/pdf'}
        mock_pdf.content = b'%PDF-1.4\nTest PDF content'
        mock_pdf.url = 'https://sci-hub.st/downloads/paper.pdf'
        
        mock_get.side_effect = [mock_html, mock_pdf]

        # We also need to patch getSchiHubPDF_xpath because our mock HTML is simple
        with patch('extractors.scihub.getSchiHubPDF_xpath', return_value='https://sci-hub.st/downloads/paper.pdf'):
            pdf_content, source_url, error = self.client._download_via_http("10.1038/171737a0", self.mirror_config, is_doi=True)
        
        self.assertIsNotNone(pdf_content)
        self.assertEqual(pdf_content, b'%PDF-1.4\nTest PDF content')
        self.assertIsNone(error)
    
    @patch('extractors.scihub.requests.Session.get')
    def test_download_via_http_error_page(self, mock_get):
        """Test HTTP download with error page."""
        # Mock error page response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'content-type': 'text/html'}
        mock_response.content = b"<html><body>Alas, the following paper is not yet available in my database</body></html>"
        mock_get.return_value = mock_response
        
        pdf_content, source_url, error = self.client._download_via_http("10.1002/ijop.70027", self.mirror_config, is_doi=True)
        
        self.assertIsNone(pdf_content)
        self.assertEqual(error, 'not_available')
    
    def test_close(self):
        """Test client cleanup."""
        # Test with no driver
        self.client.close()
        self.assertIsNone(self.client.selenium_driver)
        
        # Test with mock driver
        mock_driver = Mock()
        self.client.selenium_driver = mock_driver
        self.client.close()
        # Mock doesn't strictly reset attribute, but we check call
        mock_driver.quit.assert_called_once()

if __name__ == '__main__':
    unittest.main()
