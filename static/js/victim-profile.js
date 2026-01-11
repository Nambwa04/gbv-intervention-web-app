document.addEventListener('DOMContentLoaded', function() {
    // Element References
    const profileContainer = document.querySelector('.profile-container');
    const sosButton = document.getElementById('sosButton');
    const safetyStatus = document.getElementById('safetyStatus');
    const uploadTrigger = document.querySelector('.upload-overlay');
    const fileInput = document.getElementById('fileInput');
    const editProfileBtn = document.getElementById('editProfileBtn');
    const editProfileModal = document.getElementById('editProfileModal');

    // SOS Button Handling
    if (sosButton) {
        sosButton.addEventListener('click', async function(e) {
            e.preventDefault();
            if (confirm('Are you sure you want to send an SOS alert? Emergency contacts will be notified immediately.')) {
                try {
                    await sendSosAlert();
                    showToast('Emergency contacts have been notified', 'success');
                } catch (error) {
                    showToast('Failed to send SOS alert', 'error');
                }
            }
        });
    }

    // Safety Status Updates
    if (safetyStatus) {
        safetyStatus.addEventListener('change', async function() {
            try {
                const response = await updateSafetyStatus(this.value);
                if (response.ok) {
                    showToast('Safety status updated', 'success');
                    updateStatusIndicator(this.value);
                } else {
                    throw new Error('Failed to update status');
                }
            } catch (error) {
                showToast('Failed to update safety status', 'error');
            }
        });
    }

    // Profile Picture Upload
    if (uploadTrigger && fileInput) {
        uploadTrigger.addEventListener('click', () => fileInput.click());
        fileInput.addEventListener('change', handleProfilePicUpload);
    }

    // Edit Profile Modal
    if (editProfileBtn && editProfileModal) {
        editProfileBtn.addEventListener('click', () => {
            editProfileModal.style.display = 'flex';
        });

        // Close modal when clicking outside
        window.addEventListener('click', (e) => {
            if (e.target === editProfileModal) {
                editProfileModal.style.display = 'none';
            }
        });
    }

    // Helper Functions
    async function sendSosAlert() {
        const response = await fetch('/victim/profile/sos', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        if (!response.ok) throw new Error('Failed to send SOS');
        return response.json();
    }

    async function updateSafetyStatus(status) {
        return fetch('/victim/profile/safety-status', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `status=${status}`
        });
    }

    async function handleProfilePicUpload(event) {
        const file = event.target.files[0];
        if (!file) return;

        if (!validateFileType(file)) {
            showToast('Please select an image file (PNG, JPG, JPEG, GIF)', 'error');
            return;
        }

        const formData = new FormData();
        formData.append('profile_pic', file);

        try {
            const response = await fetch('/victim/profile/upload-pic', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();
            if (response.ok) {
                showToast('Profile picture updated successfully', 'success');
                updateProfilePicture(result.filename);
            } else {
                throw new Error(result.message);
            }
        } catch (error) {
            showToast(error.message || 'Failed to upload profile picture', 'error');
        }
    }

    function validateFileType(file) {
        const validTypes = ['image/jpeg', 'image/png', 'image/gif'];
        return validTypes.includes(file.type);
    }

    function updateProfilePicture(filename) {
        // Image display removed per styling requirements
        /*
        const profilePic = document.querySelector('.profile-pic');
        if (profilePic) {
            profilePic.src = `/static/uploads/${filename}`;
        }
        */
    }

    function updateStatusIndicator(status) {
        const indicator = document.querySelector('.safety-status');
        if (indicator) {
            indicator.className = `safety-status ${status}`;
        }
    }

    function showToast(message, type = 'info') {
        let container = document.querySelector('.toast-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'toast-container';
            document.body.appendChild(container);
        }

        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;

        container.appendChild(toast);
        
        // Trigger animation
        setTimeout(() => toast.classList.add('show'), 10);

        // Remove toast after delay
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
});