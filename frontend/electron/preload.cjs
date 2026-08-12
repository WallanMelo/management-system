const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("electronAPI", {
    abrirComNativo: (dados) => ipcRenderer.invoke("abrir-com-nativo", dados),
    
    // funct que permite o react escutar eventos de sincronização
    onSyncStatus: (callback) => ipcRenderer.on("sync-status", (_event, data) => callback(data))
});