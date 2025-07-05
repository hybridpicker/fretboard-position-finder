#!/usr/bin/env python3
"""
Fretboard Position Finder Setup Script
Works with Python 3.12 - No Conda required
Compatible with AlmaLinux 9 and CentOS production environment
"""

import os
import sys
import subprocess
import venv
from pathlib import Path

def run_command(command, check=True, shell=False):
    """Run command and handle errors"""
    print(f"Running: {command}")
    try:
        if shell:
            result = subprocess.run(command, shell=True, check=check, capture_output=True, text=True)
        else:
            result = subprocess.run(command.split(), check=check, capture_output=True, text=True)
        
        if result.stdout:
            print(result.stdout)
        if result.stderr and result.returncode != 0:
            print(f"Error: {result.stderr}")
        return result
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {e}")
        if not check:
            return e
        sys.exit(1)

def create_virtual_env():
    """Create Python virtual environment"""
    venv_path = Path('venv')
    
    if venv_path.exists():
        print("✓ Virtual environment already exists")
        return
    
    print("Creating Python virtual environment...")
    venv.create('venv', with_pip=True)
    print("✓ Virtual environment created")

def activate_venv_and_get_python():
    """Get the path to Python in virtual environment"""
    if os.name == 'nt':  # Windows
        return 'venv/Scripts/python.exe'
    else:  # Unix/Linux/macOS
        return 'venv/bin/python'

def create_local_settings():
    """Create local_settings.py for AlmaLinux production"""
    settings_content = '''import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent

# Development/Production toggle
DEBUG = True  # Set to False in production
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0', '*']

# Database configuration (SQLite for dev, PostgreSQL for production)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Production database (uncomment for production)
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'fretboard_db',
#         'USER': 'fretboard_user',
#         'PASSWORD': 'your_password',
#         'HOST': 'localhost',
#         'PORT': '5432',
#     }
# }

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Security
SECRET_KEY = 'dev-key-change-in-production-with-long-random-string'

# AlmaLinux/CentOS specific settings
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'django.log'),
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
'''
    
    if not os.path.exists('local_settings.py'):
        print("Creating local_settings.py...")
        with open('local_settings.py', 'w') as f:
            f.write(settings_content)
        print("✓ local_settings.py created")
    else:
        print("✓ local_settings.py already exists")

def install_requirements(python_exe):
    """Install Python requirements"""
    print("Installing Python dependencies...")
    if os.path.exists('requirements.txt'):
        run_command(f"{python_exe} -m pip install --upgrade pip")
        run_command(f"{python_exe} -m pip install -r requirements.txt")
        print("✓ Requirements installed")
    else:
        print("⚠️  requirements.txt not found")

def setup_database(python_exe):
    """Setup Django database"""
    print("Setting up database...")
    
    # Make migrations
    run_command(f"{python_exe} manage.py makemigrations")
    run_command(f"{python_exe} manage.py makemigrations positionfinder")
    
    # Apply migrations
    run_command(f"{python_exe} manage.py migrate")
    print("✓ Database migrations completed")

def load_fixtures(python_exe):
    """Load fixture data in correct order"""
    print("Loading fixtures...")
    
    fixture_files = [
        'fixtures/notes_data_clean.json',
        'fixtures/fretboard_data_clean.json',
        'fixtures/chord_data_clean.json',
        'positionfinder/fixtures/databasedump.json'
    ]
    
    loaded_any = False
    for fixture in fixture_files:
        if os.path.exists(fixture):
            try:
                run_command(f"{python_exe} manage.py loaddata {fixture}")
                print(f"✓ Loaded {fixture}")
                loaded_any = True
            except:
                print(f"⚠️  Failed to load {fixture}")
        else:
            print(f"⚠️  Fixture not found: {fixture}")
    
    if not loaded_any:
        print("⚠️  No fixtures were loaded successfully")

def collect_static(python_exe):
    """Collect static files"""
    print("Collecting static files...")
    run_command(f"{python_exe} manage.py collectstatic --noinput")
    print("✓ Static files collected")

def create_superuser(python_exe):
    """Optionally create superuser"""
    response = input("Create superuser? (y/N): ").lower()
    if response in ['y', 'yes']:
        run_command(f"{python_exe} manage.py createsuperuser", check=False)

def start_server(python_exe):
    """Start development server"""
    print("\n" + "="*50)
    print("🚀 Starting development server on port 8080...")
    print("Access your application at: http://localhost:8080")
    print("Press Ctrl+C to stop the server")
    print("="*50 + "\n")
    
    try:
        subprocess.run([python_exe, "manage.py", "runserver", "0.0.0.0:8080"])
    except KeyboardInterrupt:
        print("\n\n✓ Server stopped")

def create_activation_script():
    """Create activation script for easy use"""
    script_content = '''#!/bin/bash
# Fretboard Project Activation Script

cd "$(dirname "$0")"
source venv/bin/activate
echo "🎸 Fretboard environment activated!"
echo "Python: $(which python)"
echo "Django version: $(python -c 'import django; print(django.get_version())')"
echo ""
echo "To start server: python manage.py runserver 0.0.0.0:8080"
echo "To deactivate: deactivate"
'''
    
    with open('activate_fretboard.sh', 'w') as f:
        f.write(script_content)
    
    os.chmod('activate_fretboard.sh', 0o755)
    print("✓ Created activation script: activate_fretboard.sh")

def main():
    """Main setup function"""
    print("🎸 Fretboard Position Finder Setup")
    print("Using Python 3.12 with Virtual Environment")
    print("Compatible with AlmaLinux 9 / CentOS Production")
    print("="*50)
    
    # Change to project directory
    project_path = Path("/Users/lukasschonsgibl/Coding/Django/fretboard-position-finder")
    if project_path.exists():
        os.chdir(project_path)
        print(f"✓ Changed to project directory: {project_path}")
    
    # Create virtual environment
    create_virtual_env()
    
    # Get Python executable path
    python_exe = activate_venv_and_get_python()
    
    # Run setup steps
    create_local_settings()
    install_requirements(python_exe)
    setup_database(python_exe)
    load_fixtures(python_exe)
    collect_static(python_exe)
    create_activation_script()
    create_superuser(python_exe)
    
    # Ask if user wants to start server
    response = input("\nStart development server now? (Y/n): ").lower()
    if response not in ['n', 'no']:
        start_server(python_exe)
    else:
        print("\n✓ Setup complete!")
        print("To activate environment: source activate_fretboard.sh")
        print("To start server: python manage.py runserver 0.0.0.0:8080")

if __name__ == "__main__":
    main()
