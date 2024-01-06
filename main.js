let btn = document.querySelector("#btn");
let sidebar = document.querySelector(".sidebar");
let popup = document.getElementById('logoutPopup');

btn.onclick = function () {
    toggleSidebar();
};

document.addEventListener('DOMContentLoaded', function () {
    restoreSession();
    checkLoginStatus();
    displayExpirationDate();

    window.addEventListener('beforeunload', function (event) {
        storeSession();
    });

    // Set an interval to check session expiration every 10 seconds
    sessionExpirationTimer = setInterval(checkSessionExpiration, 10000);
});

document.getElementById('btn').onclick = function () {
    toggleSidebar();
};

function toggleSidebar() {
    sidebar.classList.toggle("active");
    popup.style.zIndex = sidebar.classList.contains("active") ? '3' : '4';
    document.querySelector('body').classList.toggle('blur', sidebar.classList.contains("active"));
    var logoutButton = document.getElementById('logoutButton');
    logoutButton.style.pointerEvents = sidebar.classList.contains("active") ? 'none' : 'auto';
}


//dashboard content 
document.getElementById('username').textContent = localStorage.getItem('username') || 'Guest';


function logout() {
    console.log('Logout function called');
    try {
        localStorage.removeItem('loggedIn');
        localStorage.removeItem('username');
        localStorage.removeItem('expirationDate');

        window.location.href = 'index.html';
    } catch (error) {
        console.error('Logout error:', error);
    }
}

function cancelLogout() {
    var popup = document.getElementById('logoutPopup');
    popup.style.display = 'none';
}

function showLogoutPopup() {
    console.log('Show logout popup function called');
    var popup = document.getElementById('logoutPopup');
    popup.style.display = 'block';
    popup.style.zIndex = '100';
    document.querySelector('body').classList.add('blur');
}

function checkLoginStatus() {
    var loggedIn = localStorage.getItem('loggedIn');
    console.log('loggedIn:', loggedIn);
    if (loggedIn === 'true') {
        var username = localStorage.getItem('username');
        console.log('username:', username);
        var usernameSpan = document.getElementById('usernameSpan');
        usernameSpan.textContent = username;
        usernameSpan.style.fontWeight = 'bold';
    } else {
        window.location.href = 'login2.html';
    }
}

function storeSession() {
    // Store session data before unloading the page
    var loggedIn = localStorage.getItem('loggedIn');
    if (loggedIn === 'true') {
        var username = localStorage.getItem('username');
        var expirationDate = localStorage.getItem('expirationDate');
        var storedCredentials = JSON.parse(localStorage.getItem('validCredentials'));

        var sessionData = {
            loggedIn: loggedIn,
            username: username,
            expirationDate: expirationDate,
            validCredentials: storedCredentials
        };

        localStorage.setItem('sessionData', JSON.stringify(sessionData));
    }
}

function restoreSession() {
    // Check for stored session data and restore it
    var sessionData = JSON.parse(localStorage.getItem('sessionData'));

    if (sessionData) {
        localStorage.setItem('loggedIn', sessionData.loggedIn);
        localStorage.setItem('username', sessionData.username);
        localStorage.setItem('expirationDate', sessionData.expirationDate);
        localStorage.setItem('validCredentials', JSON.stringify(sessionData.validCredentials));

        // Clear the stored session data
        localStorage.removeItem('sessionData');
    }
}

function checkSessionExpiration() {
    var loggedIn = localStorage.getItem('loggedIn');
    var username = localStorage.getItem('username');
    var storedCredentials = JSON.parse(localStorage.getItem('validCredentials'));

    if (loggedIn === 'true' && storedCredentials && storedCredentials[username]) {
        var credentials = storedCredentials[username];
        var expirationDate = new Date(credentials.expires);
        var currentDate = new Date();

        if (currentDate >= expirationDate) {
            // Delay the logout by 5 seconds
            setTimeout(function () {
                logout();
            }, 5000);
        }
    }
}

// Set an interval to check session expiration every 10 seconds
sessionExpirationTimer = setInterval(checkSessionExpiration, 10000);

document.addEventListener('DOMContentLoaded', function () {
    checkLoginStatus();
    displayExpirationDate();
});

function checkLoginStatus() {
    var loggedIn = localStorage.getItem('loggedIn');
    var username = localStorage.getItem('username');
    var storedCredentials = JSON.parse(localStorage.getItem('validCredentials'));

    if (loggedIn === 'true' && username && storedCredentials && storedCredentials[username]) {
        var credentials = storedCredentials[username];
        var expirationDate = new Date(credentials.expires);
        var currentDate = new Date();

        if (currentDate < expirationDate) {
            // User is still logged in, update the login name in the HTML
            var nameElement = document.querySelector('.name');
            nameElement.textContent = username;
        } else {
            // Session has expired, redirect to the login page
            window.location.href = 'login2.html';
        }
    } else {
        // User not logged in, redirect to the login page
        window.location.href = 'login2.html';
    }
}

