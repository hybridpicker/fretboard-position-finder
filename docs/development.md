# Development Workflow

This document outlines the development workflow and best practices for contributing to the Fretboard Position Finder project.

## Development Environment Setup

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

### 4. Create Database Configuration

Create a `local_settings.py` file:

```python
# local_settings.py
SECRET_KEY = 'your-development-secret-key'

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'fretboard-devel',  # For 6-string development
        'USER': 'your-db-user',
        'PASSWORD': 'your-db-password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 5. Apply Migrations

```bash
python manage.py migrate
```

### 6. Load Initial Data

```bash
python manage.py loaddata positionfinder/fixtures/databasedump.json
```

### 7. Run Development Server

```bash
python manage.py runserver
```

## Version Control Workflow

### Branching Strategy

Use a feature branch workflow:

1. **main** - Stable production code
2. **develop** - Integration branch for features
3. **feature/feature-name** - Individual feature branches
4. **bugfix/bug-description** - Bug fix branches
5. **6-string** and **8-string** - Specific branches for string-specific features

### Creating a Feature Branch

```bash
git checkout develop
git pull
git checkout -b feature/your-feature-name
```

### Committing Changes

Make small, focused commits with descriptive messages:

```bash
git add .
git commit -m "Add Hungarian minor scale with positions"
```

### Pushing Changes

```bash
git push -u origin feature/your-feature-name
```

### Creating Pull Requests

1. Push your feature branch to the remote repository
2. Create a pull request to merge into the develop branch
3. Request code review
4. Address feedback
5. Merge after approval

## Working with 6-String and 8-String Versions

### Approach 1: Separate Databases

Maintain separate databases for each version:

1. 6-string database: `fretboard-devel`
2. 8-string database: `fretboard`

Switch between configurations by changing the database name in `local_settings.py`.

### Approach 2: Feature Flags

Use feature flags to control string configuration:

```python
# settings.py
EIGHT_STRING_ENABLED = True

# views.py
if settings.EIGHT_STRING_ENABLED:
    string_names = ['lowBString', 'ELowString', 'AString', 'dString', 
                    'gString', 'bString', 'eString', 'highAString']
else:
    string_names = ['ELowString', 'AString', 'dString', 
                    'gString', 'bString', 'eString']
```

### Approach 3: Dynamic Configuration

Query the database to determine the available strings:

```python
# Detect available strings from database content
available_strings = set()
for chord in ChordNotes.objects.all():
    if chord.first_note_string:
        available_strings.add(chord.first_note_string)
    # ... check other string fields

# Determine if 8-string is available
has_8string = 'lowBString' in available_strings or 'highAString' in available_strings
```

## Testing Strategy

### Test Types

1. **Unit Tests**: Test individual functions and methods
2. **Integration Tests**: Test interactions between components
3. **Functional Tests**: Test complete features from user perspective
4. **Compatibility Tests**: Test with different string configurations

### Setting Up Test Databases

Create test-specific settings:

```python
# test_settings.py
from .settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}
```

Run tests with these settings:

```bash
python manage.py test --settings=fretboard.test_settings
```

### Example Test Cases

```python
from django.test import TestCase
from positionfinder.models import Notes, NotesCategory, Root
from positionfinder.get_position_dict_scales import get_scale_position_dict

class ScalePositionTests(TestCase):
    def setUp(self):
        # Create test data
        self.category = NotesCategory.objects.create(id=1, category_name='Scales')
        self.root = Root.objects.create(id=1, name='C', pitch=0)
        self.scale = Notes.objects.create(
            category=self.category,
            note_name='Major',
            first_note=0,
            second_note=2,
            third_note=4,
            fourth_note=5,
            fifth_note=7,
            sixth_note=9,
            seventh_note=11
        )
        
    def test_scale_position_dict(self):
        # Test the position dictionary generation
        position_dict = get_scale_position_dict(
            'Major', 1, 0, 0, 'C'
        )
        self.assertIsNotNone(position_dict)
        # More assertions...
```

### Running Tests

```bash
# Run all tests
python manage.py test

# Run specific test class
python manage.py test positionfinder.tests.ScalePositionTests

# Run specific test method
python manage.py test positionfinder.tests.ScalePositionTests.test_scale_position_dict
```

## Database Schema Evolution

### Creating Migrations

When modifying models, create migrations:

```bash
python manage.py makemigrations positionfinder
```

### Applying Migrations

```bash
python manage.py migrate positionfinder
```

### Custom Migrations

For complex data migrations:

```python
# positionfinder/migrations/0010_custom_migration.py
from django.db import migrations

