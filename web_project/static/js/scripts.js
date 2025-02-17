// DOM Loaded
document.addEventListener("DOMContentLoaded", function () {
    console.log("JavaScript is ready!");

    // Example: Alert on button click
    const buttons = document.querySelectorAll(".button");
    buttons.forEach(button => {
        button.addEventListener("click", function () {
            alert("Button clicked!");
        });
    });

    // Example: Confirmation on delete
    const deleteLinks = document.querySelectorAll(".delete-link");
    deleteLinks.forEach(link => {
        link.addEventListener("click", function (e) {
            if (!confirm("Are you sure you want to delete this item?")) {
                e.preventDefault();
            }
        });
    });
});
