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

    // Function to get URL parameter value
    function getUrlParam(paramName, defaultValue) {
        const queryString = window.location.search;
        const urlParams = new URLSearchParams(queryString);
        return urlParams.get(paramName) || defaultValue;
    }

    // Default URL parameters
    let urlParams = {
        models_select: getUrlParam('models_select', '3'),
        root: getUrlParam('root', '1'),
        type_options_select: getUrlParam('type_options_select', 'Triads'),
        chords_options_select: getUrlParam('chords_options_select', 'Major'),
        note_range: getUrlParam('note_range', 'e - g'),
        position_select: getUrlParam('position_select', 'Basic Position')
    };

    // Ensure the overlay menu is hidden initially
    overlayMenuChords.style.display = 'none';

    overlayToggleChords.addEventListener('click', function() {
        overlayMenuChords.style.display = 'flex';
        initialStepChords.classList.add('active');
    });

    closeOverlayChords.addEventListener('click', function() {
        overlayMenuChords.style.display = 'none';
        resetStepsChords();
    });

    selectRootNoteChords.addEventListener('click', function() {
        initialStepChords.classList.remove('active');
        rootStepChords.classList.add('active');
    });

    selectTypeChords.addEventListener('click', function() {
        initialStepChords.classList.remove('active');
        typeStepChords.classList.add('active');
    });

    selectChord.addEventListener('click', function() {
        initialStepChords.classList.remove('active');
        chordStep.classList.add('active');
    });

    selectNoteRange.addEventListener('click', function() {
        initialStepChords.classList.remove('active');
        noteRangeStep.classList.add('active');
    });

    selectPositionChords.addEventListener('click', function() {
        initialStepChords.classList.remove('active');
        positionStepChords.classList.add('active');
    });

    backToInitialFromRootChords.addEventListener('click', function() {
        rootStepChords.classList.remove('active');
        initialStepChords.classList.add('active');
    });

    backToInitialFromTypeChords.addEventListener('click', function() {
        typeStepChords.classList.remove('active');
        initialStepChords.classList.add('active');
    });

    backToInitialFromChord.addEventListener('click', function() {
        chordStep.classList.remove('active');
        initialStepChords.classList.add('active');
    });

    backToInitialFromNoteRange.addEventListener('click', function() {
        noteRangeStep.classList.remove('active');
        initialStepChords.classList.add('active');
    });

    backToInitialFromPositionChords.addEventListener('click', function() {
        positionStepChords.classList.remove('active');
        initialStepChords.classList.add('active');
    });

    document.querySelectorAll('.grid-item').forEach(item => {
        item.addEventListener('click', function() {
            const value = this.getAttribute('data-value');
            const step = this.closest('.step').id;

            // Update URL parameters based on the step
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
        rootStepChords.classList.remove('active');
        typeStepChords.classList.remove('active');
        chordStep.classList.remove('active');
        noteRangeStep.classList.remove('active');
        positionStepChords.classList.remove('active');
    }

    // Optional: Close overlay when clicking outside the content
    overlayMenuChords.addEventListener('click', function(event) {
        if (event.target === overlayMenuChords) {
            overlayMenuChords.style.display = 'none';
            resetStepsChords();
        }
    });
});
