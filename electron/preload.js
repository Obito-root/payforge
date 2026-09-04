const { contextBridge, ipcMain, ipcRenderer } = require('electron');

// Expose secure API to renderer process
contextBridge.exposeInMainWorld('payforgeAPI', {
    checkCredentials: (username, password) => 
        ipcRenderer.invoke('check-credentials', username, password),
    
    createUser: (username, password, email) => 
        ipcRenderer.invoke('create-user', username, password, email),
    
    getEthicalGuidelines: () => 
        ipcRenderer.invoke('get-ethical-guidelines'),
    
    launchConsole: () => 
        ipcRenderer.invoke('launch-console'),
    
    closeApp: () => {
        const { app } = require('electron').remote;
        app.quit();
    }
});
