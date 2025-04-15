import difflib

# Define canonical lists for fuzzy matching and normalization
NOTES = ["C", "C#", "Db", "D", "D#", "Eb", "E", "F", "F#", "Gb", "G", "G#", "Ab", "A", "A#", "Bb", "B"]
TYPES = ["chord", "scale", "arpeggio"]
QUALITIES = [
    "major", "minor", "maj7", "min7", "dominant 7", "dim7", "m7b5", "pentatonic", "minor pentatonic", "harmonic major", "harmonic minor",
    "melodic minor", "dorian", "phrygian", "lydian", "mixolydian", "locrian", "augmented", "diminished"
]
POSITIONS = [f"V{i}" for i in range(1, 15)] + ["all positions"]
INVERSIONS = ["root position", "1st inversion", "2nd inversion", "3rd inversion", "basic position"]


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

    # Fuzzy match for quality/flavor (prefer multi-word and non-adjacent matches)
    quality = best_fuzzy_match(joined, QUALITIES) or QUALITIES[0]

    # Fuzzy match for position (case-insensitive)
    position = best_fuzzy_match(joined, POSITIONS, case_sensitive=False)

    # Fuzzy match for inversion
    inversion = best_fuzzy_match(joined, INVERSIONS) or "basic position"

    return note, type_, quality, position, inversion
