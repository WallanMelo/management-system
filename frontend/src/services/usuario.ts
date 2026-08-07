import api from "../api/api";
import type { Usuario, UsuarioCreateData } from "../types/usuario"; 

export const usuarioService = {

  obterMe: async (): Promise<Usuario> => {
    const response = await api.get("/usuarios/me");
    return response.data;
  },

  listar: async (): Promise<Usuario[]> => {
    const response = await api.get("/usuarios/");
    return response.data;
  },

  criar: async (dados: UsuarioCreateData): Promise<Usuario> => {
    const response = await api.post("/usuarios/", dados);
    return response.data;
  },

  atualizar: async (id: number, dados: Partial<UsuarioCreateData>): Promise<Usuario> => {
    const response = await api.put(`/usuarios/${id}`, dados);
    return response.data;
  },

  excluir: async (id: number): Promise<void> => {
    await api.delete(`/usuarios/${id}`);
  },
};