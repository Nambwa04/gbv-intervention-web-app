document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const uploadTrigger = document.getElementById('uploadTrigger');
    const addResponderBtn = document.getElementById('addResponderBtn');
    const filterButtons = document.querySelectorAll('[data-filter]');
    const exportButton = document.querySelector('.btn-primary[ion-icon="download"]');

    // Logo Upload Handling
    if (uploadTrigger) {
        const fileInput = document.createElement('input');
        fileInput.type = 'file';
        fileInput.accept = 'image/*';
        fileInput.style.display = 'none';
        document.body.appendChild(fileInput);

        uploadTrigger.addEventListener('click', () => fileInput.click());

        fileInput.addEventListener('change', async (e) => {
            if (e.target.files.length > 0) {
                const file = e.target.files[0];
                if (!validateFileType(file)) {
                    showToast('Please select an image file (PNG, JPG, JPEG)', 'error');
                    return;
                }

                const formData = new FormData();
                formData.append('logo', file);

                try {
                    const response = await fetch('/organization/profile/upload-logo', {
                        method: 'POST',
                        body: formData
                    });

                    const result = await response.json();
                    if (response.ok) {
                        showToast('Logo updated successfully', 'success');
                        updateLogo(result.filename);
                    } else {
                        throw new Error(result.message);
                    }
                } catch (error) {
                    showToast(error.message || 'Failed to upload logo', 'error');
                }
            }
        });
    }

    // Add Responder Modal
    if (addResponderBtn) {
        addResponderBtn.addEventListener('click', () => {
            showAddResponderModal();
        });
    }

    // Filtering
    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            const filterType = this.dataset.filter;
            filterItems(filterType);
        });
    });

    // Export Report
    if (exportButton) {
        exportButton.addEventListener('click', async () => {
            try {
                const response = await fetch('/organization/profile/export-report', {
                    method: 'POST'
                });

                if (response.ok) {
                    const blob = await response.blob();
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `org-report-${new Date().toISOString().split('T')[0]}.xlsx`;
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                    window.URL.revokeObjectURL(url);
                    showToast('Report exported successfully', 'success');
                } else {
                    throw new Error('Failed to export report');
                }
            } catch (error) {
                showToast(error.message, 'error');
            }
        });
    }

    // Utility Functions
    function validateFileType(file) {
        const validTypes = ['image/jpeg', 'image/png'];
        return validTypes.includes(file.type);
    }

    function updateLogo(filename) {
        // Image display removed per styling requirements
        /*
        const logoImg = document.querySelector('.org-logo');
        if (logoImg) {
            logoImg.src = `/static/uploads/${filename}`;
        }
        */
    }

    function showAddResponderModal() {
        // Implement modal logic
        console.log('Show add responder modal');
    }

    function filterItems(type) {
        // Implement filtering logic
        console.log('Filter items by:', type);
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

    // Charts and Analytics (if needed)
    function initializeCharts() {
        // Implement charts using a library like Chart.js
        console.log('Initialize charts');
    }

    // Initialize any charts if needed
    initializeCharts();
});