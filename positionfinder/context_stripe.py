from django.conf import settings

def stripe_url_context(request):
    """
    Adds STRIPE_DONATE_URL to the context for all templates.
    """
    return {
        'STRIPE_DONATE_URL': getattr(settings, 'STRIPE_DONATE_URL', None)
    }
