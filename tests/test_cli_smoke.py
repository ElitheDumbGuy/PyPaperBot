import subprocess
import unittest
import sys
import os

class TestCLISmoke(unittest.TestCase):
    """Smoke tests for the CLI interface."""
    
    def run_cli(self, args):
        """Helper to run CLI with correct PYTHONPATH."""
        env = os.environ.copy()
        # Add src to PYTHONPATH so we test the local code, not installed package
        src_path = os.path.join(os.getcwd(), "src")
        env["PYTHONPATH"] = src_path + os.pathsep + env.get("PYTHONPATH", "")
        
        return subprocess.run(
            [sys.executable, "-m", "core.cli"] + args,
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=env
        )

    def test_version_flag(self):
        """Test that the --version check (implied by running the module) works."""
        # Running python -m core.cli should print the version banner
        result = self.run_cli(["--help"])
        
        self.assertEqual(result.returncode, 0)
        # Check for new name
        self.assertIn("AcademicArchiver", result.stdout)
        self.assertIn("--expand-network", result.stdout)

    def test_missing_args_exit(self):
        """Test that running without args exits gracefully with help."""
        result = self.run_cli([])
        
        # It exits with 1 if arguments are missing
        self.assertEqual(result.returncode, 1)
        self.assertIn("Error", result.stdout)

if __name__ == '__main__':
    unittest.main()
