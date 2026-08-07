import { useEffect, useState } from "react";
import "./Usuarios.css";
import { usuarioService } from "../../services/usuario";
import type { Usuario, UsuarioCreateData } from "../../types/usuario";
import Navbar from "../../components/layout/Navbar/Navbar";

export default function Usuarios() {
  const [usuarios, setUsuarios] = useState<Usuario[]>([]);
  const [loading, setLoading] = useState(true);
  const [erro, setErro] = useState<string | null>(null);

  // Estados do Modal de Novo Usuário
  const [modalAberto, setModalAberto] = useState(false);
  const [novoNome, setNovoNome] = useState("");
  const [novoEmail, setNovoEmail] = useState("");
  const [novaSenha, setNovaSenha] = useState("");
  const [novoPerfil, setNovoPerfil] = useState("ADMIN");
  const [salvando, setSalvando] = useState(false);

  useEffect(() => {
    carregarUsuarios();
  }, []);

  async function carregarUsuarios() {
    try {
      setLoading(true);
      const lista = await usuarioService.listar();
      setUsuarios(lista);
      setErro(null);
    } catch (error: any) {
      setErro("Falha ao carregar lista de usuários.");
    } finally {
      setLoading(false);
    }
  }

  async function handleCriarUsuario(e: React.FormEvent) {
    e.preventDefault();
    setSalvando(true);
    setErro(null);

    try {
      const payload: UsuarioCreateData = {
        nome: novoNome,
        email: novoEmail,
        senha: novaSenha,
        perfil: novoPerfil,
      };

      await usuarioService.criar(payload);
      setModalAberto(false);
      
      // Limpa os campos
      setNovoNome("");
      setNovoEmail("");
      setNovaSenha("");
      
      // Recarrega a tabela
      await carregarUsuarios();
    } catch (error: any) {
      const msg = error.response?.data?.detail || "Erro ao criar usuário.";
      setErro(msg);
    } finally {
      setSalvando(false);
    }
  }

  // 🛡️ MUDANÇA DE STATUS COM CONFIRMAÇÃO
  async function handleToggleStatus(usuario: Usuario) {
    const acao = usuario.ativo ? "DESATIVAR" : "ATIVAR";
    const aviso = usuario.ativo
      ? `Tem certeza que deseja DESATIVAR o usuário "${usuario.nome}"?\n\nEle perderá o acesso ao sistema imediatamente.`
      : `Deseja ATIVAR o acesso para o usuário "${usuario.nome}"?`;

    if (!window.confirm(aviso)) {
      return;
    }

    try {
      await usuarioService.atualizar(usuario.id, { ativo: !usuario.ativo });
      await carregarUsuarios();
    } catch (error) {
      alert("Não foi possível alterar o status do usuário.");
    }
  }

  // 🛡️ EXCLUSÃO COM CONFIRMAÇÃO DETALHADA
  async function handleExcluir(usuario: Usuario) {
    const confirmacao = window.confirm(
      `⚠️ ATENÇÃO: Tem certeza que deseja EXCLUIR permanentemente o usuário "${usuario.nome}"?\n\nEsta ação não poderá ser desfeita.`
    );

    if (confirmacao) {
      try {
        await usuarioService.excluir(usuario.id);
        await carregarUsuarios();
      } catch (error) {
        alert("Erro ao excluir usuário.");
      }
    }
  }

  return (
    <>
      <Navbar />

      <div className="usuarios-container">
        <header className="usuarios-header">
          <div>
            <h1>Gerenciamento de Usuários</h1>
            <p>Cadastre, edite e gerencie o acesso ao sistema</p>
          </div>
          <button className="btn-primary" onClick={() => setModalAberto(true)}>
            + Novo Usuário
          </button>
        </header>

        {erro && <div className="usuarios-error-banner">⚠️ {erro}</div>}

        {loading ? (
          <div className="loading-state">Carregando usuários...</div>
        ) : (
          <div className="table-card">
            <table className="usuarios-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Nome</th>
                  <th>Email</th>
                  <th>Perfil</th>
                  <th>Status</th>
                  <th>Ações</th>
                </tr>
              </thead>
              <tbody>
                {usuarios.map((u) => (
                  <tr key={u.id}>
                    <td>#{u.id}</td>
                    <td><strong>{u.nome}</strong></td>
                    <td>{u.email}</td>
                    <td>
                      <span className="badge badge-perfil">{u.perfil}</span>
                    </td>
                    <td>
                      <span
                        className={`badge ${u.ativo ? "badge-ativo" : "badge-inativo"}`}
                        onClick={() => handleToggleStatus(u)}
                        title="Clique para alternar status"
                        style={{ cursor: "pointer" }}
                      >
                        {u.ativo ? "Ativo" : "Inativo"}
                      </span>
                    </td>
                    <td>
                      <button
                        className="btn-danger-icon"
                        onClick={() => handleExcluir(u)} // 👈 Passando o objeto 'u' completo
                        title="Excluir Usuário"
                      >
                        🗑️
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* MODAL DE CRIAÇÃO */}
        {modalAberto && (
          <div className="modal-overlay">
            <div className="modal-card">
              <h2>Cadastrar Novo Usuário</h2>
              <form onSubmit={handleCriarUsuario}>
                <div className="input-group">
                  <label>Nome Completo</label>
                  <input
                    type="text"
                    required
                    value={novoNome}
                    onChange={(e) => setNovoNome(e.target.value)}
                  />
                </div>

                <div className="input-group">
                  <label>E-mail</label>
                  <input
                    type="email"
                    required
                    value={novoEmail}
                    onChange={(e) => setNovoEmail(e.target.value)}
                  />
                </div>

                <div className="input-group">
                  <label>Senha Inicial</label>
                  <input
                    type="password"
                    required
                    value={novaSenha}
                    onChange={(e) => setNovaSenha(e.target.value)}
                  />
                </div>

                <div className="input-group">
                  <label>Perfil de Acesso</label>
                  <select
                    value={novoPerfil}
                    onChange={(e) => setNovoPerfil(e.target.value)}
                  >
                    <option value="ADMIN">Administrador</option>
                    <option value="ESTAGIARIO">Estagiário</option>
                    <option value="EXTERNO">Acesso Externo</option>
                  </select>
                </div>

                <div className="modal-actions">
                  <button
                    type="button"
                    className="btn-secondary"
                    onClick={() => setModalAberto(false)}
                  >
                    Cancelar
                  </button>
                  <button type="submit" className="btn-primary" disabled={salvando}>
                    {salvando ? "Salvando..." : "Salvar Usuário"}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </>
  );
}