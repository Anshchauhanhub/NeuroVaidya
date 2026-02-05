document.addEventListener('DOMContentLoaded', () => {
    const uploadArea = document.getElementById('upload-area');
    const fileInput = document.getElementById('file-input');
    const previewArea = document.getElementById('preview-area');
    const imagePreview = document.getElementById('image-preview');
    const resultsArea = document.getElementById('results-area');
    const resetBtn = document.getElementById('reset-btn');

    const conditionName = document.getElementById('condition-name');
    const severityFill = document.getElementById('severity-fill');
    const severityText = document.getElementById('severity-text');
    const recommendationList = document.getElementById('recommendation-list');

    // Mock Data for Demo
    const mockConditions = [
        {
            name: "Eczema (Atopic Dermatitis)",
            severity: "Moderate",
            score: 65,
            color: "#fbbf24", // Amber
            recommendations: [
                "Apply fragrance-free moisturizer twice daily.",
                "Use a mild, soap-free cleanser.",
                "Avoid known triggers like wool or synthetic fabrics."
            ]
        },
        {
            name: "Acne Vulgaris",
            severity: "Mild",
            score: 30,
            color: "#34d399", // Green
            recommendations: [
                "Use a gentle cleanser with salicylic acid.",
                "Avoid touching your face.",
                "Consider a non-comedogenic moisturizer."
            ]
        },
        {
            name: "Psoriasis",
            severity: "High",
            score: 85,
            color: "#ef4444", // Red
            recommendations: [
                "Consult a dermatologist mainly.",
                "Apply prescribed topical corticosteroids.",
                "Keep skin moisturized to reduce scaling."
            ]
        }
    ];

    // Drag and Drop Events
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        uploadArea.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, unhighlight, false);
    });

    function highlight(e) {
        uploadArea.classList.add('drag-over');
    }

    function unhighlight(e) {
        uploadArea.classList.remove('drag-over');
    }

    uploadArea.addEventListener('drop', handleDrop, false);

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFiles(files);
    }

    fileInput.addEventListener('change', function () {
        handleFiles(this.files);
    });

    function handleFiles(files) {
        if (files.length > 0) {
            const file = files[0];
            if (file.type.startsWith('image/')) {
                const reader = new FileReader();
                reader.onload = function (e) {
                    startAnalysis(e.target.result);
                }
                reader.readAsDataURL(file);
            } else {
                alert("Please upload an image file.");
            }
        }
    }

    function startAnalysis(imageSrc) {
        // Hide Upload, Show Preview
        uploadArea.classList.add('hidden');
        previewArea.classList.remove('hidden');
        imagePreview.src = imageSrc;

        // Simulate Scanning process (3 seconds)
        setTimeout(() => {
            showResults();
        }, 3000);
    }

    function showResults() {
        previewArea.classList.add('hidden');
        resultsArea.classList.remove('hidden');

        // Randomize Result for Demo
        const result = mockConditions[Math.floor(Math.random() * mockConditions.length)];

        conditionName.textContent = result.name;
        severityText.textContent = result.severity;

        // Populate recommendations
        recommendationList.innerHTML = '';
        result.recommendations.forEach(rec => {
            const li = document.createElement('li');
            li.textContent = rec;
            recommendationList.appendChild(li);
        });

        // Animate progress bar
        setTimeout(() => {
            severityFill.style.width = `${result.score}%`;
            severityFill.style.backgroundColor = result.color;
        }, 100);
    }

    resetBtn.addEventListener('click', () => {
        resultsArea.classList.add('hidden');
        previewArea.classList.add('hidden');
        uploadArea.classList.remove('hidden');

        // Reset file input
        fileInput.value = '';
        severityFill.style.width = '0%';
    });
});
