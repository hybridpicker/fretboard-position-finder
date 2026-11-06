"""Settings for the test suite and CI.

Does not require ``local_settings.py``. Connection details come from the
standard libpq environment variables (PGHOST, PGPORT, PGUSER, PGPASSWORD);
Django creates and drops ``test_<NAME>`` itself, so the development database
is never touched.
"""

import os

from fretboard.settings import *  # noqa: F403

SECRET_KEY = "test-only-not-a-secret"  # noqa: S105
DEBUG = False
ALLOWED_HOSTS = ["testserver", "localhost", "127.0.0.1", "[::1]"]
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("PGDATABASE", "fretboard_test"),
    }
}
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
