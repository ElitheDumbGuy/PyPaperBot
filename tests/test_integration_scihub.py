import unittest
import os
import requests
from extractors.scihub import SciHubClient

class TestSciHubIntegration(unittest.TestCase):
    """
    Integration tests for Sci-Hub client.
    WARNING: These tests make actual network requests.
    """
    
    def setUp(self):
        # Check if integration tests are enabled via env var
        if os.environ.get('RUN_INTEGRATION_TESTS') != 'true':
            self.skipTest("Skipping integration tests. Set RUN_INTEGRATION_TESTS=true to run.")
        
        self.client = SciHubClient(use_selenium=False, headless=True)
        # Known open access DOI for testing (won't likely be taken down or change)
        self.test_doi = "10.1038/171737a0" # DNA structure paper (Watson/Crick)

    def test_mirror_connectivity(self):
        """Test connectivity to configured mirrors."""
        available = []
        for mirror in self.client.mirrors:
            try:
                response = requests.head(mirror['url'], timeout=5, verify=False)
                if response.status_code < 500:
                    available.append(mirror['url'])
            except Exception:
                pass
        
        if not available:
            self.fail("No Sci-Hub mirrors are currently reachable.")
        print(f"Reachable mirrors: {available}")

    def test_real_download(self):
        """Attempt to download a real paper."""
        try:
            pdf_content, source_url, mirror_url = self.client.download(self.test_doi)
            self.assertTrue(pdf_content.startswith(b'%PDF'), "Downloaded content is not a PDF")
            self.assertTrue(len(pdf_content) > 1000, "Downloaded PDF is suspiciously small")
            print(f"Successfully downloaded {self.test_doi} from {mirror_url}")
        except Exception as e:
            self.fail(f"Integration download failed: {e}")

    def tearDown(self):
        self.client.close()

if __name__ == '__main__':
    unittest.main()

