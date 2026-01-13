// Login Form Validation
document.addEventListener('DOMContentLoaded', function() {
    console.log('Login JS loaded');

    const loginForm = document.querySelector('form');
    if (loginForm) {
        loginForm.addEventListener('submit', function(event) {
            // Perform any custom validation or actions here
            console.log('Form submitted');
        });
    }
});

// Register Form Validation
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('registerForm');
    const firstName = document.getElementById('first_name');
    const lastName = document.getElementById('last_name');
    const email = document.getElementById('email');
    const phone = document.getElementById('phone');
    const gender = document.getElementById('gender');
    const password = document.getElementById('password');
    const confirmPassword = document.getElementById('confirmPassword');

    if (form) {
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            checkInputs();
        });
    }

    function checkInputs() {
        // trim to remove the whitespaces
        const firstNameValue = firstName ? firstName.value.trim() : '';
        const lastNameValue = lastName ? lastName.value.trim() : '';
        const emailValue = email ? email.value.trim() : '';
        const phoneValue = phone ? phone.value.trim() : '';
        const genderValue = gender ? gender.value.trim() : '';
        const passwordValue = password ? password.value.trim() : '';
        const confirmPasswordValue = confirmPassword ? confirmPassword.value.trim() : '';
        
        let isValid = true;

        if(firstName) {
            if(firstNameValue === '') {
                setErrorFor(firstName, 'First name cannot be blank');
                isValid = false;
            } else if(firstNameValue.length < 2) {
                setErrorFor(firstName, 'First name must be at least 2 characters');
                isValid = false;
            } else {
                setSuccessFor(firstName);
            }
        }

        if(lastName) {
            if(lastNameValue === '') {
                setErrorFor(lastName, 'Last name cannot be blank');
                isValid = false;
            } else if(lastNameValue.length < 2) {
                setErrorFor(lastName, 'Last name must be at least 2 characters');
                isValid = false;
            } else {
                setSuccessFor(lastName);
            }
        }
        
        if(email) {
            if(emailValue === '') {
                setErrorFor(email, 'Email cannot be blank');
                isValid = false;
            } else if (!isEmail(emailValue)) {
                setErrorFor(email, 'Not a valid email');
                isValid = false;
            } else {
                setSuccessFor(email);
            }
        }

        if(phone) {
            if(phoneValue === '') {
                setErrorFor(phone, 'Phone number cannot be blank');
                isValid = false;
            } else {
                setSuccessFor(phone);
            }
        }

        if(gender) {
            if(genderValue === '') {
                setErrorFor(gender, 'Gender cannot be blank');
                isValid = false;
            } else {
                setSuccessFor(gender);
            }
        }
        
        if(password) {
            if(passwordValue === '') {
                setErrorFor(password, 'Password cannot be blank');
                isValid = false;
            } else if(passwordValue.length < 6) {
                setErrorFor(password, 'Password must be at least 6 characters');
                isValid = false;
            } else {
                setSuccessFor(password);
            }
        }
        
        if(confirmPassword) {
            if(confirmPasswordValue === '') {
                setErrorFor(confirmPassword, 'Confirm Password cannot be blank');
                isValid = false;
            } else if(passwordValue !== confirmPasswordValue) {
                setErrorFor(confirmPassword, 'Passwords do not match');
                isValid = false;
            } else {
                setSuccessFor(confirmPassword);
            }
        }

        if (isValid){
            form.submit();
        }
    }

    function setErrorFor(input, message) {
        const formControl = input.parentElement.parentElement;
        const small = formControl.querySelector('small');
        formControl.className = 'form-control error';
        if (small) small.innerText = message;
    }

    function setSuccessFor(input) {
        const formControl = input.parentElement.parentElement;
        formControl.className = 'form-control success';
    }

    function isEmail(email) {
        return /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@(([^<>()[\]\.,;:\s@"]+\.)+[^<>()[\]\.,;:\s@"]{2,})$/i.test(email);
    }
});

// Wait for the DOM to fully load before executing the script
document.addEventListener('DOMContentLoaded', function() {
    // Get the "Show/Hide" button for the password field
    const togglePassword = document.getElementById('togglePassword');
    // Get the password input field
    const password = document.getElementById('password');

    // Get the "Show/Hide" button for the confirm password field
    const toggleConfirmPassword = document.getElementById('toggleConfirmPassword');
    // Get the confirm password input field
    const confirmPassword = document.getElementById('confirmPassword');

    // Add a click event listener to the "Show/Hide" button for the password field
    if (togglePassword) {
        togglePassword.addEventListener('click', function() {
            // Check the current type of the password field (either "password" or "text")
            const type = password.getAttribute('type') === 'password' ? 'text' : 'password';
            // Toggle the type attribute of the password field
            password.setAttribute('type', type);
            // Toggle icon
            this.setAttribute('name', type === 'password' ? 'eye-outline' : 'eye-off-outline');
        });
    }

    // Add a click event listener to the "Show/Hide" button for the confirm password field
    if (toggleConfirmPassword) {
        toggleConfirmPassword.addEventListener('click', function() {
            const type = confirmPassword.getAttribute('type') === 'password' ? 'text' : 'password';
            confirmPassword.setAttribute('type', type);
            // Toggle icon
            this.setAttribute('name', type === 'password' ? 'eye-outline' : 'eye-off-outline');
        });
    }
});

