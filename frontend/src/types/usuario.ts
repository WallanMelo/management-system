export interface Usuario {
  id: number;
  nome: string;
  email: string;
  perfil: string;
  ativo: boolean;
  ultimo_login?: string;
}

export interface UsuarioCreateData {
  nome: string;
  email: string;
  senha: string;
  perfil: string;
  ativo?: boolean;
}