document.addEventListener("DOMContentLoaded", function () {
    const navbar = document.querySelector(".navbar");

    window.addEventListener("scroll", function () {
        if (window.scrollY > 50) {
            navbar.classList.add("scrolled");
        } else {
            navbar.classList.remove("scrolled");
        }
    });
});

document.addEventListener("DOMContentLoaded", function () {
    let navLinks = document.querySelectorAll(".nav-link");
    let navbarToggler = document.querySelector(".navbar-toggler");
    let navbarCollapse = document.querySelector(".navbar-collapse");

    // Close the navbar when a nav link is clicked
    navLinks.forEach(link => {
        link.addEventListener("click", function () {
            if (navbarCollapse.classList.contains("show")) {
                navbarToggler.click();
            }
        });
    });

    // Close the navbar when clicking outside of it
    document.addEventListener("click", function (event) {
        if (!navbarToggler.contains(event.target) && !navbarCollapse.contains(event.target)) {
            navbarCollapse.classList.remove("show");
        }
    });
});

document.addEventListener("DOMContentLoaded", function () {
    const countdownElements = document.querySelectorAll(".event-countdown");

    countdownElements.forEach(el => {
        const eventDate = new Date(el.getAttribute("data-date")).getTime();

        setInterval(() => {
            let now = new Date().getTime();
            let timeLeft = eventDate - now;

            let days = Math.floor(timeLeft / (1000 * 60 * 60 * 24));
            let hours = Math.floor((timeLeft % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            let minutes = Math.floor((timeLeft % (1000 * 60 * 60)) / (1000 * 60));

            el.innerHTML = `<strong>${days}d ${hours}h ${minutes}m left</strong>`;
        }, 1000);
    });
});

document.getElementById('ticket-category').addEventListener('change', updateTotal);
let quantity = 1;

function changeQuantity(amount) {
    quantity = Math.max(1, quantity + amount);
    document.getElementById('ticket-quantity').textContent = quantity;
    updateTotal();
}

function updateTotal() {
    let ticketPrice = parseInt(document.getElementById('ticket-category').value);
    let totalPrice = ticketPrice * quantity;
    document.getElementById('total-price').textContent = totalPrice.toLocaleString();
}

document.addEventListener("DOMContentLoaded", function () {
    let paymentMethods = document.querySelectorAll('input[name="payment-method"]');
    let mpesaInput = document.getElementById("mpesa-input");

    // Show/hide relevant payment input
    paymentMethods.forEach(method => {
        method.addEventListener("change", function () {
            if (this.value === "mpesa") {
                mpesaInput.classList.add("active");
            } else {
                mpesaInput.classList.remove("active");
            }
        });
    });

    // Load order details dynamically (assuming data is passed via URL or session)
    document.getElementById("event-name").textContent = localStorage.getItem("eventName") || "Food & Wine Festival";
    document.getElementById("event-date").textContent = localStorage.getItem("eventDate") || "May 10, 2025";
    document.getElementById("event-location").textContent = localStorage.getItem("eventLocation") || "Nairobi, Kenya";
    document.getElementById("ticket-type").textContent = localStorage.getItem("ticketType") || "VIP";
    document.getElementById("ticket-quantity").textContent = localStorage.getItem("ticketQuantity") || "2";
    document.getElementById("total-price").textContent = localStorage.getItem("totalPrice") || "10,000";
});

function increaseQty(button) {
    let qtyElement = button.previousElementSibling;
    let qty = parseInt(qtyElement.innerText);
    qtyElement.innerText = qty + 1;
    updateCartTotal();
}

function decreaseQty(button) {
    let qtyElement = button.nextElementSibling;
    let qty = parseInt(qtyElement.innerText);
    if (qty > 1) {
        qtyElement.innerText = qty - 1;
        updateCartTotal();
    }
}

function updateCartTotal() {
    let subtotal = 0;
    let serviceFee = 200;

    document.querySelectorAll(".cart-item").forEach(item => {
        let priceText = item.querySelector(".price").innerText;
        let price = parseInt(priceText.replace("Ksh ", "").replace(",", ""));
        let qty = parseInt(item.querySelector(".qty").innerText);

        subtotal += price * qty;
    });

    document.getElementById("subtotal").innerText = "Ksh " + subtotal.toLocaleString();
    document.getElementById("total").innerText = "Ksh " + (subtotal + serviceFee).toLocaleString();
}

// Update total on page load
document.addEventListener("DOMContentLoaded", updateCartTotal);

function addTicket() {
    let ticketSection = document.getElementById("ticket-section");
    let newTicket = document.createElement("div");
    newTicket.classList.add("ticket-category", "mb-2");
    newTicket.innerHTML = `
        <input type="text" name="ticket_type[]" class="form-control mb-2" placeholder="Ticket Type (e.g., VIP, Early Bird)" required>
        <input type="number" name="ticket_price[]" class="form-control mb-2" placeholder="Price (Ksh)" required>
        <input type="number" name="ticket_quantity[]" class="form-control mb-2" placeholder="Available Quantity" required>
    `;
    ticketSection.appendChild(newTicket);
}

document.addEventListener("DOMContentLoaded", function () {
    // Get all radio buttons
    const paymentRadios = document.querySelectorAll('input[name="payment-method"]');

    // Add event listeners to all radio buttons
    paymentRadios.forEach(radio => {
        radio.addEventListener('change', function () {
            showPaymentFields(this.value);
        });
    });

    // Function to show the selected payment fields
    function showPaymentFields(method) {
        // Hide all payment fields
        document.querySelectorAll('.payment-detail').forEach(el => el.style.display = 'none');

        // Show the selected method's fields
        document.getElementById(method + '-fields').style.display = 'block';
    }
});

document.addEventListener("DOMContentLoaded", function () {
    var ctx = document.getElementById('ticketSalesChart').getContext('2d');
    var myChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
            datasets: [{
                label: 'Tickets Sold',
                data: [120, 200, 150, 300, 250],
                backgroundColor: 'rgba(54, 162, 235, 0.5)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {beginAtZero: true}
            }
        }
    });
});

// Hide flash messages after 3 seconds
setTimeout(function () {
    let alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => alert.style.display = 'none');
}, 3000);
