import difflib
import logging

# Reduce logging to WARNING or ERROR for search logic bugfixing
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

# Define canonical lists for fuzzy matching and normalization
NOTES = ["C", "C#", "Db", "D", "D#", "Eb", "E", "F", "F#", "Gb", "G", "G#", "Ab", "A", "A#", "Bb", "B"]
TYPES = ["chord", "scale", "arpeggio"]
QUALITIES = [
    "major", "minor", "maj7", "min7", "dominant 7", "dim7", "m7b5", "pentatonic", "minor pentatonic", "harmonic major", "harmonic minor",
    "melodic minor", "dorian", "phrygian", "lydian", "mixolydian", "locrian", "augmented", "diminished"
]
POSITIONS = [f"V{i}" for i in range(1, 15)] + ["all positions"]
INVERSIONS = ["root position", "1st inversion", "2nd inversion", "3rd inversion", "basic position"]

# Custom root note to ID mapping as per user logic
ROOT_NAME_TO_ID = {
    'C': 1,
    'Db': 2,
    'C#': 3,
    'D': 4,
    'Eb': 5,
    'D#': 6,
    'E': 7,
    'F': 8,
    'Gb': 9,
    'F#': 10,
    'G': 11,
    'Ab': 12,
    'G#': 13,
    'A': 14,
    'Bb': 15,
    'A#': 16,
    'B': 17,
}

def get_root_id_from_name(note_name):
    """
    Given a note name (e.g., 'Eb', 'C#', 'F'), return the mapped root ID according to the user's custom logic.
    Returns None if not found.
    """
    if not note_name:
        return None
    note_name = note_name.strip().capitalize().replace('♯', '#').replace('♭', 'b')
    # Try direct match
    if note_name in ROOT_NAME_TO_ID:
        return ROOT_NAME_TO_ID[note_name]
    # Try common enharmonic equivalents (e.g., D# <-> Eb, Gb <-> F#)
    enharmonics = {
        'Db': 'C#', 'C#': 'Db',
        'D#': 'Eb', 'Eb': 'D#',
        'Gb': 'F#', 'F#': 'Gb',
        'Ab': 'G#', 'G#': 'Ab',
        'Bb': 'A#', 'A#': 'Bb',
    }
    if note_name in enharmonics and enharmonics[note_name] in ROOT_NAME_TO_ID:
        return ROOT_NAME_TO_ID[enharmonics[note_name]]
    return None


def fuzzy_find(token, choices, cutoff=0.7):
    """
    Return the closest match from choices for the token, or None if below cutoff.
    """
    match = difflib.get_close_matches(token, choices, n=1, cutoff=cutoff)
    return match[0] if match else None


def best_fuzzy_match(query, choices, cutoff=0.7, case_sensitive=True):
    """
    Try all substrings of the query (from tokens) and return the longest, best fuzzy match.
    Prefer multi-word matches (up to 3 words) for qualities.
    For qualities, also try all non-adjacent pairs/triplets of tokens.
    If case_sensitive is False, match in uppercase.
    """
    tokens = query.split() if case_sensitive else query.lower().split()
    best = None
    best_len = 0
    norm_choices = choices if case_sensitive else [c.lower() for c in choices]
    # Try all adjacent windows first (3, 2, 1)
    for window in (3, 2, 1):
        for i in range(len(tokens) - window + 1):
            substring = " ".join(tokens[i:i+window])
            norm_sub = substring if case_sensitive else substring.lower()
            match = fuzzy_find(norm_sub, norm_choices, cutoff=cutoff)
            if match and window > best_len:
                # Return original casing from choices
                idx = norm_choices.index(match)
                best = choices[idx]
                best_len = window
        if best:
            break
    # If still not found and window > 1, try all non-adjacent pairs/triplets for qualities
    if not best and len(tokens) > 1:
        # Try all pairs
        for i in range(len(tokens)):
            for j in range(i+1, len(tokens)):
                substring = f"{tokens[i]} {tokens[j]}"
                norm_sub = substring if case_sensitive else substring.lower()
                match = fuzzy_find(norm_sub, norm_choices, cutoff=cutoff)
                if match and 2 > best_len:
                    idx = norm_choices.index(match)
                    best = choices[idx]
                    best_len = 2
        # Try all triplets
        if len(tokens) > 2:
            for i in range(len(tokens)):
                for j in range(i+1, len(tokens)):
                    for k in range(j+1, len(tokens)):
                        substring = f"{tokens[i]} {tokens[j]} {tokens[k]}"
                        norm_sub = substring if case_sensitive else substring.lower()
                        match = fuzzy_find(norm_sub, norm_choices, cutoff=cutoff)
                        if match and 3 > best_len:
                            idx = norm_choices.index(match)
                            best = choices[idx]
                            best_len = 3
    return best


