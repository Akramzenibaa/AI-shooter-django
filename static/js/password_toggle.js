// Password Toggle Functionality
// This script adds eye icon toggle to all password fields

document.addEventListener('DOMContentLoaded', function () {
    // Find all password input fields
    const passwordFields = document.querySelectorAll('input[type=\"password\"]');

    passwordFields.forEach(function (field) {
        // Skip if already has toggle
        if (field.parentElement.classList.contains('password-wrapper')) {
            return;
        }

        // Create wrapper
        const wrapper = document.createElement('div');
        wrapper.className = 'password-wrapper';
        wrapper.style.position = 'relative';

        // Move field into wrapper
        field.parentNode.insertBefore(wrapper, field);
        wrapper.appendChild(field);

        // Create toggle button
        const toggleBtn = document.createElement('button');
        toggleBtn.type = 'button';
        toggleBtn.className = 'password-toggle';
        toggleBtn.setAttribute('aria-label', 'Toggle password visibility');
        toggleBtn.innerHTML = '<i data-lucide=\"eye\" class=\"eye-icon\"></i>';

        wrapper.appendChild(toggleBtn);

        // Toggle functionality
        toggleBtn.addEventListener('click', function () {
            const type = field.getAttribute('type') === 'password' ? 'text' : 'password';
            field.setAttribute('type', type);

            // Update icon
            const icon = type === 'password' ? 'eye' : 'eye-off';
            toggleBtn.innerHTML = `<i data-lucide=\"${icon}\" class=\"eye-icon\"></i>`;

            // Reinitialize lucide icons
            if (typeof lucide !== 'undefined') {
                lucide.createIcons();
            }
        });
    });

    // Initialize lucide icons
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
});
