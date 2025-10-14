// Performance issue: inefficient DOM manipulation
function updateList(items) {
    const list = document.getElementById('list');
    list.innerHTML = '';
    
    for (let i = 0; i < items.length; i++) {
        const li = document.createElement('li');
        li.textContent = items[i];
        list.appendChild(li);
    }
}

// Security issue: potential XSS vulnerability
function displayMessage(message) {
    document.getElementById('output').innerHTML = message;
}

// Code quality issue: no error handling
async function fetchData(url) {
    const response = await fetch(url);
    const data = await response.json();
    return data;
}