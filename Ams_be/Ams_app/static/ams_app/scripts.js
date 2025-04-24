// ams_app/static/ams_app/scripts.js

document.addEventListener("DOMContentLoaded", function() {
    const checkInButton = document.querySelector(".check-in-btn");
    const checkOutButton = document.querySelector(".check-out-btn");

    // If check-in button is pressed, disable it to prevent multiple submissions
    if (checkInButton) {
        checkInButton.addEventListener("click", function() {
            checkInButton.disabled = true;
            checkInButton.innerText = "Checked In";
        });
    }

    // If check-out button is pressed, disable it to prevent multiple submissions
    if (checkOutButton) {
        checkOutButton.addEventListener("click", function() {
            checkOutButton.disabled = true;
            checkOutButton.innerText = "Checked Out";
        });
    }
});
