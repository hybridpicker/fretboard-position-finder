document.addEventListener("DOMContentLoaded", function() {
    const overlayToggleChords = document.getElementById('overlayToggleChords');
    const overlayMenuChords = document.getElementById('overlayMenuChords');
    const closeOverlayChords = document.getElementById('closeOverlayChords');

    const initialStepChords = document.getElementById('initialStepChords');
    const rootStepChords = document.getElementById('rootStepChords');
    const typeStepChords = document.getElementById('typeStepChords');
    const chordStep = document.getElementById('chordStep');
    const noteRangeStep = document.getElementById('noteRangeStep');
    const positionStepChords = document.getElementById('positionStepChords');

    const selectRootNoteChords = document.getElementById('selectRootNoteChords');
    const selectTypeChords = document.getElementById('selectTypeChords');
    const selectChord = document.getElementById('selectChord');
    const selectNoteRange = document.getElementById('selectNoteRange');
    const selectPositionChords = document.getElementById('selectPositionChords');

    const backToInitialFromRootChords = document.getElementById('backToInitialFromRootChords');
    const backToInitialFromTypeChords = document.getElementById('backToInitialFromTypeChords');
    const backToInitialFromChord = document.getElementById('backToInitialFromChord');
    const backToInitialFromNoteRange = document.getElementById('backToInitialFromNoteRange');
    const backToInitialFromPositionChords = document.getElementById('backToInitialFromPositionChords');

    function getUrlParam(paramName, defaultValue) {
        const queryString = window.location.search;
        const urlParams = new URLSearchParams(queryString);
        return urlParams.get(paramName) || defaultValue;
    }

    function setFormValuesFromParams() {
        const params = new URLSearchParams(window.location.search);

        const modelsSelect = document.getElementById('models_select');
        const rootSelect = document.getElementById('root');
        const typeOptionsSelect = document.getElementById('type_options_select');
        const chordsOptionsSelect = document.getElementById('chords_options_select');
        const noteRangeSelect = document.getElementById('note_range');
        const positionSelect = document.getElementById('position_select');

        const modelsValue = params.get('models_select') || '3';
        const rootValue = params.get('root') || '1';
        const typeOptionsValue = params.get('type_options_select') || 'Triads';
        const chordsOptionsValue = params.get('chords_options_select') || 'Major';
        const noteRangeValue = params.get('note_range') || 'e - g';
        const positionValue = params.get('position_select') || 'Basic Position';

        if (modelsSelect) modelsSelect.value = modelsValue;
        if (rootSelect) rootSelect.value = rootValue;
        if (typeOptionsSelect) typeOptionsSelect.value = typeOptionsValue;
        if (chordsOptionsSelect) chordsOptionsSelect.value = chordsOptionsValue;
        if (noteRangeSelect) noteRangeSelect.value = noteRangeValue;
        if (positionSelect) positionSelect.value = positionValue;
    }

    // Call the function to initialize the form values
    setFormValuesFromParams();

    // Ensure the overlay menu is hidden initially
    overlayMenuChords.style.display = 'none';

    // Event listeners to show/hide overlay and navigate steps
    overlayToggleChords.addEventListener('click', function() {
        overlayMenuChords.style.display = 'flex';
        initialStepChords.style.display = 'block';
        initialStepChords.classList.add('active');
    });

    closeOverlayChords.addEventListener('click', function() {
        overlayMenuChords.style.display = 'none';
        resetStepsChords();
    });

    selectRootNoteChords.addEventListener('click', function() {
        initialStepChords.style.display = 'none';
        rootStepChords.style.display = 'block';
    });

    selectTypeChords.addEventListener('click', function() {
        initialStepChords.style.display = 'none';
        typeStepChords.style.display = 'block';
    });

    selectChord.addEventListener('click', function() {
        initialStepChords.style.display = 'none';
        chordStep.style.display = 'block';
    });

    selectNoteRange.addEventListener('click', function() {
        initialStepChords.style.display = 'none';
        noteRangeStep.style.display = 'block';
    });

    selectPositionChords.addEventListener('click', function() {
        initialStepChords.style.display = 'none';
        positionStepChords.style.display = 'block';
    });

    backToInitialFromRootChords.addEventListener('click', function() {
        rootStepChords.style.display = 'none';
        initialStepChords.style.display = 'block';
    });

    backToInitialFromTypeChords.addEventListener('click', function() {
        typeStepChords.style.display = 'none';
        initialStepChords.style.display = 'block';
    });

    backToInitialFromChord.addEventListener('click', function() {
        chordStep.style.display = 'none';
        initialStepChords.style.display = 'block';
    });

    backToInitialFromNoteRange.addEventListener('click', function() {
        noteRangeStep.style.display = 'none';
        initialStepChords.style.display = 'block';
    });

    backToInitialFromPositionChords.addEventListener('click', function() {
        positionStepChords.style.display = 'none';
        initialStepChords.style.display = 'block';
    });

    // Event listeners for grid items
    document.querySelectorAll('.grid-item').forEach(item => {
        item.addEventListener('click', function() {
            const value = this.getAttribute('data-value');
            const step = this.closest('.step').id;

            if (step === 'rootStepChords') {
                urlParams.root = value;
            } else if (step === 'typeStepChords') {
                urlParams.type_options_select = value;
            } else if (step === 'chordStep') {
                urlParams.chords_options_select = value;
            } else if (step === 'noteRangeStep') {
                urlParams.note_range = value;
            } else if (step === 'positionStepChords') {
                urlParams.position_select = value;
            }

            submitFormChords();
        });
    });

    function submitFormChords() {
        const queryParams = new URLSearchParams(urlParams).toString();
        window.location.href = '?' + queryParams;
    }

    function resetStepsChords() {
        initialStepChords.classList.remove('active');
        initialStepChords.style.display = 'block';

        rootStepChords.classList.remove('active');
        rootStepChords.style.display = 'none';

        typeStepChords.classList.remove('active');
        typeStepChords.style.display = 'none';

        chordStep.classList.remove('active');
        chordStep.style.display = 'none';

        noteRangeStep.classList.remove('active');
        noteRangeStep.style.display = 'none';

        positionStepChords.classList.remove('active');
        positionStepChords.style.display = 'none';
    }

    overlayMenuChords.addEventListener('click', function(event) {
        if (event.target === overlayMenuChords) {
            overlayMenuChords.style.display = 'none';
            resetStepsChords();
        }
    });
});