// START OF forgotpassword.html
// Function to open the user's default email client with a pre-filled email
function sendEmail() {//gets called when the button is clicked.

    let email = document.getElementById("userEmail").value; // Get the user's email from the input field

    // Check if the email field is empty
     if (email.trim() === "") {
        alert("Please enter a valid email address.");
        return; // Stop execution if no email is entered
    }

    let subject = "Request for Help"; // The subject of the email

    let body = "Hello,%0D%0A%0D%0AI would like more information regarding..."; // The body of the email

    // Formatting the "mailto" link
    let mailtoLink = `mailto:${email}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;

    // Redirecting the user to the email client
    window.location.href = mailtoLink;
}
// END OF forgotpassword.html

// START OF frontpage.html
/** FOOTER VISIBILITY **/
const footer = document.getElementById("footer");

if (footer) {
    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach(entry => {
                footer.style.visibility = entry.isIntersecting ? "visible" : "hidden";
                // Optional opacity transition
                // footer.style.opacity = entry.isIntersecting ? "1" : "0";
            });
        },
        { threshold: 0.3 } // Footer appears when at least 30% is visible
    );
    observer.observe(footer);
}
// END OF frontpage.html

// START OF admin.html
// Select all sidebar list items
const listItems = document.querySelectorAll(".sidebar li"); // Grabs all <li> elements inside the .sidebar

// Function to handle click (permanent selection)
function setActiveItem() {
    listItems.forEach((item) => item.classList.remove("active")); // Remove "active" from all items
    this.classList.add("active"); // Add "active" class to the clicked item
    localStorage.setItem("activeSidebarItem", this.dataset.item); // Save the clicked item's index in localStorage
}

// Function to handle hover (temporary effect)
function handleHover() {
    this.classList.add("hovered"); // Add "hovered" class when mouse enters the item
}

// Function to remove hover effect when mouse leaves
function removeHover() {
    this.classList.remove("hovered"); // Remove "hovered" class when mouse leaves the item
}

// Add event listeners to all sidebar items
listItems.forEach((item, index) => {
    item.dataset.item = index; // Assign a unique index to each item for identification in localStorage
    item.addEventListener("click", setActiveItem); // Listen for clicks to apply the "active" state
    item.addEventListener("mouseenter", handleHover); // Apply "hovered" class on mouse enter
    item.addEventListener("mouseleave", removeHover); // Remove "hovered" class on mouse leave
});

// Restore the active item based on the current page URL when the page loads
document.addEventListener("DOMContentLoaded", () => {
    const currentPage = window.location.pathname; // Get the current page's URL path
    let matched = false; // Variable to track if a sidebar item matches the current page

    listItems.forEach((item) => {
        const itemLink = item.querySelector("a"); // Get the <a> tag inside the sidebar item
        if (itemLink && itemLink.getAttribute("href") === currentPage) { // Check if the item's link matches the current URL
            listItems.forEach((el) => el.classList.remove("active")); // Remove "active" class from all items
            item.classList.add("active"); // Set "active" only on the matching item
            localStorage.setItem("activeSidebarItem", item.dataset.item); // Save the active item in localStorage
            matched = true; // Mark that a match was found
        }
    });

    // If no matching URL is found, fall back to last saved selection from localStorage
    if (!matched) {
        const savedItem = localStorage.getItem("activeSidebarItem"); // Retrieve the last saved active item index
        if (savedItem !== null && listItems[savedItem]) { // Ensure the saved item exists in the list
            listItems[savedItem].classList.add("active"); // Restore the saved active item
        }
    }
});


// Function to update and display the current date and time in DD/MM/YYYY format
function updateDateTime() {
    let now = new Date();
    let day = now.getDate().toString().padStart(2, '0');
    let month = (now.getMonth() + 1).toString().padStart(2, '0');
    let year = now.getFullYear();
    let hours = now.getHours().toString().padStart(2, '0');
    let minutes = now.getMinutes().toString().padStart(2, '0');
    let seconds = now.getSeconds().toString().padStart(2, '0');

    let dateString = `${day}/${month}/${year}`;
    let timeString = `${hours}:${minutes}:${seconds}`;

    const dateTimeElement = document.getElementById("dateTime");
    if (dateTimeElement) {
        dateTimeElement.innerHTML = `${dateString}<br>${timeString}`;
    } else {
        console.warn('Element with id "dateTime" not found');
    }
}

setInterval(updateDateTime, 1000);
updateDateTime();
// END OF admin.html

console.log('Script loaded');
const button = document.getElementById('someButton');
if (button) {
    button.addEventListener('click', function () {
        console.log('Button clicked');
    });
} else {
    console.warn('Button with id "someButton" not found');
}