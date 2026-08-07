export interface ElectronAPI {
    abrirComNativo: (dados: {
        driveFileId: string;
        nomeArquivo: string;
        token: string;
        apiBaseURL: string;
    }) => Promise<{ success: boolean; error?: string }>;

    onSyncStatus: (callback: (dados: { success: boolean; nomeArquivo: string; error?: string }) => void) => void;
}

declare global {
    interface Window {
        electronAPI?: ElectronAPI;
    }
}