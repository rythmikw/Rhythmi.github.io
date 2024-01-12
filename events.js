// events.js
// Define events for each user
var userEvents = {
    '51160': [
      { date: '2021-03-10', event: 'Team Building Workshop' },
      { date: '2024-02-15', event: 'Product Launch' },
    ],
    '49001': [
      { date: '2024-03-20', event: 'Company Anniversary Celebration' },
      { date: '2024-04-05', event: 'Training Session' },
      { date: '2024-01-03', event: 'test11' },
    ],
    'admin': [
      // Admin-specific events
      // Add more events as needed
    ],
    'StartUp': [
      { date: '2024-05-01', event: 'welcome startup to our website' },
      // Add more events as needed
    ],
    'Ebrahim': [
      // Ebrahim-specific events
      // Add more events as needed
    ],






    'AUM': [
      { date: '2025-1-16', event: 'Welcome Dear Doctor, This is your events part' },
    ],

    'Alaa.Eleyan': [
      { date: '2025-1-16', event: 'Welcome Dear Dr. Alaa Eleyan, This is your events part' },
      { date: '2025-1-16', event: 'RHYTHMI appreciate your remarkable effort upon making this project possible'},
    ],
    'Khaled.Chaine': [
      { date: '2025-1-16', event: 'Welcome Dear Dr. Khanled Chaine, This is your events part' },
    ],
    'Bilal.Jabakhanji': [
      { date: '2025-1-16', event: 'Welcome Dear Dr. Bilal Jabakhanji, This is your events part'},
    ],
    'Samer.Al Kork': [
      { date: '2025-1-16', event: 'Welcome Dear Dr. Samer Al Kork, This is your events part' },
    ],
    'Taha.Beyrouthy': [
      { date: '2025-1-16', event: 'Welcome Dear Dr. Taha Beyrouthy, This is your events part' },
    ],
    'Abdullah.Karar': [
      { date: '2025-1-16', event:'Welcome Dear Dr. Abdullah Karar, This is your events part'},
    ],
    'Fahmi.El-Sayed': [
      { date: '2025-1-16', event: 'Welcome Dear Dr. Fahmi El-Sayed, This is your events part'},
    ],
    'Mouhammad.AlAkkoumi': [
      { date: '2025-1-16', event: 'Welcome Dear Dr. Mouhammad AlAkkoumi, This is your events part' },
    ],
    'Mehmet.Karaman': [
      { date: '2025-1-16', event: 'Welcome Dear Dr. Mehmet Karaman, This is your events part' },
    ],
    'Wael.Farag': [
      { date: '2025-1-16', event: 'Welcome Dear Dr. Wael Farag, This is your events part'},
    ],








};

// Store user events in local storage
localStorage.setItem('userEvents', JSON.stringify(userEvents));

// Define public events
var publicEvents = [
 //   { date: '2024-05-01', event: 'this is public events1'},
   // { date: '2023-06-15', event: 'this is public events2' },
    // Add more public events as needed
];

// Store public events in local storage
localStorage.setItem('publicEvents', JSON.stringify(publicEvents));