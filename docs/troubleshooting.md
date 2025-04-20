# Troubleshooting Guide

This document provides solutions for common issues you might encounter when working with the Fretboard Position Finder application.

## Database Issues

### Issue: Database Connection Errors

**Symptoms:**
- "could not connect to server" errors
- Django reports database connection failures

**Solutions:**

1. **Check PostgreSQL service:**
   ```bash
   # Linux/Mac
   sudo service postgresql status
   
   # Windows
   sc query postgresql
   ```

2. **Verify database credentials:**
   - Check the database name, username, and password in `local_settings.py`
   - Ensure the user has proper permissions

3. **Test direct connection:**
   ```bash
   psql -U postgres -d fretboard
   ```

4. **Check database exists:**
   ```bash
   psql -U postgres -c "\l"
   ```

### Issue: Migration Errors

**Symptoms:**
- "table already exists" errors during migration
- "no such table" errors during operation

**Solutions:**

1. **Reset migrations (development only):**
   ```bash
   python manage.py migrate positionfinder zero
   python manage.py migrate positionfinder
   ```

2. **Fix inconsistent migration state:**
   ```bash
   python manage.py showmigrations
   # Find inconsistent migrations
   python manage.py migrate --fake positionfinder 0001_initial
   ```

3. **Create a clean database:**
   ```bash
   dropdb fretboard-devel
   createdb fretboard-devel
   python manage.py migrate
   python manage.py loaddata positionfinder/fixtures/databasedump.json
   ```

## Application Errors

### Issue: Application Not Starting

**Symptoms:**
- Server fails to start
- ImportError or ModuleNotFoundError

**Solutions:**

1. **Check for missing dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Verify local_settings.py exists:**
   - Create from template if missing

3. **Check for syntax errors:**
   ```bash
   python -m py_compile manage.py
   ```

4. **Django version compatibility:**
   - Ensure using compatible Django version (2.2+)

### Issue: 500 Server Error

**Symptoms:**
- "Internal Server Error" in browser
- 500 error in logs

**Solutions:**

1. **Check error logs:**
   - Django error traceback in console
   - Server error logs

2. **Enable DEBUG mode:**
   ```python
   # local_settings.py
   DEBUG = True
   ```

3. **Check for database issues:**
   - Missing tables
   - Incorrect model references

### Issue: 404 Not Found

**Symptoms:**
- "Page not found" errors
- Missing views or resources

**Solutions:**

1. **Check URL configuration:**
   - Verify URL patterns in `urls.py`

2. **Check view existence:**
   - Ensure view functions exist and are properly imported

3. **Verify templates:**
   - Check template paths and existence

## Position Display Issues

### Issue: Positions Not Displaying

**Symptoms:**
- Blank fretboard
- Missing note markers

**Solutions:**

1. **Check JavaScript console:**
   - Look for JavaScript errors

2. **Verify JSON data:**
   - Inspect network requests for JSON format issues

3. **Test with known working scale:**
   - Try Major scale in C as a baseline

4. **Check template rendering:**
   - Ensure template variables are correctly passed to template

### Issue: Incorrect Positions

**Symptoms:**
- Notes appear in wrong locations
- Inconsistent or unexpected patterns

**Solutions:**

1. **Verify scale/chord definition:**
   ```python
   # In Django shell
   from positionfinder.models import Notes
   scale = Notes.objects.get(note_name='Scale Name')
   print(scale.first_note, scale.second_note, scale.third_note)  # etc.
   ```

2. **Check position data:**
   ```python
   from positionfinder.models import NotesPosition
   positions = NotesPosition.objects.filter(notes_name__note_name='Scale Name')
   for pos in positions:
       print(pos.position_order, pos.first_note, pos.first_note_string)
   ```

3. **Validate string mapping:**
   - Ensure string assignments match intended strings

4. **Test with different root notes:**
   - Try multiple root notes to identify patterns in errors

