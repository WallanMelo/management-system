import api from "../api/api";
import type { Documento } from "../types/documento";

export async function executarAbrirCom(doc: Documento) {
    const token = localStorage.getItem("access_token") || "";
    const apiBaseURL = api.defaults.baseURL || "http://localhost:8000";

    if (window.electronAPI) {
        const resultado = await window.electronAPI.abrirComNativo({
            driveFileId: doc.drive_file_id || String(doc.id),
            nomeArquivo: doc.nome_original,
            token,
            apiBaseURL,
        });

        if (!resultado.success) {
            alert(`Erro ao abrir o arquivo: ${resultado.error}`);
        }
    } else {
        alert("A opção 'Abrir com' só funciona na versão Desktop do aplicativo.");
    }
}