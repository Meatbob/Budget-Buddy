document.addEventListener("DOMContentLoaded", function () {
    console.log("JavaScript is ready!");

    // Example: Confirmation on delete
    const deleteLinks = document.querySelectorAll(".delete-link");
    deleteLinks.forEach(link => {
        link.addEventListener("click", function (e) {
            if (!confirm("Are you sure you want to delete this item?")) {
                e.preventDefault();
            }
        });
    });

    // Show Password Toggle
    const showPasswordCheckbox = document.getElementById("show-password");
    const passwordField = document.getElementById("password");

    // Check if the elements exist before adding the event listener
    if (showPasswordCheckbox && passwordField) {
        showPasswordCheckbox.addEventListener("change", function () {
            // Toggle password field visibility based on the checkbox state
            passwordField.type = showPasswordCheckbox.checked ? "text" : "password";
        });
    }
});