### Issue: Missing Scales or Chords

**Symptoms:**
- Scale or chord doesn't appear in selection dropdowns
- Can't select specific musical elements

**Solutions:**

1. **Check database content:**
   ```python
   # In Django shell
   from positionfinder.models import Notes, NotesCategory
   scales = Notes.objects.filter(category__category_name='Scales')
   print([s.note_name for s in scales])
   ```

2. **Verify menu options:**
   ```python
   from positionfinder.views_helpers import get_menu_options
   options = get_menu_options()
   print(options['scales_options'])
   ```

3. **Check category assignments:**
   - Ensure items are assigned to correct categories

4. **Add missing content:**
   - Follow the instructions in [Adding Content](adding_content.md)

## 8-String Issues

### Issue: 8-String Content Not Showing

**Symptoms:**
- Additional strings aren't displayed
- 8-string specific content missing

**Solutions:**

1. **Verify database connection:**
   - Ensure connected to the 8-string database ('fretboard' not 'fretboard-devel')

2. **Check string references:**
   - Confirm data includes references to 'lowBString' and 'highAString'

3. **Inspect template context:**
   ```python
   # Add debug output to views
   print("String names:", string_names)
   ```

4. **Check for JavaScript issues:**
   - String count detection in frontend code

### Issue: String Range Issues

**Symptoms:**
- String ranges not available in selection
- Range selection causes display issues

**Solutions:**

1. **Check available ranges:**
   ```python
   # In Django shell
   from positionfinder.models_chords import ChordNotes
   ranges = ChordNotes.objects.values_list('range', flat=True).distinct()
   print(sorted(list(ranges)))
   ```

2. **Verify string range choices:**
   - Check `string_range_choices.py` for proper definitions

3. **Add missing ranges:**
   - Add needed range combinations to the database

4. **Fix range ordering:**
   - Ensure ranges have appropriate `range_ordering` values

## Performance Issues

### Issue: Slow Page Loads

**Symptoms:**
- Pages take a long time to load
- Browser shows "waiting for server" for extended periods

**Solutions:**

1. **Optimize database queries:**
   - Add indexes to frequently queried fields
   - Use `select_related` and `prefetch_related`

2. **Implement caching:**
   ```python
   from django.core.cache import cache
   
   # Try to get from cache first
   cache_key = f"scale_{root_id}_{notes_options_id}"
   position_json_data = cache.get(cache_key)
   if position_json_data is None:
       # Generate if not in cache
       position_json_data = get_scale_position_dict(...)
       # Store in cache for future requests
       cache.set(cache_key, position_json_data, 60*60)  # 1 hour cache
   ```

3. **Reduce template complexity:**
   - Simplify template logic
   - Use template fragments

4. **Profile slow views:**
   ```python
   import cProfile
   
   def profile_view(request):
       profiler = cProfile.Profile()
       profiler.enable()
       
       # Run the view
       response = original_view(request)
       
       profiler.disable()
       profiler.print_stats(sort='cumtime')
       
       return response
   ```

### Issue: High Memory Usage

**Symptoms:**
- Application consumes excessive memory
- Out of memory errors

**Solutions:**

1. **Optimize large data structures:**
   - Avoid keeping large objects in memory

2. **Use pagination:**
   - For large result sets, paginate the data

3. **Reduce JSON payload size:**
   - Only include necessary data
   - Consider compression

4. **Memory profiling:**
   ```bash
   pip install memory_profiler
   mprof run python manage.py runserver
   mprof plot
   ```

## Frontend Issues

### Issue: JavaScript Errors

**Symptoms:**
- Console shows JavaScript errors
- Interactive elements don't work

**Solutions:**

1. **Check browser console:**
   - Identify specific errors

2. **Verify script loading:**
   - Check network tab for failed script loads

3. **Test in different browsers:**
   - Check for browser compatibility issues

