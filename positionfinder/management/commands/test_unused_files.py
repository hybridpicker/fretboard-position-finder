"""
Django management command to test if removing certain static files affects the application.
This command temporarily renames files and allows you to test the application.

Usage:
    python manage.py test_unused_files [--hide js,css] [--restore]
"""

import os
import shutil
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = 'Test if removing unused JS/CSS files affects the application'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--hide',
            help='Temporarily hide JS and/or CSS files (comma-separated)',
            default='js,css'
        )
        parser.add_argument(
            '--restore',
            action='store_true',
            help='Restore all hidden files'
        )
    
    def handle(self, *args, **options):
        # High confidence files to test removal
        js_files = [
            'base_fixed.js',
            'c_major_final_fix.js',
            'c_major_fix.js',
            'c_major_fix_v2.js',
            'chord_note_autofix.js',
            'chord_ui_enhancements_fixed.js',
            'debug-helpers.js',
            'direct_keyboard_fix.js',
            'fixed-chord-inversions.js',
            'installHook.js',
            'keyboard_navigation_fix.js',
            'root_note_fix.js'
        ]
        
        css_files = []  # No high confidence CSS files to test
        
        # Determine the static directory path
        static_dir = os.path.join(settings.BASE_DIR, 'static')
        
        # Create backup directories if they don't exist
        backup_js_dir = os.path.join(static_dir, 'backup_js')
        backup_css_dir = os.path.join(static_dir, 'backup_css')
        
        if not os.path.exists(backup_js_dir):
            os.makedirs(backup_js_dir)
        
        if not os.path.exists(backup_css_dir):
            os.makedirs(backup_css_dir)
        
        # Restore all hidden files if requested
        if options['restore']:
            self.restore_files(static_dir, backup_js_dir, backup_css_dir)
            return
        
        # Determine which file types to hide
        file_types = options['hide'].split(',')
        
        # Hide JS files if requested
        if 'js' in file_types:
            self.hide_files(static_dir, 'js', js_files, backup_js_dir)
        
        # Hide CSS files if requested
        if 'css' in file_types:
            self.hide_files(static_dir, 'css', css_files, backup_css_dir)
        
        self.stdout.write(self.style.SUCCESS(
            f"Temporarily hidden files. Test the application now. "
            f"To restore all files, run: python manage.py test_unused_files --restore"
        ))
    
    def hide_files(self, static_dir, file_type, files, backup_dir):
        """Temporarily hide files by moving them to a backup directory."""
        type_dir = os.path.join(static_dir, file_type)
        
        count = 0
        for file in files:
            src_path = os.path.join(type_dir, file)
            if os.path.exists(src_path):
                dst_path = os.path.join(backup_dir, file)
                shutil.move(src_path, dst_path)
                self.stdout.write(f"Temporarily hidden: {file}")
                count += 1
        
        self.stdout.write(self.style.SUCCESS(f"Hidden {count} {file_type} files"))
    
    def restore_files(self, static_dir, backup_js_dir, backup_css_dir):
        """Restore all hidden files."""
        # Restore JS files
        js_count = self.restore_file_type(static_dir, 'js', backup_js_dir)
        
        # Restore CSS files
        css_count = self.restore_file_type(static_dir, 'css', backup_css_dir)
        
        self.stdout.write(self.style.SUCCESS(
            f"Restored {js_count} JS files and {css_count} CSS files"
        ))
    
    def restore_file_type(self, static_dir, file_type, backup_dir):
        """Restore all files of a specific type."""
        type_dir = os.path.join(static_dir, file_type)
        count = 0
        
        for file in os.listdir(backup_dir):
            src_path = os.path.join(backup_dir, file)
            if os.path.isfile(src_path):
                dst_path = os.path.join(type_dir, file)
                shutil.move(src_path, dst_path)
                self.stdout.write(f"Restored: {file}")
                count += 1
        
        return count