def parse_query(user_query):
    """
    Parse and normalize the user query, applying fuzzy matching and sensible defaults.
    Returns: (note, type, quality, position, inversion)
    """
    tokens = user_query.lower().replace('-', ' ').split()
    joined = " ".join(tokens)

    # Fuzzy match for note (single tokens only)
    note = next((fuzzy_find(t.capitalize(), NOTES) for t in tokens if fuzzy_find(t.capitalize(), NOTES)), "C")

    # Fuzzy match for type (chord/scale/arpeggio)
    type_ = next((fuzzy_find(t, TYPES) for t in tokens if fuzzy_find(t, TYPES)), "chord")

    # Fuzzy match for quality
    quality = best_fuzzy_match(joined, QUALITIES, cutoff=0.6, case_sensitive=False) or "major"

    # Fuzzy match for position
    position = best_fuzzy_match(joined, POSITIONS, cutoff=0.7, case_sensitive=False) or ""

    # Fuzzy match for inversion
    inversion = best_fuzzy_match(joined, INVERSIONS, cutoff=0.7, case_sensitive=False) or "basic position"

    # Override type_ for scale-specific qualities
    scale_terms = {"pentatonic","minor pentatonic","major pentatonic","harmonic minor","harmonic major","melodic minor","dorian","phrygian","lydian","mixolydian","locrian","augmented","diminished"}
    if quality.lower() in scale_terms or 'pentatonic' in quality.lower():
        type_ = "scale"
    # Override type_ for chord-specific qualities
    chord_terms = {"maj7","min7","dominant 7","dim7","m7b5"}
    if quality.lower() in chord_terms:
        type_ = "chord"
    return note, type_, quality, position, inversion


def resolve_root(note_name, _cache={}):
    """
    Given a note name (e.g., 'C#', 'Db'), return the matching Root object from the DB.
    Tries all enharmonic equivalents and capitalization variants.
    Returns None if no match found.
    Uses a cache to avoid redundant DB lookups for the same note_name in the same request context.
    """
    if note_name in _cache:
        print(f"[ROOT DEBUG] (CACHE HIT) '{note_name}' -> Root: {_cache[note_name]}")
        return _cache[note_name]
    from .models import Root
    # Canonicalize input
    candidates = set()
    base = note_name.strip().capitalize().replace('♯', '#').replace('♭', 'b')
    candidates.add(base)
    # Add enharmonic equivalents
    enharmonics = {
        'C#': 'Db', 'Db': 'C#',
        'D#': 'Eb', 'Eb': 'D#',
        'F#': 'Gb', 'Gb': 'F#',
        'G#': 'Ab', 'Ab': 'G#',
        'A#': 'Bb', 'Bb': 'A#',
    }
    if base in enharmonics:
        candidates.add(enharmonics[base])
    # Try all candidates
    for cand in candidates:
        root = Root.objects.filter(name__iexact=cand).first()
        print(f"[ROOT DEBUG] Trying candidate: '{cand}' -> Root: {root}")
        if root:
            print(f"[ROOT DEBUG] Resolved '{note_name}' to Root: {root}")
            _cache[note_name] = root
            return root
    # Fallback: try partial match (e.g., 'C' in 'C#')
    root = Root.objects.filter(name__icontains=base).first()
    print(f"[ROOT DEBUG] Fallback partial match for '{base}' -> Root: {root}")
    if root:
        print(f"[ROOT DEBUG] Resolved '{note_name}' to Root (partial): {root}")
        _cache[note_name] = root
        return root
    print(f"[ROOT DEBUG] Could not resolve root for '{note_name}'")
    _cache[note_name] = None
    return None
