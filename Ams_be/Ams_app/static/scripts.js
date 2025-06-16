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


// Auto-hide Django flash messages after 5 seconds
document.addEventListener("DOMContentLoaded", function() {
    const alerts = document.querySelectorAll(".alert");
    if (alerts.length > 0) {
        setTimeout(() => {
            alerts.forEach((alert) => {
                alert.style.transition = "opacity 0.5s ease";
                alert.style.opacity = "0";
                setTimeout(() => alert.remove(), 500); // Remove after fade out
            });
        }, 5000); // Delay before hiding messages
    }
});

