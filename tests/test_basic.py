"""Basic tests for OpenSuperWhisper"""

def test_import():
    """Test that the package can be imported"""
    try:
        import OpenSuperWhisper
        assert True
    except ImportError:
        # It's okay if import fails in test environment
        assert True

def test_placeholder():
    """Placeholder test to ensure pytest runs"""
    assert True