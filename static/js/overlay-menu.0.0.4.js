function initializeOverlayMenu() {
    const overlayToggle = document.getElementById('overlayToggle');
    const overlayMenu = document.getElementById('overlayMenu');
    const closeOverlay = document.getElementById('closeOverlay');

    const initialStep = document.getElementById('initialStep');
    const rootStep = document.getElementById('rootStep');
    const typeStep = document.getElementById('typeStep');
    const positionStep = document.getElementById('positionStep');

    const selectRootNote = document.getElementById('selectRootNote');
    const selectType = document.getElementById('selectType');
    const selectPosition = document.getElementById('selectPosition');

    const backToInitialFromRoot = document.getElementById('backToInitialFromRoot');
    const backToInitialFromType = document.getElementById('backToInitialFromType');
    const backToInitialFromPosition = document.getElementById('backToInitialFromPosition');

    // Default URL parameters
    let urlParams = {
        models_select: '1',
        root: '4',
        notes_options_select: '1',
        position_select: '0'
    };

    // Ensure the overlay menu is hidden initially
    overlayMenu.style.display = 'none';

    overlayToggle.addEventListener('click', function() {
        overlayMenu.style.display = 'flex';
        initialStep.classList.add('active');
    });

    closeOverlay.addEventListener('click', function() {
        overlayMenu.style.display = 'none';
        resetSteps();
    });

    selectRootNote.addEventListener('click', function() {
        initialStep.classList.remove('active');
        rootStep.classList.add('active');
    });

    selectType.addEventListener('click', function() {
        initialStep.classList.remove('active');
        typeStep.classList.add('active');
    });

    selectPosition.addEventListener('click', function() {
        initialStep.classList.remove('active');
        positionStep.classList.add('active');
    });

    backToInitialFromRoot.addEventListener('click', function() {
        rootStep.classList.remove('active');
        initialStep.classList.add('active');
    });

    backToInitialFromType.addEventListener('click', function() {
        typeStep.classList.remove('active');
        initialStep.classList.add('active');
    });

    backToInitialFromPosition.addEventListener('click', function() {
        positionStep.classList.remove('active');
        initialStep.classList.add('active');
    });

    document.querySelectorAll('.grid-item').forEach(item => {
        item.addEventListener('click', function() {
            const value = this.getAttribute('data-value');
            const step = this.closest('.step').id;

            if (step === 'rootStep') {
                urlParams.root = value;
                submitForm();
            } else if (step === 'typeStep') {
                urlParams.notes_options_select = value;
                submitForm();
            } else if (step === 'positionStep') {
                urlParams.position_select = value;
                submitForm();
            }
        });
    });

    function submitForm() {
        const form = document.createElement('form');
        form.method = 'GET';
        form.action = '';

        for (const key in urlParams) {
            const input = document.createElement('input');
            input.type = 'hidden';
            input.name = key;
            input.value = urlParams[key];
            form.appendChild(input);
        }

        document.body.appendChild(form);
        form.submit();
    }

    function resetSteps() {
        initialStep.classList.remove('active');
        rootStep.classList.remove('active');
        typeStep.classList.remove('active');
        positionStep.classList.remove('active');
    }

    // Optional: Close overlay when clicking outside the content
    overlayMenu.addEventListener('click', function(event) {
        if (event.target === overlayMenu) {
            overlayMenu.style.display = 'none';
            resetSteps();
        }
    });
}

document.addEventListener('DOMContentLoaded', function() {
      initializeOverlayMenu();
});