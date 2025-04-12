document.addEventListener('DOMContentLoaded', function() {
    // Get all the fret cells
    const fretCells = document.querySelectorAll('.fretboard .fret');
    
    // Find the fretboard container
    const fretboard = document.querySelector('.fretboard');
    
    // Create a container for the inlays
    const inlayContainer = document.createElement('div');
    inlayContainer.className = 'inlay-container';
    inlayContainer.style.position = 'absolute';
    inlayContainer.style.top = '0';
    inlayContainer.style.left = '0';
    inlayContainer.style.width = '100%';
    inlayContainer.style.height = '100%';
    inlayContainer.style.pointerEvents = 'none';
    inlayContainer.style.zIndex = '1';
    
    // Functions to add inlays
    function addInlay(fretNumber, position) {
        // Find the fret cell
        let targetFret = null;
        
        // Find G string cells by checking if it has 'gString' in class name
        let gStringCells = Array.from(fretCells).filter(cell => 
            cell.className.includes('gString')
        );
        
        // Find the right fret on G string
        if (gStringCells.length > 0) {
            targetFret = gStringCells.find(cell => 
                cell.className.includes(fretNumber)
            );
        }
        
        if (targetFret) {
            // Create inlay dot
            const inlay = document.createElement('div');
            inlay.className = 'fret-inlay';
            inlay.style.position = 'absolute';
            inlay.style.width = '8px';
            inlay.style.height = '8px';
            inlay.style.backgroundColor = '#cacbcb';
            inlay.style.borderRadius = '50%';
            
            // Position the inlay relative to the targetFret
            const rect = targetFret.getBoundingClientRect();
            const boardRect = fretboard.getBoundingClientRect();
            
            inlay.style.left = `${rect.left - boardRect.left + rect.width/2}px`;
            inlay.style.top = `${rect.top - boardRect.top + rect.height/2}px`;
            inlay.style.transform = 'translate(-50%, -50%)';
            
            // Add the inlay to the container
            inlayContainer.appendChild(inlay);
        }
    }
    
    function addDoubleDot(fretNumber) {
        // Find D string for upper dot
        let dStringCells = Array.from(fretCells).filter(cell => 
            cell.className.includes('dString')
        );
        
        // Find the right fret on D string
        let upperTargetFret = null;
        if (dStringCells.length > 0) {
            upperTargetFret = dStringCells.find(cell => 
                cell.className.includes(fretNumber)
            );
        }
        
        // Find A string for lower dot
        let aStringCells = Array.from(fretCells).filter(cell => 
            cell.className.includes('AString')
        );
        
        // Find the right fret on A string
        let lowerTargetFret = null;
        if (aStringCells.length > 0) {
            lowerTargetFret = aStringCells.find(cell => 
                cell.className.includes(fretNumber)
            );
        }
        
        if (upperTargetFret) {
            // Create upper inlay dot
            const upperInlay = document.createElement('div');
            upperInlay.className = 'fret-inlay';
            upperInlay.style.position = 'absolute';
            upperInlay.style.width = '8px';
            upperInlay.style.height = '8px';
            upperInlay.style.backgroundColor = '#cacbcb';
            upperInlay.style.borderRadius = '50%';
            
            // Position the inlay
            const rect = upperTargetFret.getBoundingClientRect();
            const boardRect = fretboard.getBoundingClientRect();
            
            upperInlay.style.left = `${rect.left - boardRect.left + rect.width/2}px`;
            upperInlay.style.top = `${rect.top - boardRect.top + rect.height/2}px`;
            upperInlay.style.transform = 'translate(-50%, -50%)';
            
            // Add the inlay to the container
            inlayContainer.appendChild(upperInlay);
        }
        
        if (lowerTargetFret) {
            // Create lower inlay dot
            const lowerInlay = document.createElement('div');
            lowerInlay.className = 'fret-inlay';
            lowerInlay.style.position = 'absolute';
            lowerInlay.style.width = '8px';
            lowerInlay.style.height = '8px';
            lowerInlay.style.backgroundColor = '#cacbcb';
            lowerInlay.style.borderRadius = '50%';
            
            // Position the inlay
            const rect = lowerTargetFret.getBoundingClientRect();
            const boardRect = fretboard.getBoundingClientRect();
            
            lowerInlay.style.left = `${rect.left - boardRect.left + rect.width/2}px`;
            lowerInlay.style.top = `${rect.top - boardRect.top + rect.height/2}px`;
            lowerInlay.style.transform = 'translate(-50%, -50%)';
            
            // Add the inlay to the container
            inlayContainer.appendChild(lowerInlay);
        }
    }
    
    // Add the inlay container to the fretboard
    if (fretboard) {
        fretboard.appendChild(inlayContainer);
        
        // Add the inlays
        setTimeout(() => {
            addInlay('three', 'middle');
            addInlay('five', 'middle');
            addInlay('seven', 'middle');
            addInlay('nine', 'middle');
            addDoubleDot('twelve');
            addInlay('fifteen', 'middle');
            addInlay('seventeen', 'middle');
        }, 100); // Small delay to ensure the DOM is fully rendered
    }
});
