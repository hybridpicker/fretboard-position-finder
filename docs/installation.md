# Installation and Setup

This guide will help you set up the Fretboard Position Finder project for development.

## Prerequisites

- Python 3.6+
- PostgreSQL 10+
- Git

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/fretboard-position-finder.git
cd fretboard-position-finder
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Create PostgreSQL Databases

Create two databases for the 6-string and 8-string versions:

```sql
CREATE DATABASE "fretboard-devel";  -- For 6-string
CREATE DATABASE "fretboard";         -- For 8-string
```

### 5. Configure Database Settings

Create a `local_settings.py` file in the project root:

```python
# local_settings.py
SECRET_KEY = 'your-secret-key-here'

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        # For 6-string: 'NAME': 'fretboard-devel',
        # For 8-string: 'NAME': 'fretboard',
        'NAME': 'fretboard',  # Current setting
        'USER': 'your-db-user',
        'PASSWORD': 'your-db-password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 6. Apply Migrations

```bash
python manage.py migrate
```

### 7. Load Fixtures

```bash
python manage.py loaddata positionfinder/fixtures/databasedump.json
```

### 8. Run the Development Server

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` in your browser to access the application.

## Switching Between 6-String and 8-String Versions

To switch between the 6-string and 8-string versions, modify the database name in `local_settings.py`:

```python
# For 6-string:
'NAME': 'fretboard-devel',

# For 8-string:
'NAME': 'fretboard',
```

Then restart the development server.

## Production Deployment

For production deployment:

1. Set `DEBUG = False` in `local_settings.py`
2. Configure a production web server (Nginx, Apache)
3. Use Gunicorn or uWSGI as the WSGI server
4. Set up PostgreSQL with proper production settings
5. Collect static files:

```bash
python manage.py collectstatic
```

## Environment Variables

For improved security, consider using environment variables for sensitive information:

```python
import os

SECRET_KEY = os.environ.get('FRETBOARD_SECRET_KEY', 'default-dev-key')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('FRETBOARD_DB_NAME', 'fretboard'),
        'USER': os.environ.get('FRETBOARD_DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('FRETBOARD_DB_PASSWORD', ''),
        'HOST': os.environ.get('FRETBOARD_DB_HOST', 'localhost'),
        'PORT': os.environ.get('FRETBOARD_DB_PORT', '5432'),
    }
}
```
