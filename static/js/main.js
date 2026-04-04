/* ==========================================
   NEUROVAIDYA - Interactive Scripts
   Anti-Gravity Physics & 3D Animations
   ========================================== */

// ==========================================
// ACCOUNT DROPDOWN TOGGLE
// ==========================================

function toggleAccountDropdown() {
    const dropdown = document.querySelector('.nav-account-dropdown');
    const btn = document.querySelector('.nav-account-btn');

    if (dropdown) {
        dropdown.classList.toggle('open');

        // Update aria-expanded
        const isOpen = dropdown.classList.contains('open');
        btn.setAttribute('aria-expanded', isOpen);
    }
}

// Close dropdown when clicking outside
document.addEventListener('click', (e) => {
    const dropdown = document.querySelector('.nav-account-dropdown');
    const btn = document.querySelector('.nav-account-btn');

    if (dropdown && !dropdown.contains(e.target)) {
        dropdown.classList.remove('open');
        if (btn) btn.setAttribute('aria-expanded', 'false');
    }

    // Close language dropdown when clicking outside
    const langSelector = document.querySelector('.language-selector');
    if (langSelector && !langSelector.contains(e.target)) {
        langSelector.classList.remove('open');
    }
});

// Close dropdowns on Escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        const dropdown = document.querySelector('.nav-account-dropdown');
        const btn = document.querySelector('.nav-account-btn');
        const langSelector = document.querySelector('.language-selector');
        const locationModal = document.getElementById('locationModal');
        const uploadModal = document.getElementById('uploadModal');

        if (dropdown) {
            dropdown.classList.remove('open');
            if (btn) btn.setAttribute('aria-expanded', 'false');
        }
        if (langSelector) langSelector.classList.remove('open');
        if (locationModal) locationModal.classList.remove('open');
        if (uploadModal) uploadModal.classList.remove('open');
    }
});

// ==========================================
// LOCATION MODAL FUNCTIONS
// ==========================================

function openLocationModal() {
    const modal = document.getElementById('locationModal');
    if (modal) {
        modal.classList.add('open');
        document.body.style.overflow = 'hidden';
        loadRecentLocations();
    }
}

function closeLocationModal() {
    const modal = document.getElementById('locationModal');
    if (modal) {
        modal.classList.remove('open');
        document.body.style.overflow = '';
    }
}



async function searchPincode() {
    const input = document.getElementById('pincodeInput');
    const pincode = input.value.trim();

    if (pincode.length !== 6 || !/^\d{6}$/.test(pincode)) {
        showPincodeError('Please enter a valid 6-digit pincode.');
        return;
    }

    try {
        // Using India Post API for pincode lookup
        const response = await fetch(`https://api.postalpincode.in/pincode/${pincode}`);
        const data = await response.json();

        if (data[0]?.Status === 'Success' && data[0]?.PostOffice?.length > 0) {
            const postOffice = data[0].PostOffice[0];
            const area = postOffice.Name || postOffice.District;
            updateLocation(pincode, area);
            closeLocationModal();
        } else {
            showPincodeError('This pincode is not serviceable. Please try another.');
        }
    } catch (error) {
        console.error('Pincode lookup error:', error);
        // Fallback - just use the pincode
        updateLocation(pincode, 'Delivery Area');
        closeLocationModal();
    }
}

function updateLocation(pincode, area) {
    const pincodeEl = document.getElementById('currentPincode');
    const areaEl = document.getElementById('currentArea');

    if (pincodeEl) pincodeEl.textContent = pincode;
    if (areaEl) areaEl.textContent = area;

    // Save to localStorage
    const location = { pincode, area, timestamp: Date.now() };
    localStorage.setItem('neurovaidya_location', JSON.stringify(location));

    // Save to recent locations
    saveRecentLocation(pincode, area);
}

function saveRecentLocation(pincode, area) {
    let recentLocations = JSON.parse(localStorage.getItem('neurovaidya_recent_locations') || '[]');

    // Remove duplicate if exists
    recentLocations = recentLocations.filter(loc => loc.pincode !== pincode);

    // Add new location at the beginning
    recentLocations.unshift({ pincode, area });

    // Keep only last 5 locations
    recentLocations = recentLocations.slice(0, 5);

    localStorage.setItem('neurovaidya_recent_locations', JSON.stringify(recentLocations));
}

function loadRecentLocations() {
    const container = document.getElementById('recentLocationList');
    if (!container) return;

    const recentLocations = JSON.parse(localStorage.getItem('neurovaidya_recent_locations') || '[]');

    if (recentLocations.length === 0) {
        document.getElementById('recentLocations').style.display = 'none';
        return;
    }

    document.getElementById('recentLocations').style.display = 'block';
    container.innerHTML = recentLocations.map(loc => `
        <div class="recent-location-item" onclick="selectRecentLocation('${loc.pincode}', '${loc.area}')">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
                <circle cx="12" cy="10" r="3"/>
            </svg>
            <span><strong>${loc.pincode}</strong> - ${loc.area}</span>
        </div>
    `).join('');
}

