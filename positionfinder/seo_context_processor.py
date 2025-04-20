"""
SEO Context Processor for providing optimized meta tags to all templates.
This processor analyzes the current page content and generates appropriate meta tags.
"""

def get_seo_metadata(request):
    """
    Provides optimized SEO metadata based on the current URL path and context.
    
    Returns a dictionary with keys:
    - page_title: The HTML title tag content
    - meta_description: Content for the meta description tag
    - meta_keywords: Content for the meta keywords tag
    - og_title: Open Graph title
    - og_description: Open Graph description
    - twitter_title: Twitter card title
    - twitter_description: Twitter card description
    """
    path = request.path.strip('/')
    path_parts = path.split('/')
    
    # Default metadata (used if no specific rule matches)
    metadata = {
        'page_title': 'Guitar Positions | Complete Fretboard Visualization Tool',
        'meta_description': 'Find any scale, chord, or arpeggio position on the guitar fretboard. Free interactive tool for guitarists of all levels with comprehensive coverage of musical situations.',
        'meta_keywords': 'guitar positions, fretboard finder, guitar scales, guitar chords, guitar arpeggios, fretboard visualization, guitar learning tool',
        'og_title': 'Guitar Positions | Ultimate Fretboard Tool',
        'og_description': 'Interactive fretboard visualization for guitarists. Explore scales, modes, arpeggios, and chord positions across the entire fretboard.',
        'twitter_title': 'Guitar Positions | Fretboard Tool',
        'twitter_description': 'Find any guitar position instantly with our comprehensive fretboard visualization tool.'
    }
    
    # Path-specific metadata based on URL pattern
    if path == '':
        # Home page
        metadata.update({
            'page_title': 'Guitar Positions | Ultimate Fretboard Visualization Tool',
            'meta_description': 'Master the guitar fretboard with our comprehensive position finder. Find scales, modes, arpeggios, and chord positions for any musical situation, completely free and ad-free.',
        })
    elif path.startswith('scale/'):
        # Scale pages
        if len(path_parts) >= 3:
            root = path_parts[1].capitalize()
            scale_type = path_parts[2].replace('-', ' ').title()
            metadata.update({
                'page_title': f'{root} {scale_type} Scale | Complete Guitar Positions',
                'meta_description': f'Learn to play the {root} {scale_type} scale across the entire guitar fretboard. Interactive diagrams showing all positions, patterns, and fingerings.',
                'meta_keywords': f'{root} {scale_type} scale, {root} {scale_type} guitar, {scale_type} scale positions, guitar {scale_type} positions, {root} guitar scale',
                'og_title': f'{root} {scale_type} Scale | Guitar Positions',
                'og_description': f'Master the {root} {scale_type} scale with our interactive fretboard tool. Find all positions and patterns.',
                'twitter_title': f'{root} {scale_type} Scale',
                'twitter_description': f'Complete {root} {scale_type} scale positions for guitar.'
            })
        else:
            # Generic scales page
            metadata.update({
                'page_title': 'Guitar Scales | Complete Scale Library',
                'meta_description': 'Comprehensive collection of guitar scales with interactive fretboard positions. Major, minor, pentatonic, blues, modal, and exotic scales in all keys.',
                'meta_keywords': 'guitar scales, scale positions, scale patterns, guitar modes, pentatonic scales, blues scales',
            })
    elif path.startswith('arpeggio/'):
        # Arpeggio pages
        if len(path_parts) >= 3:
            root = path_parts[1].capitalize()
            arpeggio_type = path_parts[2].replace('-', ' ').title()
            metadata.update({
                'page_title': f'{root} {arpeggio_type} Arpeggio | Guitar Positions',
                'meta_description': f'Master the {root} {arpeggio_type} arpeggio on guitar with our interactive fretboard tool. All positions, patterns, and fingerings across the neck.',
                'meta_keywords': f'{root} {arpeggio_type} arpeggio, {arpeggio_type} guitar arpeggio, {root} guitar arpeggio, arpeggio patterns, {arpeggio_type} sweep picking',
                'og_title': f'{root} {arpeggio_type} Arpeggio | Guitar Positions',
                'og_description': f'Complete {root} {arpeggio_type} arpeggio positions for guitar. Interactive fretboard visualization.',
                'twitter_title': f'{root} {arpeggio_type} Arpeggio',
                'twitter_description': f'Master {root} {arpeggio_type} arpeggios across the fretboard.'
            })
        else:
            # Generic arpeggios page
            metadata.update({
                'page_title': 'Guitar Arpeggios | Complete Arpeggio Library',
                'meta_description': 'Learn guitar arpeggios with our interactive visualization tool. Major, minor, dominant, diminished, and augmented arpeggios in all positions and keys.',
                'meta_keywords': 'guitar arpeggios, arpeggio patterns, sweep picking, guitar sweep arpeggios, arpeggio technique, arpeggio positions',
            })
    elif path.startswith('chord/'):
        # Chord pages
        if len(path_parts) >= 3:
            root = path_parts[1].capitalize()
            chord_type = path_parts[2].replace('-', ' ')
            
            # Special handling for common chord types
            chord_description = chord_type
            if chord_type.lower() == 'major':
                chord_description = 'Major'
            elif chord_type.lower() == 'minor':
                chord_description = 'Minor'
            elif chord_type.lower() in ['7', 'dominant 7', 'dom7']:
                chord_description = 'Dominant 7th'
            elif chord_type.lower() in ['maj7', 'major 7']:
                chord_description = 'Major 7th'
            elif chord_type.lower() in ['min7', 'm7', 'minor 7']:
                chord_description = 'Minor 7th'
            
            metadata.update({
                'page_title': f'{root} {chord_description} Chord | Guitar Positions & Voicings',
                'meta_description': f'Learn to play {root} {chord_description} chord on guitar with our interactive tool. Multiple positions, voicings, and fingerings across the entire fretboard.',
                'meta_keywords': f'{root} {chord_description} chord, {root} {chord_type} guitar chord, {chord_description} guitar voicings, {root} guitar chord, {chord_description} chord fingerings',
                'og_title': f'{root} {chord_description} Chord | Guitar Positions',
                'og_description': f'Complete {root} {chord_description} chord positions and voicings for guitar. Interactive fretboard visualization.',
                'twitter_title': f'{root} {chord_description} Chord',
                'twitter_description': f'All {root} {chord_description} chord voicings and positions.'
            })
        else:
            # Generic chords page
            metadata.update({
                'page_title': 'Guitar Chords | Complete Chord Library & Voicings',
                'meta_description': 'Extensive library of guitar chords with multiple voicings and positions. Find optimal fingerings for any chord type in all keys across the entire fretboard.',
                'meta_keywords': 'guitar chords, chord voicings, chord fingerings, guitar chord shapes, chord progressions, chord inversions',
            })
    elif path.startswith('mode/'):
        # Mode pages
        if len(path_parts) >= 3:
            root = path_parts[1].capitalize()
            mode_name = path_parts[2].replace('-', ' ').title()
            metadata.update({
                'page_title': f'{root} {mode_name} Mode | Guitar Positions',
                'meta_description': f'Master the {root} {mode_name} mode on guitar with interactive fretboard diagrams. Complete positions, patterns, and fingerings for modal playing.',
                'meta_keywords': f'{root} {mode_name} mode, {mode_name} mode guitar, modal guitar positions, {mode_name} scale positions, {root} {mode_name} patterns',
                'og_title': f'{root} {mode_name} Mode | Guitar Positions',
                'og_description': f'Complete {root} {mode_name} mode positions for guitar. Interactive fretboard visualization for modal playing.',
                'twitter_title': f'{root} {mode_name} Mode',
                'twitter_description': f'Master {root} {mode_name} mode across the fretboard.'
            })
        else:
            # Generic modes page
            metadata.update({
                'page_title': 'Guitar Modes | Complete Modal Playing Guide',
                'meta_description': 'Comprehensive guide to guitar modes with interactive fretboard positions. Master Ionian, Dorian, Phrygian, Lydian, Mixolydian, Aeolian, and Locrian modes.',
                'meta_keywords': 'guitar modes, modal playing, modal scales, Dorian mode, Phrygian mode, Lydian mode, Mixolydian mode, Aeolian mode, Locrian mode',
            })
    elif path == 'about':
        metadata.update({
            'page_title': 'About Guitar Positions | The Complete Fretboard Tool',
            'meta_description': 'Learn about our mission to provide guitarists with the most comprehensive, ad-free tool for mastering the fretboard. Created by guitarists for guitarists.',
            'meta_keywords': 'about guitar positions, fretboard tool, guitar learning, music education, guitar teaching tool',
        })
            
    return metadata
