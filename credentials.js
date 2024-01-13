// credentials.js
var validCredentials = {
    '51160': { password: 'Aa96991995', expires: '9999-12-27' },
    '49001': { password: 'ni002', expires: '9999-12-31' },
    'admin': { password: '00000', expires: '2025-12-25' },
    'StartUp': { password: '2024', expires: '2024-04-10' },
    'Ebrahim': { password: '0002', expires: '2023-12-31' },
    'wahab': { password: '9699', expires: '2023-12-6' },

    'AUM': { password: '2024', expires: '2025-01-16' },
    'Alaa.Eleyan': { password: '2024', expires: '2025-01-16' },
    'Khaled.Chaine' : { password: '2024', expires: '2025-01-16' },
    'Bilal.Jabakhanji': { password: '2024', expires: '2025-01-16' },
    'Samer.Al Kork': { password: '2024', expires: '2025-01-16' },
    'Taha.Beyrouthy': { password: '2024', expires: '2025-01-16' },
    'Abdullah.Karar': { password: '2024', expires: '2025-01-16' },
    'Fahmi.El-Sayed': { password: '2024', expires: '2025-01-16' },
    'Mouhammad.AlAkkoumi': { password: '2024', expires: '2025-01-16' },
    'Mehmet.Karaman': { password: '2024', expires: '2025-01-16' },
    'Wael.Farag': { password: '2024', expires: '2025-01-16' }, 
};

// Store in local storage
localStorage.setItem('validCredentials', JSON.stringify(validCredentials));