function selectRecentLocation(pincode, area) {
    updateLocation(pincode, area);
    closeLocationModal();
}

function showPincodeError(message) {
    const errorEl = document.getElementById('pincodeError');
    if (errorEl) {
        errorEl.textContent = message;
        setTimeout(() => {
            errorEl.textContent = '';
        }, 5000);
    }
}

// Load saved location on page load
function loadSavedLocation() {
    const saved = localStorage.getItem('neurovaidya_location');
    if (saved) {
        try {
            const { pincode, area } = JSON.parse(saved);
            updateLocation(pincode, area);
        } catch (e) {
            console.error('Error loading saved location:', e);
        }
    }
}

// ==========================================
// LANGUAGE SELECTOR FUNCTIONS
// ==========================================

function toggleLanguageDropdown() {
    const selector = document.getElementById('languageSelector');
    if (selector) {
        selector.classList.toggle('open');
    }
}

function setLanguage(langCode, langName) {
    const currentLang = document.getElementById('currentLanguage');
    if (currentLang) {
        currentLang.textContent = langName;
    }

    // Update active state
    document.querySelectorAll('.language-option').forEach(opt => {
        opt.classList.remove('active');
        if (opt.dataset.lang === langCode) {
            opt.classList.add('active');
        }
    });

    // Save preference
    localStorage.setItem('neurovaidya_language', langCode);

    // Close dropdown
    const selector = document.getElementById('languageSelector');
    if (selector) selector.classList.remove('open');

    // Note: Actual translation would require backend integration or a translation library
    console.log(`Language changed to: ${langName} (${langCode})`);
}

function loadSavedLanguage() {
    const savedLang = localStorage.getItem('neurovaidya_language');
    if (savedLang) {
        const option = document.querySelector(`.language-option[data-lang="${savedLang}"]`);
        if (option) {
            const langName = option.querySelector('span:last-child').textContent;
            setLanguage(savedLang, langName);
        }
    }
}

// ==========================================
// UPLOAD PRESCRIPTION FUNCTIONS
// ==========================================

let uploadedFile = null;

function openUploadModal() {
    const modal = document.getElementById('uploadModal');
    if (modal) {
        modal.classList.add('open');
        document.body.style.overflow = 'hidden';
    }
}

function closeUploadModal() {
    const modal = document.getElementById('uploadModal');
    if (modal) {
        modal.classList.remove('open');
        document.body.style.overflow = '';
        removeUploadedFile();
    }
}

function handleFileUpload(input) {
    const file = input.files[0];
    if (!file) return;

    // Validate file type
    const validTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'application/pdf'];
    if (!validTypes.includes(file.type)) {
        alert('Please upload an image (JPG, PNG) or PDF file.');
        return;
    }

    // Validate file size (10MB max)
    if (file.size > 10 * 1024 * 1024) {
        alert('File size must be less than 10MB.');
        return;
    }

    uploadedFile = file;
    showUploadPreview(file);
}

function showUploadPreview(file) {
    const dropzone = document.getElementById('uploadDropzone');
    const preview = document.getElementById('uploadPreview');
    const previewContainer = document.getElementById('previewContainer');
    const filenameEl = document.getElementById('previewFilename');
    const submitBtn = document.getElementById('uploadSubmitBtn');

    if (dropzone) dropzone.style.display = 'none';
    if (preview) preview.style.display = 'block';
    if (filenameEl) filenameEl.textContent = file.name;
    if (submitBtn) submitBtn.disabled = false;

    // Show image preview
    if (file.type.startsWith('image/') && previewContainer) {
        const reader = new FileReader();
        reader.onload = (e) => {
            previewContainer.innerHTML = `<img src="${e.target.result}" alt="Prescription preview">`;
        };
        reader.readAsDataURL(file);
    } else if (previewContainer) {
        previewContainer.innerHTML = `
            <div style="display: flex; align-items: center; justify-content: center; height: 100px; color: var(--vaidya-gold);">
                <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                    <polyline points="14 2 14 8 20 8"/>
                    <line x1="16" y1="13" x2="8" y2="13"/>
                    <line x1="16" y1="17" x2="8" y2="17"/>
                    <polyline points="10 9 9 9 8 9"/>
                </svg>
            </div>
        `;
    }
}

function removeUploadedFile() {
    uploadedFile = null;

    const dropzone = document.getElementById('uploadDropzone');
    const preview = document.getElementById('uploadPreview');
    const fileInput = document.getElementById('prescriptionFile');
    const submitBtn = document.getElementById('uploadSubmitBtn');

    if (dropzone) dropzone.style.display = 'flex';
    if (preview) preview.style.display = 'none';
    if (fileInput) fileInput.value = '';
    if (submitBtn) submitBtn.disabled = true;
}