def migrate_data_forward(apps, schema_editor):
    # Get historical models
    Notes = apps.get_model("positionfinder", "Notes")
    NotesCategory = apps.get_model("positionfinder", "NotesCategory")
    
    # Perform data migration
    scales_category = NotesCategory.objects.get(id=1)
    Notes.objects.create(
        category=scales_category,
        note_name='Phrygian Dominant',
        first_note=0,
        second_note=1,
        third_note=4,
        fourth_note=5,
        fifth_note=7,
        sixth_note=8,
        seventh_note=10
    )

def migrate_data_backward(apps, schema_editor):
    # Reverse the data migration
    Notes = apps.get_model("positionfinder", "Notes")
    Notes.objects.filter(note_name='Phrygian Dominant').delete()

class Migration(migrations.Migration):
    dependencies = [
        ('positionfinder', '0009_previous_migration'),
    ]
    
    operations = [
        migrations.RunPython(migrate_data_forward, migrate_data_backward),
    ]
```

## Performance Optimization

### Database Optimization

1. **Indexing**: Add indexes to frequently queried fields
   ```python
   class Meta:
       indexes = [
           models.Index(fields=['category', 'note_name']),
       ]
   ```

2. **Query Optimization**: Use `select_related` and `prefetch_related`
   ```python
   chords = ChordNotes.objects.select_related('category').all()
   ```

3. **Batch Processing**: Process data in batches
   ```python
   for i in range(0, len(items), 100):
       batch = items[i:i+100]
       process_batch(batch)
   ```

### Frontend Optimization

1. **Minify Assets**: Compress CSS and JavaScript
2. **Lazy Loading**: Only load required data
3. **Caching**: Cache fretboard positions

## Documentation Standards

### Code Documentation

Use docstrings for functions and classes:

```python
def get_scale_position_dict(scale_name, root_id, root_pitch, tonal_root, root_name):
    """
    Generate a dictionary of scale positions.
    
    Args:
        scale_name (str): Name of the scale
        root_id (int): ID of the root note
        root_pitch (int): Pitch of the root note (0-11)
        tonal_root (int): Tonal root offset
        root_name (str): Name of the root note
        
    Returns:
        dict: Dictionary containing scale positions
    """
    # Function body...
```

### Commit Messages

Use clear, descriptive commit messages:

```
Add Hungarian minor scale with positions

- Add scale definition with intervals [0, 2, 3, 6, 7, 8, 11]
- Create 5 positions covering the fretboard
- Add documentation for the scale
```

## Deployment Process

### Staging Deployment

1. Merge develop branch to staging
2. Deploy to staging server
3. Run tests and verify functionality
4. Get stakeholder approval

### Production Deployment

1. Merge staging branch to main
2. Tag the release (e.g., v1.2.0)
3. Deploy to production server
4. Verify functionality
5. Monitor for issues

### Deployment Checklist

Before deploying:
- Run full test suite
- Check for database migrations
- Set DEBUG = False
- Configure production database settings
- Collect static files
- Check for security issues

## Continuous Integration

### Setting Up CI/CD

Use GitHub Actions for CI/CD:

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [ develop, main ]
  pull_request:
    branches: [ develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:12
        env:
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: github_actions
        ports:
          - 5432:5432
        options: --health-cmd pg_isready --health-interval 10s --health-timeout 5s --health-retries 5
    
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.8
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run tests
      env:
        DATABASE_URL: postgres://postgres:postgres@localhost:5432/github_actions
      run: |
        python manage.py test
```

## Coding Standards

### Python Style Guide

Follow PEP 8 guidelines:
- Use 4 spaces for indentation
- Keep lines under 79 characters
- Use clear, descriptive variable names
- Use docstrings for documentation

### JavaScript Style Guide

Follow Airbnb JavaScript Style Guide:
- Use semicolons
- Use camelCase for variables and functions
- Use PascalCase for classes and constructors
- Comment complex code sections

## Contribution Guidelines

### Contributing Process

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write tests
5. Update documentation
6. Submit a pull request

### Code Review Process

All code changes should go through review:
1. Pull request is submitted
2. Maintainer reviews the code
3. Address feedback
4. Approval and merge

### Reporting Issues

When reporting issues, include:
1. Clear description of the issue
2. Steps to reproduce
3. Expected vs. actual behavior
4. Screenshots if applicable
5. Environment details
