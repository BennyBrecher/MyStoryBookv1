const fileInput = document.getElementById('faceUpload');
const uploadZone = document.getElementById('uploadZone');
const previewContainer = document.getElementById('previewContainer');
const previewImage = document.getElementById('previewImage');
const storySelection = document.getElementById('storySelection');
const characterDetails = document.getElementById('characterDetails');
const generateSection = document.getElementById('generateSection');
const storyForm = document.getElementById('storyForm');

// Handle file selection
fileInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = (event) => {
            previewImage.src = event.target.result;
            previewContainer.classList.add('active');
            
            // Show story selection after 500ms
            setTimeout(() => {
                storySelection.classList.add('active');
            }, 500);
        };
        reader.readAsDataURL(file);
    }
});

// Watch for story selection
document.querySelectorAll('input[name="story"]').forEach(radio => {
    radio.addEventListener('change', () => {
        setTimeout(() => {
            characterDetails.classList.add('active');
        }, 300);
    });
});

// Watch for name input and gender selection
const nameInput = document.getElementById('childName');
const genderRadios = document.querySelectorAll('input[name="gender"]');

function checkFormComplete() {
    if (nameInput.value.trim() !== '' && 
        document.querySelector('input[name="gender"]:checked')) {
        generateSection.classList.add('active');
    }
}

nameInput.addEventListener('input', checkFormComplete);
genderRadios.forEach(radio => {
    radio.addEventListener('change', checkFormComplete);
});

/* Form submission
storyForm.addEventListener('submit', (e) => {
    e.preventDefault();
    
    const formData = new FormData(storyForm);
    console.log('Form submitted with:');
    console.log('Story:', formData.get('story'));
    console.log('Name:', formData.get('child_name'));
    console.log('Gender:', formData.get('gender'));
    console.log('Image:', formData.get('face_image').name);
    
    //Send to backend
    //alert('Form ready to submit! Check console for data.');

    fetch('/generate_story', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(`Story generated! Check the directory: ${data.output_directory}`);
        } else {
            alert(`Error: ${data.error}`);
        }
    })
    .catch(error => console.error('Error:', error));
}); */

storyForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const formData = new FormData(storyForm);
    
    // Disable button and show loading
    const btn = document.querySelector('.generate-btn');
    btn.disabled = true;
    btn.innerHTML = '<span class="btn-text">Creating your book... ⏳</span>';
    
    fetch('/generate_story', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            // Error response - parse JSON
            return response.json().then(err => { 
                throw new Error(err.error || 'Unknown error'); 
            });
        }
        // Success response - it's a PDF blob
        return response.blob();
    })
    .then(blob => {
        // Download the PDF
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${formData.get('child_name')}_storybook.pdf`;
        document.body.appendChild(a); // Safari needs this
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        // Success message
        btn.innerHTML = '<span class="btn-sparkle">🎉</span><span class="btn-text">Done! Check Downloads</span><span class="btn-sparkle">🎉</span>';
        btn.disabled = false;
        
        // Optional: reload after 3 seconds
        setTimeout(() => location.reload(), 3000);
    })
    .catch(error => {
        alert('Error: ' + error.message);
        btn.disabled = false;
        btn.innerHTML = '<span class="btn-sparkle">✨</span><span class="btn-text">Create My Story!</span><span class="btn-sparkle">✨</span>';
    });
});


// Drag and drop
uploadZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadZone.style.borderColor = '#ffd700';
    uploadZone.style.transform = 'rotate(0deg) scale(1.05)';
});

uploadZone.addEventListener('dragleave', () => {
    uploadZone.style.borderColor = '#ff6b9d';
    uploadZone.style.transform = 'rotate(-1deg)';
});

uploadZone.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadZone.style.borderColor = '#ff6b9d';
    uploadZone.style.transform = 'rotate(-1deg)';
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        fileInput.files = files;
        const event = new Event('change');
        fileInput.dispatchEvent(event);
    }
});