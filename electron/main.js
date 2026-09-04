const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');
const fs = require('fs');
const crypto = require('crypto');

let mainWindow;
const DB_FILE = '/opt/payforge/database/auth.json';

// Initialize database file
function initDatabase() {
    const dbDir = path.dirname(DB_FILE);
    if (!fs.existsSync(dbDir)) {
        fs.mkdirSync(dbDir, { recursive: true });
    }
    
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
        fs.writeFileSync(DB_FILE, JSON.stringify(defaultUsers, null, 2));
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
        icon: path.join(__dirname, 'assets/icon.png'),
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
        fs.writeFileSync(DB_FILE, JSON.stringify(data, null, 2));

        return { 
            success: true, 
            message: 'Login successful',
            token: sessionToken,
            username: username
        };
    } catch (error) {
        return { success: false, message: error.message };
    }
});

ipcMain.handle('create-user', async (event, username, password, email) => {
    try {
        if (!username || !password || !email) {
            return { success: false, message: 'All fields required' };
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
        fs.writeFileSync(DB_FILE, JSON.stringify(data, null, 2));

        return { success: true, message: 'User created successfully' };
    } catch (error) {
        return { success: false, message: error.message };
    }
});

ipcMain.handle('get-ethical-guidelines', async () => {
    try {
        const guidelinesFile = '/opt/payforge/config/ethical_guidelines.md';
        if (fs.existsSync(guidelinesFile)) {
            return fs.readFileSync(guidelinesFile, 'utf8');
        }
        return 'Ethical Guidelines not found';
    } catch (error) {
        return 'Error loading guidelines: ' + error.message;
    }
});

ipcMain.handle('launch-console', async () => {
    const { spawn } = require('child_process');
    spawn('bash', ['-c', 'payforge console'], { detached: true });
    app.quit();
});