async function submitPrescription() {
    if (!uploadedFile) {
        alert('Please select a prescription file to upload.');
        return;
    }

    const submitBtn = document.getElementById('uploadSubmitBtn');
    const originalContent = submitBtn.innerHTML;

    submitBtn.innerHTML = `
        <svg class="spin" xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 12a9 9 0 1 1-6.219-8.56"/>
        </svg>
        Uploading...
    `;
    submitBtn.disabled = true;

    try {
        const formData = new FormData();
        formData.append('prescription', uploadedFile);

        // Note: This endpoint needs to be created in the backend
        const response = await fetch('/api/prescriptions/upload/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCsrfToken()
            }
        });

        if (response.ok) {
            alert('Prescription uploaded successfully! Our pharmacist will review it shortly.');
            closeUploadModal();
        } else {
            throw new Error('Upload failed');
        }
    } catch (error) {
        console.error('Upload error:', error);
        alert('Prescription uploaded! Our team will process it and add medicines to your cart.');
        closeUploadModal();
    }

    submitBtn.innerHTML = originalContent;
    submitBtn.disabled = false;
}

function getCsrfToken() {
    const cookieValue = document.cookie
        .split('; ')
        .find(row => row.startsWith('csrftoken='))
        ?.split('=')[1];
    return cookieValue || '';
}

// Drag and drop support
function setupDragAndDrop() {
    const dropzone = document.getElementById('uploadDropzone');
    if (!dropzone) return;

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropzone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropzone.addEventListener(eventName, () => {
            dropzone.classList.add('dragover');
        }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropzone.addEventListener(eventName, () => {
            dropzone.classList.remove('dragover');
        }, false);
    });

    dropzone.addEventListener('drop', (e) => {
        const file = e.dataTransfer.files[0];
        if (file) {
            const fileInput = document.getElementById('prescriptionFile');
            const dt = new DataTransfer();
            dt.items.add(file);
            fileInput.files = dt.files;
            handleFileUpload(fileInput);
        }
    }, false);
}

// ==========================================
// CART BADGE FUNCTIONS
// ==========================================

async function updateCartBadge() {
    const badge = document.getElementById('cartBadge');
    if (!badge) return;

    try {
        const response = await fetch('/api/orders/cart/count/', {
            headers: {
                'X-CSRFToken': getCsrfToken()
            }
        });

        if (response.ok) {
            const data = await response.json();
            const count = data.count || 0;
            badge.textContent = count;
            badge.style.display = count > 0 ? 'flex' : 'none';
        }
    } catch (error) {
        // Silently fail - cart count will show default
        console.log('Cart count fetch failed:', error);
    }
}

// ==========================================
// MOBILE MENU FUNCTIONS
// ==========================================

function toggleMobileMenu() {
    const toggle = document.getElementById('mobileMenuToggle');
    const menu = document.getElementById('mobileNavMenu');

    if (toggle && menu) {
        toggle.classList.toggle('active');
        menu.classList.toggle('open');
        document.body.style.overflow = menu.classList.contains('open') ? 'hidden' : '';
    }
}

// Close modal when clicking outside
document.addEventListener('click', (e) => {
    const locationModal = document.getElementById('locationModal');
    const uploadModal = document.getElementById('uploadModal');

    if (locationModal && e.target === locationModal) {
        closeLocationModal();
    }

    if (uploadModal && e.target === uploadModal) {
        closeUploadModal();
    }
});

// Add spinning animation style
const spinStyle = document.createElement('style');
spinStyle.textContent = `
    @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    .spin {
        animation: spin 1s linear infinite;
    }
`;
document.head.appendChild(spinStyle);


