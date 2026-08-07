// src/services/configuracoes.ts
import api from "../api/api";

export interface PerfilUsuario {
    nome: string;
    email: string;
}

export interface AlterarSenhaData {
    senha_atual: string;
    nova_senha: string;
}

export async function obterPerfil() {
    const response = await api.get("/usuarios/me");
    return response.data;
}

export async function atualizarPerfil(dados: PerfilUsuario) {
    const response = await api.put("/usuarios/me", dados);
    return response.data;
}


export async function alterarSenha(dados: AlterarSenhaData) {
    const response = await api.put("/usuarios/alterar-senha", dados);
    return response.data;
}