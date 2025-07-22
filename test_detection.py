#!/usr/bin/env python3
"""
Comprehensive test script for uvhow detection logic.
Can be run locally or in CI to verify detection accuracy.
"""

import sys
import unittest.mock
from pathlib import Path

# Add src to path to import uvhow
sys.path.insert(0, 'src')

try:
    from uvhow import detect_uv_installation, is_uv_installed_via_pip
except ImportError:
    print("❌ Could not import uvhow. Make sure you're running from the project root.")
    sys.exit(1)


def test_detection_logic():
    """Test the detection logic with various path and pip combinations."""
    test_cases = [
        # (path, is_pip_installed, expected_method)
        ('/opt/homebrew/Cellar/uv/0.7.21/bin/uv', False, 'Homebrew'),
        ('/opt/homebrew/bin/uv', False, 'Homebrew'),
        ('/usr/local/Cellar/uv/0.7.21/bin/uv', False, 'Homebrew'),
        
        ('/home/user/.local/bin/uv', True, 'pip (user)'),
        ('/home/user/.local/bin/uv', False, 'Standalone installer'),
        ('/Users/user/.local/bin/uv', True, 'pip (user)'),
        ('/Users/user/.local/bin/uv', False, 'Standalone installer'),
        
        ('/usr/local/bin/uv', True, 'pip (system)'),
        ('/usr/bin/uv', True, 'pip (system)'),
        ('/usr/local/bin/uv', False, 'Unknown'),
        
        ('/home/user/.cargo/bin/uv', False, 'Cargo'),
        ('/Users/user/.cargo/bin/uv', False, 'Cargo'),
        
        ('/home/user/.local/share/pipx/venvs/uv/bin/uv', False, 'pipx'),
        ('/Users/user/.local/share/pipx/venvs/uv/bin/uv', False, 'pipx'),
        ('/opt/pipx/venvs/uv/bin/uv', False, 'pipx'),
        
        ('/project/.venv/bin/uv', False, 'pip (virtual environment)'),
        ('/home/user/project/venv/bin/uv', False, 'pip (virtual environment)'),
        ('/workspace/.env/bin/uv', False, 'pip (virtual environment)'),
        
        ('/opt/local/bin/uv', True, 'pip (user)'),
        ('/some/random/path/bin/uv', True, 'pip (user)'),
        ('/some/random/path/bin/uv', False, 'Unknown'),
    ]
    
    print('🧪 Testing detection logic with various scenarios...')
    print()
    
    failed = 0
    passed = 0
    
    for path, mock_pip_installed, expected in test_cases:
        with unittest.mock.patch('shutil.which', return_value=path):
            with unittest.mock.patch('uvhow.get_uv_version', return_value='uv 0.7.21'):
                with unittest.mock.patch('uvhow.is_uv_installed_via_pip', return_value=mock_pip_installed):
                    install = detect_uv_installation()
                    
                    if install and install.method == expected:
                        print(f'✅ {path} (pip={mock_pip_installed}) -> {install.method}')
                        passed += 1
                    else:
                        actual = install.method if install else 'None'
                        print(f'❌ {path} (pip={mock_pip_installed}) -> {actual} (expected: {expected})')
                        failed += 1
    
    print()
    print(f'📊 Test Results: {passed} passed, {failed} failed')
    
    if failed > 0:
        print('❌ Some tests failed!')
        return False
    else:
        print('✅ All detection tests passed!')
        return True


def test_pip_detection():
    """Test the pip detection functionality."""
    print('🔍 Testing pip detection function...')
    
    # This will test the actual pip detection in the current environment
    try:
        pip_detected = is_uv_installed_via_pip()
        print(f'📦 Current environment - uv installed via pip: {pip_detected}')
        
        # Try to determine if this result makes sense by checking if uv is available
        import shutil
        uv_path = shutil.which('uv')
        if uv_path:
            print(f'📍 UV found at: {uv_path}')
        else:
            print('📍 UV not found in PATH')
            
        return True
    except Exception as e:
        print(f'❌ Error testing pip detection: {e}')
        return False


def test_edge_cases():
    """Test edge cases and error conditions."""
    print('🔬 Testing edge cases...')
    
    test_cases = [
        # Edge cases that should return Unknown or specific behaviors
        ('/some/weird/path/uv', False, 'Unknown'),  # Not ending in /bin/uv
        ('/home/user/project/venv/somewhere/uv', False, 'Unknown'),  # venv but not in bin
    ]
    
    failed = 0
    passed = 0
    
    for path, mock_pip_installed, expected in test_cases:
        with unittest.mock.patch('shutil.which', return_value=path):
            with unittest.mock.patch('uvhow.get_uv_version', return_value='uv 0.7.21'):
                with unittest.mock.patch('uvhow.is_uv_installed_via_pip', return_value=mock_pip_installed):
                    install = detect_uv_installation()
                    
                    if install and install.method == expected:
                        print(f'✅ {path} -> {install.method}')
                        passed += 1
                    else:
                        actual = install.method if install else 'None'
                        print(f'❌ {path} -> {actual} (expected: {expected})')
                        failed += 1
    
    # Test when uv is not found
    print('Testing when uv is not installed...')
    with unittest.mock.patch('shutil.which', return_value=None):
        install = detect_uv_installation()
        if install is None:
            print('✅ Correctly returns None when uv not found')
            passed += 1
        else:
            print('❌ Should return None when uv not found')
            failed += 1
    
    print(f'📊 Edge case results: {passed} passed, {failed} failed')
    return failed == 0


def main():
    """Run all tests."""
    print('🚀 Starting uvhow detection tests...')
    print('=' * 50)
    
    tests = [
        ('Detection Logic', test_detection_logic),
        ('Pip Detection', test_pip_detection),
        ('Edge Cases', test_edge_cases),
    ]
    
    all_passed = True
    
    for test_name, test_func in tests:
        print(f'\\n📋 Running {test_name} tests...')
        print('-' * 30)
        
        try:
            result = test_func()
            if not result:
                all_passed = False
        except Exception as e:
            print(f'❌ {test_name} test failed with exception: {e}')
            all_passed = False
    
    print('\\n' + '=' * 50)
    
    if all_passed:
        print('🎉 All tests passed! uvhow detection is working correctly.')
        sys.exit(0)
    else:
        print('💥 Some tests failed. Please check the detection logic.')
        sys.exit(1)


if __name__ == '__main__':
    main()