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
    'wahab': [
      { date: '2024-02-01', event: 'Project Kickoff' },
      // Add more events as needed
    ],
};

// Store user events in local storage
localStorage.setItem('userEvents', JSON.stringify(userEvents));

// Define public events
var publicEvents = [
    { date: '2024-05-01', event: 'this is public events1'},
    { date: '2023-06-15', event: 'this is public events2' },
    // Add more public events as needed
];

// Store public events in local storage
localStorage.setItem('publicEvents', JSON.stringify(publicEvents));