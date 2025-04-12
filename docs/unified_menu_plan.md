# Unified Overlay Menu Plan

**Goal:** Consolidate Scale, Arpeggio, and Chord selection into a single overlay menu triggered by one button. The user first selects the mode (Scale, Arpeggio, Chord).

**Phase 1: Planning & Design**

1.  **Define Menu Structure (HTML - `templates/overlay-menu/unified_menu.html`):**
    *   Trigger: Single button/icon.
    *   Main Container: `<div id="unifiedOverlayMenu" class="overlay-menu">...</div>`
    *   Initial Step (`id="initialStep"`): Buttons: "Scales", "Arpeggios", "Chords".
    *   Scale Steps: Root Note, Scale Type, Position.
    *   Arpeggio Steps: Root Note, Arpeggio Type, Position.
    *   Chord Steps: Root Note, Chord Type, Chord Name, Note Range, Position.
    *   Navigation: Consistent "Back" and "Close" buttons.
2.  **Design Interaction Logic (JavaScript - `static/js/unified_menu.js`):**
    *   Toggle menu visibility.
    *   Handle navigation between steps.
    *   Manage state.
    *   Submit final selection (AJAX).
3.  **Backend Context (Django Views):**
    *   Modify main view(s) to provide all necessary context data.
    *   Handle AJAX request for updates.
4.  **Styling (CSS - `static/css/unified_menu.css` or similar):**
    *   Style the unified menu elements.

**Phase 2: Implementation (Requires switching to Code Mode)**

1.  Create/Modify HTML, JS, CSS files.
2.  Update Django View(s).
3.  Integrate into base template, replace old includes.
4.  Remove/comment out old menu files/code.

**Phase 3: Testing & Refinement**

1.  Test all three paths (Scale, Arpeggio, Chord).
2.  Test navigation, state, AJAX updates.
3.  Verify styling and responsiveness.

**Diagrammatic Overview (Mermaid):**

```mermaid
graph TD
    A[User Clicks Trigger Button] --> B{Unified Overlay Menu Opens};
    B --> C{Initial Step: Choose Mode};
    C -- "Scales" --> D[Scale Steps: Root, Type, Position];
    C -- "Arpeggios" --> E[Arpeggio Steps: Root, Type, Position];
    C -- "Chords" --> F[Chord Steps: Root, Type, Chord, Range, Position];
    D --> G[Selection Applied via JS/AJAX];
    E --> G;
    F --> G;
    G --> H{Overlay Closes / Main View Updates};

    subgraph Navigation
        D --> C;
        E --> C;
        F --> C;
        C --> B;
    end

    subgraph Steps within Scale
        D1[Select Root] --> D2[Select Scale Type] --> D3[Select Position] --> D;
        D3 -- Back --> D2 -- Back --> D1 -- Back --> C;
    end

    subgraph Steps within Arpeggio
        E1[Select Root] --> E2[Select Arpeggio Type] --> E3[Select Position] --> E;
         E3 -- Back --> E2 -- Back --> E1 -- Back --> C;
    end

    subgraph Steps within Chord
        F1[Select Root] --> F2[Select Chord Type] --> F3[Select Chord Name] --> F4[Select Range] --> F5[Select Position] --> F;
        F5 -- Back --> F4 -- Back --> F3 -- Back --> F2 -- Back --> F1 -- Back --> C;
    end