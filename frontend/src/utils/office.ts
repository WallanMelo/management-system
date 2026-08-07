// src/utils/office.ts
import api from "../api/api"; // 👈 Importa sua api configurada

interface Arquivo {
    id: string;
    drive_file_id: string;
    nome: string;
}

export function abrirNoOfficeDesktop(arquivo: Arquivo) {
    const extensao = arquivo.nome.split('.').pop()?.toLowerCase();
    
    const token = localStorage.getItem("access_token");

    if (!token) {
        alert("Você precisa estar logado para abrir o arquivo.");
        return;
    }

    // 🌟 AQUI ESTÁ O TRUQUE: Pegamos a baseURL direto do seu Axios!
    // Assim, se você mudar o backend de lugar, não precisa alterar aqui.
    const baseURL = api.defaults.baseURL; 
    
    // O token vai na URL para que o Word consiga enviar para o seu FastAPI
    const urlWebDAV = `${baseURL}/api/webdav/${arquivo.drive_file_id}/${encodeURIComponent(arquivo.nome)}?token=${token}`;

    let esquemaProtocolo = "";

    if (extensao === "docx" || extensao === "doc") {
        esquemaProtocolo = `ms-word:ofe|u|${urlWebDAV}`;
    } else if (extensao === "xlsx" || extensao === "xls") {
        esquemaProtocolo = `ms-excel:ofe|u|${urlWebDAV}`;
    } else if (extensao === "pptx" || extensao === "ppt") {
        esquemaProtocolo = `ms-powerpoint:ofe|u|${urlWebDAV}`;
    } else {
        alert("Este formato não suporta edição direta no Office Desktop.");
        return;
    }

    // Dispara o redirecionamento para o Sistema Operacional abrir o app
    window.location.href = esquemaProtocolo;
}