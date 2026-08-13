const { app, BrowserWindow, ipcMain, shell } = require("electron");
const path = require("path");
const fs = require("fs");
const axios = require("axios");
const chokidar = require("chokidar");

let mainWindow;
const watchersAtivos = new Map();

function createWindow() {
    // Configurações de segurança para permitir carregamento de arquivo local em ASAR
    const isPackaged = app.isPackaged;

    const commonWebPreferences = {
        preload: path.join(__dirname, "preload.cjs"),
        nodeIntegration: false,
        contextIsolation: true,
        plugins: true, // Para o leitor de PDF nativo
    };

    // ADICIONE ESTAS DUAS LINHAS PARA PRODUÇÃO (CONTOURNO DE SEGURANÇA)
    // Elas desativam a sandbox de arquivo e o isolamento de recurso de arquivo.
    // Usamos apenas em produção e apenas na janela principal para diagnóstico final.
    if (isPackaged) {
        commonWebPreferences.webSecurity = false; // Desativa bloqueios de Cross-Origin e File Access
        commonWebPreferences.sandbox = false;     // Desativa a sandbox de arquivo do navegador
    }

    mainWindow = new BrowserWindow({
        width: 1200,
        height: 800,
        webPreferences: commonWebPreferences,
    });

    if (isPackaged) {
        // Carrega o arquivo local com caminho absoluto robusto
        mainWindow.loadFile(path.join(app.getAppPath(), "dist", "index.html"));
        
        // REATIVE O DEVTOOLS PARA DIAGNÓSTICO PERMANENTE EM PRODUÇÃO
        // mainWindow.webContents.openDevTools(); 
    } else {
        const devUrl = process.env.ELECTRON_START_URL || "http://localhost:5173";
        mainWindow.loadURL(devUrl);
    }
}

app.whenReady().then(createWindow);

app.on("window-all-closed", () => {
    if (process.platform !== "darwin") app.quit();
});

// =========================================================================
// HANDLER: ABRIR COM NATIVO + FILE WATCHER (CTRL + S)
// =========================================================================
ipcMain.handle("abrir-com-nativo", async (_, { driveFileId, nomeArquivo, token, apiBaseURL }) => {
    try {
        const pastaTemp = path.join(app.getPath("documents"), ".sistema_docs_temp");
        const caminhoArquivoLocal = path.join(pastaTemp, nomeArquivo);

        // 💡 Garante que a subpasta exata do arquivo exista no disco
        const pastaPaiDoArquivo = path.dirname(caminhoArquivoLocal);
        if (!fs.existsSync(pastaPaiDoArquivo)) {
            fs.mkdirSync(pastaPaiDoArquivo, { recursive: true });
        }

        // 1. Download do arquivo via FastAPI
        const response = await axios.get(`${apiBaseURL}/documentos/${driveFileId}/download-temp`, {
            headers: { Authorization: `Bearer ${token}` },
            responseType: "arraybuffer",
        });

        fs.writeFileSync(caminhoArquivoLocal, Buffer.from(response.data));

        // 2. EXCEÇÃO DE ABERTURA INTELIGENTE
        const extensao = path.extname(nomeArquivo).toLowerCase();

        if (extensao === ".pdf") {
            // 📄 ABRE O PDF EM UMA JANELA INTERNA DO ELECTRON
            const pdfWindow = new BrowserWindow({
                width: 1000,
                height: 800,
                title: path.basename(nomeArquivo),
                autoHideMenuBar: true,
                webPreferences: {
                    plugins: true, // Habilita o leitor de PDF nativo do Chromium
                    contextIsolation: true,
                },
            });

            // Usar loadFile previne erros com espaços e parênteses no caminho
            pdfWindow.loadFile(caminhoArquivoLocal);
        } else {
            // OUTROS ARQUIVOS (.docx, .xlsx, .py, vídeos, etc.): Abrem no app padrão do SO
            const erroAbertura = await shell.openPath(caminhoArquivoLocal);
            if (erroAbertura) {
                console.warn("⚠️ Não foi possível abrir o arquivo diretamente:", erroAbertura);
                shell.showItemInFolder(caminhoArquivoLocal);
            }
        }

        // 3. Gerenciamento do Chokidar (Sincronização em tempo real)
        if (watchersAtivos.has(caminhoArquivoLocal)) {
            watchersAtivos.get(caminhoArquivoLocal).close();
        }

        const watcher = chokidar.watch(caminhoArquivoLocal, {
            persistent: true,
            ignoreInitial: true,
            awaitWriteFinish: {
                stabilityThreshold: 1000,
                pollInterval: 100,
            },
        });

        watcher.on("change", async () => {
            console.log(`✏️ [CHOKIDAR] Alteração detectada em: ${nomeArquivo}`);

            try {
                const fileBuffer = fs.readFileSync(caminhoArquivoLocal);
                const formData = new FormData();
                const blob = new Blob([fileBuffer]);
                formData.append("file", blob, path.basename(nomeArquivo));

                await axios.put(`${apiBaseURL}/documentos/${driveFileId}/sincronizar`, formData, {
                    headers: {
                        Authorization: `Bearer ${token}`,
                        "Content-Type": "multipart/form-data",
                    },
                });

                console.log("✅ [CHOKIDAR] Arquivo atualizado com sucesso no Drive!");
                
                if (mainWindow) {
                    mainWindow.webContents.send("sync-status", {
                        success: true,
                        nomeArquivo: path.basename(nomeArquivo)
                    });
                }
            } catch (err) {
                console.error("❌ [CHOKIDAR] Erro ao sincronizar:", err);
                
                if (mainWindow) {
                    mainWindow.webContents.send("sync-status", {
                        success: false,
                        nomeArquivo: path.basename(nomeArquivo),
                        error: err.message
                    });
                }
            }
        }); 

        watchersAtivos.set(caminhoArquivoLocal, watcher);
        
        return { success: true };
    } catch (error) {
        console.error("Erro no manipulador 'abrir-com-nativo':", error);
        return { success: false, error: error.message };
    }
});

// Rotina para limpar arquivos antigos da pasta temporária ao fechar o sistema
app.on("before-quit", () => {
    try {
        const pastaTemp = path.join(app.getPath("documents"), ".sistema_docs_temp");
        if (fs.existsSync(pastaTemp)) {
            fs.rmSync(pastaTemp, { recursive: true, force: true });
            console.log("🧹 Pasta temporária limpa com sucesso!");
        }
    } catch (err) {
        console.error("Erro ao limpar pasta temporária:", err);
    }
});