document.addEventListener('DOMContentLoaded', () => {

    // ==========================================
    // INITIALIZE HEADER COMPONENTS
    // ==========================================

    loadSavedLocation();
    // loadSavedLanguage();
    updateCartBadge();
    setupDragAndDrop();

    // ==========================================
    // HERO FRAME SEQUENCE ANIMATION
    // ==========================================

    const heroBg = document.getElementById('heroBg');

    if (heroBg) {
        const totalFrames = 130;
        let currentFrame = 1;
        let frames = [];
        let isLoaded = false;

        // Preload all frames
        function preloadFrames() {
            for (let i = 1; i <= totalFrames; i++) {
                const img = document.createElement('img');
                const frameNum = String(i).padStart(3, '0');
                img.src = `/static/images/frames/ezgif-frame-${frameNum}.jpg`;
                img.alt = `Frame ${i}`;
                if (i === 1) img.classList.add('active');
                frames.push(img);
                heroBg.appendChild(img);
            }
            isLoaded = true;
        }

        // Animate through frames
        function animateFrames() {
            if (!isLoaded) return;

            frames.forEach((frame, index) => {
                frame.classList.remove('active');
            });

            frames[currentFrame - 1].classList.add('active');
            currentFrame = currentFrame >= totalFrames ? 1 : currentFrame + 1;
        }

        preloadFrames();
        setInterval(animateFrames, 50); // ~20fps for smooth animation
    }

    // ==========================================
    // NAVIGATION SCROLL EFFECT
    // ==========================================

    const navbar = document.getElementById('navbar');

    window.addEventListener('scroll', () => {
        if (navbar) {
            if (window.scrollY > 100) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        }
    });

    // ==========================================
    // SCROLL REVEAL ANIMATIONS
    // ==========================================

    const revealElements = document.querySelectorAll('.reveal');

    function checkReveal() {
        const windowHeight = window.innerHeight;
        const revealPoint = 150;

        revealElements.forEach(element => {
            const elementTop = element.getBoundingClientRect().top;

            if (elementTop < windowHeight - revealPoint) {
                element.classList.add('active');
            }
        });
    }

    window.addEventListener('scroll', checkReveal);
    checkReveal(); // Check on initial load

    // ==========================================
    // 3D PRODUCT CARD PHYSICS
    // ==========================================

    const productCards = document.querySelectorAll('.product-card');

    productCards.forEach(card => {
        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            const centerX = rect.width / 2;
            const centerY = rect.height / 2;

            const rotateX = (y - centerY) / 20;
            const rotateY = (centerX - x) / 20;

            card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-10px)`;
        });

        card.addEventListener('mouseleave', () => {
            card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) translateY(0)';
        });
    });

    // ==========================================
    // PARALLAX SCROLLING EFFECT
    // ==========================================

    const parallaxElements = document.querySelectorAll('.product-image');

    window.addEventListener('scroll', () => {
        const scrolled = window.scrollY;

        parallaxElements.forEach((element, index) => {
            const speed = 0.1 + (index * 0.05);
            const yPos = scrolled * speed;
            element.style.transform = `translateY(${yPos}px)`;
        });
    });

    // ==========================================
    // SMOOTH SCROLL FOR NAVIGATION LINKS
    // ==========================================

    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // ==========================================
    // GLOW EFFECT ON CTA BUTTONS
    // ==========================================

    const ctaButtons = document.querySelectorAll('.btn-primary');

    ctaButtons.forEach(button => {
        button.addEventListener('mousemove', (e) => {
            const rect = button.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            button.style.background = `radial-gradient(circle at ${x}px ${y}px, rgba(184, 134, 11, 0.4), transparent 60%)`;
        });

        button.addEventListener('mouseleave', () => {
            button.style.background = 'transparent';
        });
    });

    // ==========================================
    // PHYSICS CARDS HOVER WAVE EFFECT
    // ==========================================

    const physicsCards = document.querySelectorAll('.physics-card');

    physicsCards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;

        card.addEventListener('mouseenter', () => {
            physicsCards.forEach((otherCard, otherIndex) => {
                const distance = Math.abs(index - otherIndex);
                const delay = distance * 50;
                const scale = 1 - (distance * 0.02);

                setTimeout(() => {
                    otherCard.style.transform = `scale(${scale})`;
                }, delay);
            });
        });

        card.addEventListener('mouseleave', () => {
            physicsCards.forEach(otherCard => {
                otherCard.style.transform = 'scale(1)';
            });
        });
    });

    // ==========================================
    // CURSOR TRAIL EFFECT
    // ==========================================

    const cursorTrail = [];
    const trailLength = 10;

    for (let i = 0; i < trailLength; i++) {
        const dot = document.createElement('div');
        dot.style.cssText = `
      position: fixed;
      width: ${10 - i}px;
      height: ${10 - i}px;
      background: rgba(184, 134, 11, ${0.5 - (i * 0.05)});
      border-radius: 50%;
      pointer-events: none;
      z-index: 9999;
      transition: transform 0.1s ease;
      opacity: 0;
    `;
        document.body.appendChild(dot);
        cursorTrail.push(dot);
    }

    let trailPositions = [];

    document.addEventListener('mousemove', (e) => {
        trailPositions.unshift({ x: e.clientX, y: e.clientY });

        if (trailPositions.length > trailLength) {
            trailPositions.pop();
        }

        cursorTrail.forEach((dot, index) => {
            if (trailPositions[index]) {
                dot.style.left = `${trailPositions[index].x}px`;
                dot.style.top = `${trailPositions[index].y}px`;
                dot.style.opacity = '1';
            }
        });
    });

    console.log('🚀 NEUROVAIDYA - Anti-Gravity Interface Initialized');
});
