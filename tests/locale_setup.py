# tests/locale_setup.py
from django.utils import translation
import pytest
from functools import wraps

# List of supported languages in the application
SUPPORTED_LANGUAGES = [
    'en',  # English (default)
    'de',  # German
    'es',  # Spanish
    'fr',  # French
    # Add other supported languages as needed
]

class LocaleTestMixin:
    """
    Mixin for tests that need to check multiple locales.
    Provides helpers for setting and resetting the current locale.
    """
    
    def set_language(self, language_code):
        """
        Set the current language for testing.
        
        Args:
            language_code: The language code to set (e.g., 'en', 'de', 'fr')
        
        Returns:
            boolean: True if language was set, False if not supported
        """
        if language_code in SUPPORTED_LANGUAGES:
            translation.activate(language_code)
            return True
        return False
    
    def reset_language(self):
        """Reset to default language (English)"""
        translation.activate('en')
    
    def run_with_locale(self, language_code):
        """
        Decorator-like method to run a test with a specific locale.
        
        Usage:
            with self.run_with_locale('de'):
                # Test code with German locale
        """
        class LocaleContext:
            def __init__(self, test_instance, lang_code):
                self.test_instance = test_instance
                self.lang_code = lang_code
                self.previous_language = translation.get_language()
                
            def __enter__(self):
                self.test_instance.set_language(self.lang_code)
                return self
                
            def __exit__(self, exc_type, exc_val, exc_tb):
                translation.activate(self.previous_language)
        
        return LocaleContext(self, language_code)
    
    def assert_translated_content(self, response, expected_terms):
        """
        Assert that response contains expected translated terms.
        
        Args:
            response: Django test client response
            expected_terms: List of terms that should be present in the translated content
        """
        content = response.content.decode('utf-8')
        for term in expected_terms:
            assert term in content, f"Term '{term}' not found in translated content"


def with_multiple_locales(*languages):
    """
    Decorator to run a test with multiple languages.
    For each language, creates a new test that runs with that language activated.
    
    Usage:
        @with_multiple_locales('en', 'de', 'fr')
        def test_search_page_title(self, language):
            # language will be 'en', 'de', or 'fr' in different test runs
            ...
    """
    def decorator(test_func):
        @wraps(test_func)
        def wrapper(self, *args, **kwargs):
            current_language = translation.get_language()
            try:
                for lang in languages:
                    translation.activate(lang)
                    # Run the test with the current language
                    kwargs['language'] = lang
                    test_func(self, *args, **kwargs)
            finally:
                # Restore original language
                translation.activate(current_language)
        return wrapper
    return decorator


@pytest.fixture
def set_language(request):
    """
    Pytest fixture to set language for a test.
    
    Usage:
        def test_something(set_language):
            set_language('de')
            # Test with German language
    """
    original_language = translation.get_language()
    
    def _set_language(language_code):
        if language_code in SUPPORTED_LANGUAGES:
            translation.activate(language_code)
            return True
        return False
    
    yield _set_language
    
    # Reset language after test
    translation.activate(original_language)


@pytest.fixture
def multi_language_client(client):
    """
    Returns a Django test client with language setting methods.
    
    Usage:
        def test_something(multi_language_client):
            multi_language_client.set_language('de')
            response = multi_language_client.get('/some-url/')
            # Response will be in German
    """
    original_language = translation.get_language()
    
    def set_language(language_code):
        if language_code in SUPPORTED_LANGUAGES:
            translation.activate(language_code)
            return True
        return False
    
    client.set_language = set_language
    
    yield client
    
    # Reset language after test
    translation.activate(original_language)