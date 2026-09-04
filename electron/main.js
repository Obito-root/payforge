const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');
const fs = require('fs');
const crypto = require('crypto');
const os = require('os');

let mainWindow;

// Use user's home directory for database instead of /opt/payforge
const DB_DIR = path.join(os.homedir(), '.payforge');
const DB_FILE = path.join(DB_DIR, 'auth.json');

console.log('[*] Database path:', DB_FILE);

// Initialize database file
function initDatabase() {
    // Create directory if it doesn't exist
    if (!fs.existsSync(DB_DIR)) {
        fs.mkdirSync(DB_DIR, { recursive: true, mode: 0o755 });
    }
    
    // Create database file if it doesn't exist
    if (!fs.existsSync(DB_FILE)) {
        const defaultUsers = {
            users: [
                {
                    username: "admin",
                    password: hashPassword("admin123"),
                    email: "admin@payforge.local",
                    created_at: new Date().toISOString(),
                    last_login: null
                }
            ],
            sessions: []
        };
        
        try {
            fs.writeFileSync(DB_FILE, JSON.stringify(defaultUsers, null, 2), { mode: 0o644 });
            console.log('[+] Database initialized at:', DB_FILE);
        } catch (error) {
            console.error('[!] Error creating database:', error);
        }
    }
}

// Hash password (simple hashing for demo - use bcrypt in production)
function hashPassword(password) {
    return crypto.createHash('sha256').update(password).digest('hex');
}

// Create Electron window
function createWindow() {
    mainWindow = new BrowserWindow({
        width: 500,
        height: 700,
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'),
            nodeIntegration: false,
            contextIsolation: true,
            enableRemoteModule: false
        },
        resizable: false,
        show: false
    });

    mainWindow.loadFile(path.join(__dirname, 'src/login.html'));
    mainWindow.show();

    // Open DevTools in development
    if (process.argv.includes('--dev')) {
        mainWindow.webContents.openDevTools();
    }
}

// App event handlers
app.on('ready', () => {
    initDatabase();
    createWindow();
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('activate', () => {
    if (mainWindow === null) {
        createWindow();
    }
});

// IPC Handlers
ipcMain.handle('check-credentials', async (event, username, password) => {
    try {
        if (!fs.existsSync(DB_FILE)) {
            return { success: false, message: 'Database not initialized' };
        }

        const data = JSON.parse(fs.readFileSync(DB_FILE, 'utf8'));
        const user = data.users.find(u => u.username === username);

        if (!user) {
            return { success: false, message: 'User not found' };
        }

        const hashedPassword = hashPassword(password);
        if (user.password !== hashedPassword) {
            return { success: false, message: 'Incorrect password' };
        }

        // Create session
        const sessionToken = crypto.randomBytes(32).toString('hex');
        const session = {
            token: sessionToken,
            username: username,
            created_at: new Date().toISOString(),
            expires_at: new Date(Date.now() + 30 * 60 * 1000).toISOString()
        };

        data.sessions.push(session);
        user.last_login = new Date().toISOString();
        
        fs.writeFileSync(DB_FILE, JSON.stringify(data, null, 2), { mode: 0o644 });

        return { 
            success: true, 
            message: 'Login successful',
            token: sessionToken,
            username: username
        };
    } catch (error) {
        console.error('[!] Error checking credentials:', error);
        return { success: false, message: error.message };
    }
});

ipcMain.handle('create-user', async (event, username, password, email) => {
    try {
        if (!username || !password || !email) {
            return { success: false, message: 'All fields required' };
        }

        if (!fs.existsSync(DB_FILE)) {
            return { success: false, message: 'Database not initialized' };
        }

        const data = JSON.parse(fs.readFileSync(DB_FILE, 'utf8'));
        
        if (data.users.find(u => u.username === username)) {
            return { success: false, message: 'User already exists' };
        }

        const newUser = {
            username: username,
            password: hashPassword(password),
            email: email,
            created_at: new Date().toISOString(),
            last_login: null
        };

        data.users.push(newUser);
        fs.writeFileSync(DB_FILE, JSON.stringify(data, null, 2), { mode: 0o644 });

        return { success: true, message: 'User created successfully' };
    } catch (error) {
        console.error('[!] Error creating user:', error);
        return { success: false, message: error.message };
    }
});

ipcMain.handle('get-ethical-guidelines', async () => {
    try {
        const guidelinesFile = '/opt/payforge/config/ethical_guidelines.md';
        
        if (fs.existsSync(guidelinesFile)) {
            return fs.readFileSync(guidelinesFile, 'utf8');
        }
        
        // Fallback if file doesn't exist
        return `
# PayForge Ethical Guidelines

⚠️ CRITICAL DISCLAIMER

PayForge is provided for authorized security testing and educational purposes only.

## Key Points:
1. You must obtain explicit written permission before testing any system
2. Unauthorized access to computer systems is ILLEGAL
3. You assume full responsibility for your actions
4. Use PayForge only for authorized security testing

## Acknowledgment:
By proceeding, you confirm:
- You have obtained proper authorization
- You will use PayForge ethically and legally
- You accept full legal responsibility
- You understand the criminal penalties for unauthorized access

Unauthorized access to computer systems may result in federal charges, fines, and imprisonment.
        `;
    } catch (error) {
        console.error('[!] Error loading guidelines:', error);
        return 'Error loading guidelines: ' + error.message;
    }
});

ipcMain.handle('launch-console', async () => {
    try {
        const { spawn } = require('child_process');
        
        // Try to launch PayForge console
        const child = spawn('bash', ['-c', 'payforge console'], { 
            detached: true,
            stdio: 'ignore'
        });
        
        child.unref();
        
        // Close Electron window
        setTimeout(() => {
            app.quit();
        }, 1000);
        
        return { success: true };
    } catch (error) {
        return { success: false, message: error.message };
    }
});

console.log('[*] PayForge Electron Auth System initialized');