function displayExpirationDate() {
    var loggedIn = localStorage.getItem('loggedIn');
    var username = localStorage.getItem('username');
    var storedCredentials = JSON.parse(localStorage.getItem('validCredentials'));

    console.log('loggedIn:', loggedIn);
    console.log('username:', username);
    console.log('storedCredentials:', storedCredentials);

    if (loggedIn === 'true' && storedCredentials && storedCredentials[username]) {
        var credentials = storedCredentials[username];
        var expirationDate = credentials.expires;

        console.log('expirationDate:', expirationDate);

        // Update the expiration date in the HTML without the "Expiration: " text
        var jobElement = document.getElementById('expirationDate');
        jobElement.textContent = 'Expiration: ' + expirationDate;
    } else {
        console.log('User not logged in or credentials not found.');
    }
}

//dashboard content 

//calender

document.addEventListener('DOMContentLoaded', function () {
    const eventTableBody = document.getElementById('eventTableBody');
    const storedUsername = localStorage.getItem('username');

    if (storedUsername) {
        // If a username is stored in localStorage, load events for that user
        loadEventsForUser(storedUsername);
    } else {
        // If no username is stored, prompt the user to enter one
        promptForUsername();
    }

    function promptForUsername() {
        const allUsernames = getAllUsernamesFromEvents();
        const username = prompt("Enter your username:", allUsernames.join(', '));

        if (username && allUsernames.includes(username)) {
            localStorage.setItem('username', username);
            loadEventsForUser(username);
        } else {
            alert("Invalid or empty username. Please enter a valid username.");
            promptForUsername();
        }
    }

    function loadEventsForUser(username) {
        const storedUserEvents = JSON.parse(localStorage.getItem('userEvents')) || {};
        const storedPublicEvents = JSON.parse(localStorage.getItem('publicEvents')) || [];
    
        const userEvents = storedUserEvents[username] || [];
        const allEvents = userEvents.concat(storedPublicEvents);
    
        // Filter out outdated events (older than 3 days)
        const currentDate = new Date();
        const filteredEvents = allEvents.filter(event => {
            const eventDate = new Date(event.date);
            const daysDifference = Math.ceil((currentDate - eventDate) / (1000 * 60 * 60 * 24));
            return daysDifference <= 3; // Keep events within 3 days
        });
    
        // Save the filtered events back to local storage
        storedUserEvents[username] = filteredEvents;
        localStorage.setItem('userEvents', JSON.stringify(storedUserEvents));
    
        displayEvents(filteredEvents);
    }

    function displayEvents(events) {
        // Clear existing events from the table
        eventTableBody.innerHTML = '';
    
        // Sort events based on their dates (newest to oldest)
        events.sort((a, b) => new Date(b.date) - new Date(a.date));
    
        // Display sorted events
        events.forEach(event => {
            const row = document.createElement('tr');
            const currentDate = new Date();
            const eventDate = new Date(event.date);
    
            // Check if the event date is outdated
            if (eventDate < currentDate) {
                row.classList.add('outdated-event'); // Add a CSS class for styling
                row.innerHTML = `<td>${event.date}</td><td><span style="font-weight: bold;">${event.event}</span> (Outdated)</td>`;
            } else {
                const daysRemaining = Math.ceil((eventDate - currentDate) / (1000 * 60 * 60 * 24));
                const daysRemainingText = daysRemaining > 0 ? `(${daysRemaining} days remaining)` : "(Today)";
    
                row.innerHTML = `<td>${event.date}</td><td><span style="font-weight: bold; display: block;">${event.event}</span><span>${daysRemainingText}</span></td>`;
            }
    
            eventTableBody.appendChild(row);
        });
    }

    
});



//booking form 

// script.js
// Retrieve the username from local storage
const storedUsername = localStorage.getItem('username');

// Check if username is present in local storage
if (storedUsername) {
// Set the value of the 'Name' field to the retrieved username
document.getElementById('name').value = storedUsername;
}

function sendFormData() {
const date = document.getElementById('date').value;
const name = document.getElementById('name').value;
const countryCode = document.getElementById('countryCode').value;
const mobile = document.getElementById('mobile').value;
const customerNeeds = document.getElementById('customerNeeds').value;

// Check if all required fields are filled
if (date && name && countryCode && mobile) {
  const whatsappPhoneNumber = `+15512615218`; // Replace with your desired WhatsApp phone number
  const fullPhoneNumber = `+${countryCode}${mobile}`;
  let message = `*RHYTHMI Booking Details*\n\n*Date:* ${date}\n*Username:* ${name}\n*Mobile:* ${fullPhoneNumber}`;

  // Append customer needs to the message if provided
  if (customerNeeds) {
    message += `\n*Customer Needs:* ${customerNeeds}`;
  }

  const whatsappLink = `https://wa.me/${whatsappPhoneNumber}?text=${encodeURIComponent(message)}`;

  // Open the WhatsApp link in a new tab/window
  window.open(whatsappLink, '_blank');
} else {
  alert('Please fill in all required fields.');
}
}