// DOM Elements
const loginForm = document.getElementById('login-form');
const registerForm = document.getElementById('register-form');
const usernameInput = document.getElementById('username');
const passwordInput = document.getElementById('password');
const regUsernameInput = document.getElementById('reg-username');
const regEmailInput = document.getElementById('reg-email');
const regPasswordInput = document.getElementById('reg-password');
const regConfirmInput = document.getElementById('reg-confirm');
const agreeCheckbox = document.getElementById('agree-checkbox');
const acceptBtn = document.getElementById('accept-btn');
const guidelinesContent = document.getElementById('guidelines-content');

// Load ethical guidelines on startup
window.addEventListener('DOMContentLoaded', async () => {
    const guidelines = await window.payforgeAPI.getEthicalGuidelines();
    guidelinesContent.innerHTML = `<pre>${guidelines}</pre>`;
});

// Toggle checkbox to enable accept button
agreeCheckbox.addEventListener('change', (e) => {
    acceptBtn.disabled = !e.target.checked;
});

// Login form submission
loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const username = usernameInput.value.trim();
    const password = passwordInput.value;

    if (!username || !password) {
        showError('login-error', 'Username and password required');
        return;
    }

    try {
        const result = await window.payforgeAPI.checkCredentials(username, password);
        
        if (result.success) {
            // Store session
            localStorage.setItem('payforge_token', result.token);
            localStorage.setItem('payforge_user', result.username);
            
            // Show guidelines
            toggleSection('guidelines-section');
        } else {
            showError('login-error', result.message);
        }
    } catch (error) {
        showError('login-error', 'Login failed: ' + error.message);
    }
});

// Register form submission
registerForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const username = regUsernameInput.value.trim();
    const email = regEmailInput.value.trim();
    const password = regPasswordInput.value;
    const confirm = regConfirmInput.value;

    if (!username || !email || !password || !confirm) {
        showError('register-error', 'All fields required');
        return;
    }

    if (password.length < 8) {
        showError('register-error', 'Password must be at least 8 characters');
        return;
    }

    if (password !== confirm) {
        showError('register-error', 'Passwords do not match');
        return;
    }

    try {
        const result = await window.payforgeAPI.createUser(username, password, email);
        
        if (result.success) {
            showSuccess('register-error', result.message);
            setTimeout(() => toggleSection('login-section'), 2000);
        } else {
            showError('register-error', result.message);
        }
    } catch (error) {
        showError('register-error', 'Registration failed: ' + error.message);
    }
});

// Toggle between sections
function toggleSection(sectionId) {
    const sections = document.querySelectorAll('.section');
    sections.forEach(section => section.classList.remove('active'));
    document.getElementById(sectionId).classList.add('active');
}

// Show error message
function showError(elementId, message) {
    const errorDiv = document.getElementById(elementId);
    errorDiv.textContent = '❌ ' + message;
    errorDiv.classList.add('show');
    setTimeout(() => errorDiv.classList.remove('show'), 5000);
}

// Show success message
function showSuccess(elementId, message) {
    const successDiv = document.getElementById(elementId);
    successDiv.textContent = '✓ ' + message;
    successDiv.style.background = '#d5f4e6';
    successDiv.style.color = '#27ae60';
    successDiv.classList.add('show');
}

// Launch console
async function launchConsole() {
    await window.payforgeAPI.launchConsole();
}

// Default credentials for testing
console.log('%c🔓 PayForge Auth System Loaded', 'color: #667eea; font-size: 14px; font-weight: bold');
console.log('%cDefault test credentials:', 'color: #666');
console.log('%cUsername: admin', 'color: #666');
console.log('%cPassword: admin123', 'color: #666');
