document.addEventListener('DOMContentLoaded', function() {
    console.log('Victim JS loaded');

    // Handle the search form submission for better UX
    const searchForm = document.querySelector('.search-form');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            const searchQuery = document.getElementById('searchVictim').value.trim();
            const genderFilter = document.getElementById('genderFilter').value;
            
            // Only submit if at least one field has a value
            if (!searchQuery && !genderFilter) {
                e.preventDefault();
                alert('Please enter a search term or select a filter');
            }
        });
    }

    // Add Victim Form toggling
    const showAddVictimFormButton = document.getElementById('showAddVictimForm');
    const addVictimFormContainer = document.getElementById('addVictimFormContainer');
    const cancelAddVictimButton = document.getElementById('cancelAddVictim');
    const editVictimFormContainer = document.getElementById('editVictimFormContainer');
    const cancelEditVictimButton = document.getElementById('cancelEditVictim');
    const overlay = document.createElement('div');
    overlay.className = 'overlay';
    document.body.appendChild(overlay);

    if (showAddVictimFormButton && addVictimFormContainer && cancelAddVictimButton) {
        showAddVictimFormButton.addEventListener('click', function() {
            addVictimFormContainer.style.display = 'flex';
            overlay.style.display = 'block';
        });
        cancelAddVictimButton.addEventListener('click', function() {
            addVictimFormContainer.style.display = 'none';
            overlay.style.display = 'none';
        });
        overlay.addEventListener('click', function() {
            addVictimFormContainer.style.display = 'none';
            editVictimFormContainer.style.display = 'none';
            overlay.style.display = 'none';
        });
    } else {
        console.error("Missing add victim elements");
    }

    // Edit Victim Form handling
    document.querySelectorAll('.edit-btn').forEach(button => {
        button.addEventListener('click', function() {
            const victimId = this.getAttribute('data-id');
            const firstName = this.getAttribute('data-first_name');
            const lastName = this.getAttribute('data-last_name');
            const email = this.getAttribute('data-email');
            const phone = this.getAttribute('data-phone');
            const gender = this.getAttribute('data-gender');
            const location = this.getAttribute('data-location');
            const caseDescription = this.getAttribute('data-case_description');

            document.getElementById('edit_victim_id').value = victimId;
            document.getElementById('edit_first_name').value = firstName;
            document.getElementById('edit_last_name').value = lastName;
            document.getElementById('edit_email').value = email;
            document.getElementById('edit_phone').value = phone;
            document.getElementById('edit_gender').value = gender;
            document.getElementById('edit_location').value = location;
            document.getElementById('edit_case_description').value = caseDescription;

            document.getElementById('editVictimForm').action = `/victim/edit_victim/${victimId}`;

            editVictimFormContainer.style.display = 'flex';
            overlay.style.display = 'block';
        });
    });

    cancelEditVictimButton.addEventListener('click', function() {
        editVictimFormContainer.style.display = 'none';
        overlay.style.display = 'none';
    });
});