#!/usr/bin/env python
import os
import sys
import django
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fretboard.settings')
django.setup()

from positionfinder.models import Root, NotesCategory
from positionfinder.models_chords import ChordNotes
from django.db.models import Q

def test_arpeggio_search(note_name, quality):
    """Test a manual version of the search_arpeggios function"""
    logger.debug(f"Testing search for note='{note_name}', quality='{quality}'")
    
    # Start with base arpeggio query
    qs = ChordNotes.objects.filter(category__category_name__icontains='arpeggio')
    logger.debug(f"Base arpeggio query returns {qs.count()} results")
    
    # Filter by root note
    if note_name:
        # First try to find the note by name
        root_obj = Root.objects.filter(name__iexact=note_name).first()
        
        if root_obj:
            # Use the pitch value for filtering (not the ID)
            root_pitch = root_obj.pitch
            logger.debug(f"Filtering by root_pitch: {root_pitch} (note: {note_name}, ID: {root_obj.id})")
            qs = qs.filter(tonal_root=root_pitch)
            logger.debug(f"After root filter: {qs.count()} results")
        else:
            logger.warning(f"Could not find root for note: {note_name}")
    
    # Filter by quality
    if quality:
        # Use Q object for more flexible quality matching
        quality_filters = Q()
        variations = [quality, quality.capitalize(), quality.lower()]
        
        if quality.lower() == 'minor':
            variations.extend(['Min', 'm', 'minor pentatonic', 'Minor Pentatonic'])
        elif quality.lower() == 'major':
            variations.extend(['Maj', 'major pentatonic', 'Major Pentatonic'])
            
        for var in set(variations):
            quality_filters |= Q(chord_name__icontains=var)
            
        logger.debug(f"Applying quality filters: {variations}")
        qs = qs.filter(quality_filters)
        logger.debug(f"After quality filter: {qs.count()} results")
    
    # Show results
    logger.debug(f"Final results: {qs.count()}")
    
    for arp in qs:
        logger.debug(f"ID: {arp.id}, Category: {arp.category}, Type: {arp.type_name}, Name: {arp.chord_name}, Root: {arp.tonal_root}, Range: {arp.range}")
    
    return qs

if __name__ == "__main__":
    print("Testing arpeggio search for A minor...")
    result = test_arpeggio_search('A', 'minor')
    print(f"\nFound {result.count()} results")
    
    if result.count() > 0:
        print("\nChecking URL generation...")
        first_result = result.first()
        url = f"/?root=14&models_select=2&notes_options_select={first_result.chord_name}&position_select=0"
        print(f"Generated URL: {url}")
        
        # Generate proper URL for search results
        print("\nOptimized URL:")
        url = f"/?root=14&models_select=2&notes_options_select={first_result.id}&position_select=0"
        print(f"Generated URL: {url}")
