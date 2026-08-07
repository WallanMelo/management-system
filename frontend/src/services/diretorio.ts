import api from "../api/api";

export async function listarConteudo(parentId?: string | null) {
    const url = parentId
        ? `/diretorios/conteudo/${parentId}`
        : `/diretorios/conteudo`;

    const response = await api.get(url);
    return response.data;
}

export async function criarPasta(nome: string, parentId?: string | null) {
    const response = await api.post("/diretorios/criar", { nome, parent_id: parentId });
    return response.data;
}

// 🎯 Dica: Aceitando 'number | string' evita erros de tipagem do TypeScript
export async function excluirPasta(id: number | string) { 
    const response = await api.delete(`/diretorios/${id}`);
    return response.data;
}

// 🎯 Dica: Aceitando 'number | string' evita erros de tipagem do TypeScript
export async function renomearPasta(id: number | string, nome: string) {
    const response = await api.patch(`/diretorios/${id}/renomear`, { nome });
    return response.data;
}

export async function downloadPasta(id: string | number) {
    // IMPORTANTE: responseType: "blob" é essencial para arquivos!
    const response = await api.get(`/diretorios/${id}/download`, {responseType: "blob", });
    
    return response.data; // Retorna o blob para o FileExplorer
}