"""
Script untuk menjalankan semua unit test
"""
import unittest
import sys
import os

# Tambahkan path parent untuk import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_all_tests():
    """Jalankan semua test suite"""
    
    # Discover semua test di folder tests
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Tambahkan test dari masing-masing module
    test_modules = [
        'test_validators',
        'test_entities',
        'test_repositories',
        'test_rental_service'
    ]
    
    for module in test_modules:
        try:
            tests = loader.loadTestsFromName(module)
            suite.addTests(tests)
            print(f"✓ Loaded: {module}")
        except Exception as e:
            print(f"✗ Error loading {module}: {e}")
    
    print("\n" + "=" * 70)
    print("RUNNING ALL TESTS")
    print("=" * 70 + "\n")
    
    # Jalankan test dengan verbosity tinggi
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Tests Run    : {result.testsRun}")
    print(f"Failures     : {len(result.failures)}")
    print(f"Errors       : {len(result.errors)}")
    print(f"Skipped      : {len(result.skipped)}")
    print(f"Success Rate : {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print("=" * 70)
    
    return result


if __name__ == '__main__':
    # Change ke direktori tests
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    result = run_all_tests()
    
    # Exit code berdasarkan hasil test
    sys.exit(0 if result.wasSuccessful() else 1)
