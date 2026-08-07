import api from "../api/api";

export async function listarDocumentos() {
    const response = await api.get("/documentos");
    return response.data;
}

export async function uploadDocumento(
    arquivo: File,
    parentId?: string | null
) {
    const form = new FormData();

    // 1. Chave exigida pelo parâmetro "arquivo: UploadFile"
    form.append("arquivo", arquivo);

    // 2. Adiciona parent_id apenas se houver uma pasta válida selecionada
    if (
        parentId &&
        parentId !== "null" &&
        parentId !== "undefined"
    ) {
        form.append("parent_id", String(parentId));
    }

    const response = await api.post("/documentos/upload", form, {
        headers: {
            "Content-Type": "multipart/form-data",
        },
    });

    return response.data;
}

// ========= FUNÇÃO PARA EXCLUIR DOCUMENTO =============================
export async function excluirDocumento(id: number) {
    await api.delete(`/documentos/${id}`);
}

// ========= FUNÇÃO P/ RENOMEAR DOCUMENTO =============================
export async function renomearDocumento(id: number, novoNome: string) {
    // Ajustado para coincidir com o FastAPI: PATCH /documentos/{id}/renomear
    const response = await api.patch(`/documentos/${id}/renomear`, {
        novo_nome: novoNome,
    });
    return response.data;
}

// ========= FUNÇÃO PARA DOWNLOAD DO DOCUMENTO =============================
export async function downloadDocumento(id: number) {
    const response = await api.get(`/documentos/${id}/download`, {
        responseType: "blob", // 👈 Fundamental para o Axios entender que é um arquivo e não JSON
    });
    return response.data;
}

// ========= FUNÇÃO PARA SINCRONIZAR COM GOOGLE DRIVE ======================
export async function sincronizarComGoogleDrive() {
    const response = await api.get("/documentos/sincronizar-drive");
    return response.data;
}