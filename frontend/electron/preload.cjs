const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("electronAPI", {
    abrirComNativo: (dados) => ipcRenderer.invoke("abrir-com-nativo", dados),
    
    // 🌟 NOVA FUNÇÃO: Permite ao React escutar eventos de sincronização
    onSyncStatus: (callback) => ipcRenderer.on("sync-status", (_event, data) => callback(data))
});