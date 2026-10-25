"""
Guitar Positions Studio: the redesigned single-page fretboard app.

The studio renders everything client-side from one JSON catalogue that is built
from the existing database models (scales, arpeggios and V-System chord voicings),
so the musical content stays managed in Django while the UI is a fast SPA.
"""

from django.core.cache import cache
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET

from .models import Notes, Root
from .models_chords import ChordNotes

CATALOG_CACHE_KEY = "studio_catalog_v1"
CATALOG_CACHE_SECONDS = 60 * 60

NOTE_FIELDS = (
    "first_note",
    "second_note",
    "third_note",
    "fourth_note",
    "fifth_note",
    "sixth_note",
    "seventh_note",
    "eigth_note",
    "ninth_note",
    "tenth_note",
    "eleventh_note",
    "twelth_note",
)
CHORD_NOTE_FIELDS = (
    "first_note",
    "second_note",
    "third_note",
    "fourth_note",
    "fifth_note",
    "sixth_note",
)

# Legacy query parameter `models_select` -> studio mode
LEGACY_MODES = {"1": "scale", "2": "arpeggio", "3": "chord"}


def _intervals(obj, fields):
    """Pitch classes relative to the object's tonal root, in stored order, without duplicates."""
    seen = []
    for field in fields:
        value = getattr(obj, field, None)
        if value is None:
            continue
        interval = (value - obj.tonal_root) % 12
        if interval not in seen:
            seen.append(interval)
    return seen


def _normalise_chord_name(name):
    # The database contains both "Minor 7b5" and "Minor7b5"
    return "Minor 7b5" if name.replace(" ", "") == "Minor7b5" else name.strip()


def build_catalog():
    scales, arpeggios = [], []
    for note in Notes.objects.select_related("category").order_by("category_id", "ordering", "id"):
        intervals = sorted(_intervals(note, NOTE_FIELDS))
        if len(intervals) < 3:
            continue  # incomplete records carry no usable formula
        entry = {"id": note.id, "name": note.note_name.strip(), "intervals": intervals}
        if note.category_id == 1:
            scales.append(entry)
        elif note.category_id == 2:
            arpeggios.append(entry)

    chords = {}
    for voicing in ChordNotes.objects.order_by(
        "ordering", "chord_ordering", "range_ordering", "id"
    ):
        name = _normalise_chord_name(voicing.chord_name)
        tones = []
        for index, field in enumerate(CHORD_NOTE_FIELDS):
            value = getattr(voicing, field)
            string = getattr(voicing, f"{field}_string")
            if value is None or not string:
                continue
            tones.append(
                {"string": string, "interval": (value - voicing.tonal_root) % 12, "order": index}
            )
        if len(tones) < 3:
            continue
        chord = chords.setdefault(name, {"name": name, "intervals": set(), "voicings": []})
        chord["intervals"].update(t["interval"] for t in tones)
        chord["voicings"].append(
            {
                "id": voicing.id,
                "system": voicing.type_name,
                "range": voicing.range,
                "tones": [{"string": t["string"], "interval": t["interval"]} for t in tones],
            }
        )

    chord_list = []
    for chord in chords.values():
        chord["intervals"] = sorted(chord["intervals"])
        chord_list.append(chord)

    roots = [{"id": r.id, "name": r.name, "pitch": r.pitch} for r in Root.objects.all()]
    return {
        "version": 1,
        "scales": scales,
        "arpeggios": arpeggios,
        "chords": chord_list,
        "roots": roots,
    }


def clear_catalog_cache(**kwargs):
    cache.delete(CATALOG_CACHE_KEY)


def get_catalog():
    catalog = cache.get(CATALOG_CACHE_KEY)
    if catalog is None:
        catalog = build_catalog()
        cache.set(CATALOG_CACHE_KEY, catalog, CATALOG_CACHE_SECONDS)
    return catalog


@require_GET
def catalog_json(request):
    response = JsonResponse(get_catalog())
    response["Cache-Control"] = "public, max-age=3600"
    return response


def _legacy_state(request):
    """Translate old `/?models_select=..&root=..&notes_options_id=..` links into studio state."""
    params = request.GET
    state = {}
    mode = LEGACY_MODES.get(params.get("models_select", ""))
    if mode:
        state["mode"] = mode
    root_id = params.get("root")
    if root_id and root_id.isdigit():
        root = Root.objects.filter(pk=int(root_id)).first()
        if root:
            state["root"] = root.pitch
    notes_id = params.get("notes_options_id")
    if mode in ("scale", "arpeggio") and notes_id and notes_id.isdigit():
        state["typeId"] = int(notes_id)
    if mode == "chord":
        for param, key in (
            ("chords_options_select", "chordName"),
            ("type_options_select", "system"),
            ("note_range", "range"),
        ):
            if params.get(param):
                state[key] = params[param]
    position = params.get("position_select")
    if position and position.isdigit():
        state["position"] = int(position)
    return state


def studio_view(request):
    context = {
        "catalog_json": get_catalog(),
        "legacy_state_json": _legacy_state(request),
    }
    return render(request, "studio/index.html", context)
