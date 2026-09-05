// electron/main.js
// Robust Electron auth initializer with permission-safe DB file handling.

const { app, BrowserWindow, ipcMain } = require('electron');
const fs = require('fs');
const os = require('os');
const path = require('path');

function getPayforgeHome() {
  // Priority: PAYFORGE_HOME env -> XDG_CONFIG_HOME/payforge -> ~/.payforge
  if (process.env.PAYFORGE_HOME) return process.env.PAYFORGE_HOME;
  if (process.env.XDG_CONFIG_HOME) return path.join(process.env.XDG_CONFIG_HOME, 'payforge');
  return path.join(os.homedir(), '.payforge');
}

function safeWriteJson(filePath, data, opts = {}) {
  const defaultOpts = { encoding: 'utf8', mode: 0o600 };
  const writeOpts = Object.assign({}, defaultOpts, opts);
  fs.writeFileSync(filePath, JSON.stringify(data, null, 2), writeOpts);
}

function initDatabase() {
  const payforgeHome = getPayforgeHome();
  let dbPath = path.join(payforgeHome, 'auth.json');

  // Ensure directory exists with conservative permissions
  try {
    fs.mkdirSync(payforgeHome, { recursive: true, mode: 0o700 });
  } catch (err) {
    console.error('[!] Failed to create directory %s: %s', payforgeHome, err && err.message);
    // try to continue — we'll attempt fallbacks below
  }

  // Try to create the DB/auth file if missing
  const defaultData = { users: [], meta: { created: new Date().toISOString() } };
  try {
    if (!fs.existsSync(dbPath)) {
      safeWriteJson(dbPath, defaultData);
    }
    console.log('[*] Database path:', dbPath);
    console.log('[*] PayForge Electron Auth System initialized');
    return dbPath;
  } catch (err) {
    console.error('[!] Error creating database: %s', err && err.stack ? err.stack : err);
    // EACCES fallback: try alternate locations
    if (err && err.code === 'EACCES') {
      // Prefer /opt/payforge/database if installed system-wide and writable
      const altDir = process.env.PAYFORGE_ALT || '/opt/payforge/database';
      try {
        fs.mkdirSync(altDir, { recursive: true });
        const altPath = path.join(altDir, 'auth.json');
        safeWriteJson(altPath, defaultData);
        console.warn('[!] Permission on user config prevented writing. Using alternate path:', altPath);
        return altPath;
      } catch (altErr) {
        console.error('[!] Alternate path write failed:', altErr && altErr.message);
      }

      // Final fallback to system temp dir
      try {
        const tmpDir = os.tmpdir();
        const tmpPath = path.join(tmpDir, `payforge-auth-${Date.now()}.json`);
        safeWriteJson(tmpPath, defaultData);
        console.warn('[!] Falling back to temp auth file:', tmpPath);
        return tmpPath;
      } catch (tmpErr) {
        console.error('[!] Temporary file fallback failed:', tmpErr && tmpErr.message);
      }
    }

    // If we get here, initialization failed entirely — return null so caller can handle it
    return null;
  }
}

let mainWindow;
let authDbPath = null;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 900,
    height: 700,
    webPreferences: {
      contextIsolation: true,
      nodeIntegration: false,
      preload: path.join(__dirname, 'preload.js'),
    },
  });

  mainWindow.loadFile(path.join(__dirname, 'src', 'login.html')).catch(err => {
    console.error('[!] Failed to load login.html:', err && err.message);
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

app.whenReady().then(() => {
  authDbPath = initDatabase();
  if (!authDbPath) {
    // Show a dialog in real app; for now log and continue (login UI should show an error)
    console.error('[!] Auth DB initialization failed; login may not work.');
  }
  createWindow();

  app.on('activate', function () {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', function () {
  if (process.platform !== 'darwin') app.quit();
});

// Provide DB path to renderer upon request
ipcMain.handle('payforge:get-auth-db-path', async () => {
  return authDbPath;
});
