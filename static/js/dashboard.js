document.addEventListener('DOMContentLoaded', () => {
    // Elements
    const dropzone = document.getElementById('dropzone');
    const imageInput = document.getElementById('image-input');
    const previewImg = document.getElementById('preview-img');
    const dropzoneContent = document.getElementById('dropzone-content');
    const generateBtn = document.getElementById('generate-btn');

    const deductMsg = document.getElementById('deduct-msg');
    const errorMsg = document.getElementById('error-msg');
    const statusMsg = document.getElementById('status-msg');
    const generatingCard = document.getElementById('generating-card');
    const resultsCard = document.getElementById('results-card');
    const resultsGallery = document.getElementById('results-gallery');
    const getMoreBtn = document.getElementById('getmore-btn');
    const getMorePanel = document.getElementById('getmore-panel');

    let selectedFile = null;
    let imgCount = 4;

    // Toggle Get More panel
    if (getMoreBtn) {
        getMoreBtn.addEventListener('click', () => {
            getMorePanel.style.display = getMorePanel.style.display === 'none' ? 'block' : 'none';
        });
    }

    // Handle Option Selection (Count)
    const countOpts = document.querySelectorAll('.count-opt');
    countOpts.forEach(opt => {
        opt.addEventListener('click', () => {
            countOpts.forEach(o => o.classList.remove('selected'));
            opt.classList.add('selected');
            imgCount = parseInt(opt.dataset.count);
            deductMsg.textContent = `Cost: ${imgCount} credits`;
        });
    });

    // Handle Mode Selection
    let selectedMode = 'creative';
    const modeOpts = document.querySelectorAll('.mode-opt');
    modeOpts.forEach(opt => {
        opt.addEventListener('click', () => {
            modeOpts.forEach(o => o.classList.remove('selected'));
            opt.classList.add('selected');
            selectedMode = opt.dataset.mode;
        });
    });

    // Handle Dropzone clicks
    dropzone.addEventListener('click', () => {
        if (generatingCard.style.display === 'block') return;
        imageInput.click();
    });


    // Handle File Change
    imageInput.addEventListener('change', (e) => {
        if (generatingCard.style.display === 'block') return;
        const file = e.target.files[0];
        if (file) {
            selectedFile = file;
            const reader = new FileReader();
            reader.onload = (event) => {
                previewImg.src = event.target.result;
                previewImg.style.display = 'block';
                dropzoneContent.style.display = 'none';
                generateBtn.disabled = false;
            };
            reader.readAsDataURL(file);
        }
    });

    // Handle Generation
    generateBtn.addEventListener('click', async () => {
        // Authenticated check
        const isAuthenticated = generateBtn.dataset.authenticated === 'true';
        if (!isAuthenticated) {
            const loginUrl = generateBtn.dataset.loginUrl || '/accounts/login/';
            window.location.href = loginUrl;
            return;
        }

        if (!selectedFile) {
            errorMsg.textContent = "Please upload an image first!";
            errorMsg.style.display = 'block';
            return;
        }
        if (generateBtn.disabled) return;

        console.log("Generation started...");

        // Reset UI
        errorMsg.style.display = 'none';
        statusMsg.textContent = 'Please wait...';

        // Disable UI
        generateBtn.disabled = true;
        generateBtn.textContent = 'Generating...';
        dropzone.style.pointerEvents = 'none';
        dropzone.style.opacity = '0.7';

        generatingCard.style.display = 'block';
        // resultsCard is no longer hidden here, keeping previous results visible


        const userPrompt = document.getElementById('user-prompt').value;
        const formData = new FormData();
        formData.append('image', selectedFile);
        formData.append('count', imgCount);
        formData.append('mode', selectedMode);
        formData.append('user_prompt', userPrompt);

        try {
            const response = await fetch('/images/generate/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: formData
            });

            const data = await response.json();

            if (response.ok) {
                statusMsg.textContent = 'Images generated successfully';
                generatingCard.style.display = 'none';
                resultsCard.style.display = 'block';

                // Render Gallery (Append to session history)
                data.urls.forEach(url => {
                    const wrap = document.createElement('div');
                    wrap.className = 'thumb-wrap';
                    wrap.innerHTML = `
                        <img src="${url}" alt="Generated image" loading="lazy">
                        <a href="${url}" download class="dl-icon" title="Download">
                            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="w-6 h-6">
                                <path fillRule="evenodd" d="M12 2.25a.75.75 0 01.75.75v11.69l3.22-3.22a.75.75 0 111.06 1.06l-4.5 4.5a.75.75 0 01-1.06 0l-4.5-4.5a.75.75 0 111.06-1.06l3.22 3.22V3a.75.75 0 01.75-.75zm-9 13.5a.75.75 0 01.75.75v2.25a1.5 1.5 0 001.5 1.5h13.5a1.5 1.5 0 001.5-1.5v-2.25a.75.75 0 011.5 0v2.25a3 3 0 01-3 3H4.5a3 3 0 01-3-3v-2.25a.75.75 0 01.75-.75z" clipRule="evenodd" />
                            </svg>
                        </a>
                    `;
                    resultsGallery.prepend(wrap);
                });


                // Update Credits in UI (Session)
                const creditValueEl = document.getElementById('credit-value');
                if (creditValueEl && data.new_credits !== undefined) {
                    creditValueEl.textContent = data.new_credits;
                }
            } else {
                throw new Error(data.error || 'Generation failed');
            }
        } catch (error) {
            errorMsg.textContent = error.message;
            errorMsg.style.display = 'block';
            statusMsg.textContent = '';
        } finally {
            console.log("Generation process finished. Re-enabling UI.");
            generatingCard.style.display = 'none';

            // Explicitly force re-enable
            generateBtn.disabled = false;
            generateBtn.removeAttribute('disabled');
            generateBtn.style.opacity = '1';
            generateBtn.style.filter = 'none';
            generateBtn.textContent = 'Generate';

            dropzone.style.pointerEvents = 'auto';
            dropzone.style.opacity = '1';

            // Re-check file to be sure
            if (selectedFile) {
                generateBtn.classList.remove('loading'); // Use class if needed
            }
        }
    });



    // Modal logic
    const modal = document.getElementById('image-modal');
    const modalImg = document.getElementById('modal-img');

    document.addEventListener('click', (e) => {
        if (e.target.tagName === 'IMG' && (e.target.closest('.gallery') || e.target.closest('.history-grid'))) {
            modalImg.src = e.target.src;
            modal.style.display = 'flex';
        }
    });

    modal.addEventListener('click', () => {
        modal.style.display = 'none';
    });

    // Helper: Get CSRF Cookie
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