4. **Debug JSON data:**
   ```javascript
   console.log(JSON.parse(scaleData));
   ```

### Issue: Rendering Problems

**Symptoms:**
- Visual glitches
- Elements misaligned or missing

**Solutions:**

1. **Inspect DOM structure:**
   - Use browser developer tools to inspect elements

2. **Check CSS loading:**
   - Verify stylesheets are properly loaded

3. **Test with different screen sizes:**
   - Check responsive design issues

4. **Validate HTML:**
   - Check for HTML validation errors

## Installation Issues

### Issue: Cannot Install Dependencies

**Symptoms:**
- pip install fails
- Package conflicts

**Solutions:**

1. **Update pip:**
   ```bash
   python -m pip install --upgrade pip
   ```

2. **Use a clean virtual environment:**
   ```bash
   python -m venv fresh_venv
   source fresh_venv/bin/activate  # On Windows: fresh_venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Check for specific errors:**
   - Research specific package errors

4. **Update requirements.txt:**
   - Try updating package versions

### Issue: Static Files Not Loading

**Symptoms:**
- Missing CSS or JavaScript
- Unstyled pages

**Solutions:**

1. **Check static files configuration:**
   ```python
   # settings.py
   print(STATIC_URL, STATICFILES_DIRS, STATIC_ROOT)
   ```

2. **Collect static files:**
   ```bash
   python manage.py collectstatic
   ```

3. **Verify file paths:**
   - Check template references to static files

4. **Check web server configuration:**
   - Ensure web server is configured to serve static files

## Data Integrity Issues

### Issue: Corrupted or Inconsistent Data

**Symptoms:**
- Unexplained errors when accessing certain items
- Incomplete or incorrect musical data

**Solutions:**

1. **Check database integrity:**
   ```sql
   -- In PostgreSQL
   VACUUM ANALYZE positionfinder_notes;
   ```

2. **Validate data relationships:**
   ```python
   # In Django shell
   from positionfinder.models import Notes, NotesPosition
   
   # Check for orphaned positions
   orphans = NotesPosition.objects.filter(notes_name__isnull=True)
   print(list(orphans))
   ```

3. **Restore from backup:**
   - Use a database backup to restore clean data

4. **Rebuild specific data:**
   - Delete and recreate problematic data entries

## Deployment Issues

### Issue: Production Deployment Failures

**Symptoms:**
- Application works locally but fails in production
- 500 errors on production server

**Solutions:**

1. **Check production logs:**
   - Server error logs
   - Application logs

2. **Verify environment differences:**
   - Database configuration
   - Static files path
   - Debug settings

3. **Test with DEBUG=False locally:**
   - Identify issues that only appear with DEBUG disabled

4. **Step-by-step deployment:**
   - Deploy components individually to identify issues

## Common Error Messages and Solutions

### "No module named 'positionfinder'"

**Cause:** Python cannot find the application module.

**Solutions:**
- Check your PYTHONPATH
- Verify the app is installed in the correct directory
- Restart the Python interpreter

### "OperationalError: FATAL: database 'fretboard' does not exist"

**Cause:** PostgreSQL database doesn't exist.

**Solutions:**
- Create the database: `createdb fretboard`
- Check database name in settings
- Verify PostgreSQL server is running

### "TypeError: Object of type Decimal is not JSON serializable"

**Cause:** Trying to convert Decimal values to JSON.

**Solution:**
```python
import json
from decimal import Decimal

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

# Use this encoder
json_data = json.dumps(data, cls=DecimalEncoder)
```

### "MultipleObjectsReturned: get() returned more than one ChordNotes"

**Cause:** Multiple objects match your query when only one was expected.

**Solution:**
```python
# Instead of:
chord = ChordNotes.objects.get(chord_name='Major 7')

# Use:
chords = ChordNotes.objects.filter(chord_name='Major 7')
if chords.exists():
    chord = chords.first()
    # Use chord
```
