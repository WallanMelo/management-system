import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import Navbar from "../../components/layout/Navbar/Navbar";
import { usuarioService } from "../../services/usuario";
import { listarDocumentos, sincronizarComGoogleDrive } from "../../services/documento"; 
import "./Dashboard.css";

function formatarTempoRelativo(data: Date | null): string {
  if (!data) return "carregando...";

  const agora = new Date();
  const segundos = Math.floor((agora.getTime() - data.getTime()) / 1000);

  if (segundos < 10) return "há poucos segundos";
  if (segundos < 60) return `há ${segundos} segundo${segundos > 1 ? "s" : ""}`;

  const minutos = Math.floor(segundos / 60);
  if (minutos < 60) return `há ${minutos} minuto${minutos > 1 ? "s" : ""}`;

  const horas = Math.floor(minutos / 60);
  if (horas < 24) return `há ${horas} hora${horas > 1 ? "s" : ""}`;

  const dias = Math.floor(horas / 24);
  return `há ${dias} dia${dias > 1 ? "s" : ""}`;
}

// Decodifica as informações contidas no JWT (access_token)
function obterDadosDoToken(): any {
  try {
    const token = localStorage.getItem("access_token");
    if (!token) return null;

    const base64Url = token.split(".")[1];
    if (!base64Url) return null;

    const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
    const jsonPayload = decodeURIComponent(
      window
        .atob(base64)
        .split("")
        .map((c) => "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2))
        .join("")
    );

    return JSON.parse(jsonPayload);
  } catch (error) {
    console.error("Erro ao decodificar token JWT:", error);
    return null;
  }
}

const CACHE_KEY = "dashboard_metrics_cache";

export default function Dashboard() {
  const cacheSalvo = (() => {
    try {
      const dados = localStorage.getItem(CACHE_KEY);
      return dados ? JSON.parse(dados) : null;
    } catch {
      return null;
    }
  })();

  const [totalUsuarios, setTotalUsuarios] = useState<number>(cacheSalvo?.totalUsuarios ?? 0);
  const [usuariosAtivos, setUsuariosAtivos] = useState<number>(cacheSalvo?.usuariosAtivos ?? 0);
  const [totalDocumentos, setTotalDocumentos] = useState<number>(cacheSalvo?.totalDocumentos ?? 0);
  const [isDarkMode, setIsDarkMode] = useState<boolean>(false);
  
  const [loading, setLoading] = useState<boolean>(!cacheSalvo);
  const [atualizando, setAtualizando] = useState<boolean>(false);

  const [driveConectado, setDriveConectado] = useState<boolean>(cacheSalvo?.driveConectado ?? false);
  const [driveStatusTexto, setDriveStatusTexto] = useState<string>(
    cacheSalvo?.driveStatusTexto ?? "Verificando..."
  );

  const [ultimaSincronizacao, setUltimaSincronizacao] = useState<Date | null>(cacheSalvo?.ultimaSincronizacao ? new Date(cacheSalvo.ultimaSincronizacao) : null);
  const [tempoTexto, setTempoTexto] = useState<string>("carregando...");

  // Tenta obter o usuário do localStorage ou decodifica diretamente do access_token
  const usuarioLogado = (() => {
    try {
      const raw = localStorage.getItem("usuario") || localStorage.getItem("user");
      if (raw) return JSON.parse(raw);
    } catch {}
    return obterDadosDoToken();
  })();

  // Extrai o perfil independentemente da chave usada no token ou objeto
  const perfilTexto = String(
    usuarioLogado?.perfil || 
    usuarioLogado?.perfil_usuario || 
    usuarioLogado?.perfilUsuario || 
    usuarioLogado?.role || 
    usuarioLogado?.tipo || 
    usuarioLogado?.cargo || 
    ""
  ).toUpperCase();

  // Valida permissão administrativa
  const isAdmin = 
    perfilTexto.includes("ADMIN") || 
    usuarioLogado?.is_admin === true || 
    usuarioLogado?.admin === true;

  console.log("DEBUG DASHBOARD:", { usuarioLogado, perfilTexto, isAdmin });

  useEffect(() => {
    carregarMetricas();

    const temaSalvo = localStorage.getItem("tema");
    setIsDarkMode(temaSalvo === "dark");
  }, []);

  useEffect(() => {
    if (!ultimaSincronizacao) return;

    setTempoTexto(formatarTempoRelativo(ultimaSincronizacao));

    const timer = setInterval(() => {
      setTempoTexto(formatarTempoRelativo(ultimaSincronizacao));
    }, 1000);

    return () => clearInterval(timer);
  }, [ultimaSincronizacao]);

  async function carregarMetricas() {
    try {
      if (!cacheSalvo) {
        setLoading(true);
      } else {
        setAtualizando(true);
      }

      const listaUsuarios = await usuarioService.listar();
      const totalU = listaUsuarios.length;
      const ativosU = listaUsuarios.filter((u) => u.ativo).length;

      const listaDocs = await listarDocumentos();
      const totalD = listaDocs.length;

      let driveOk = false;
      let driveTxt = "";

      try {
        await sincronizarComGoogleDrive(); 
        driveOk = true;
        driveTxt = "Sincronização em tempo real";
      } catch (driveError) {
        console.warn("Falha na conexão com o Google Drive:", driveError);
        driveOk = false;
        driveTxt = "Falha na sincronização ou desconectado";
      }

      const agora = new Date();

      setTotalUsuarios(totalU);
      setUsuariosAtivos(ativosU);
      setTotalDocumentos(totalD);
      setDriveConectado(driveOk);
      setDriveStatusTexto(driveTxt);
      setUltimaSincronizacao(agora);

      localStorage.setItem(
        CACHE_KEY,
        JSON.stringify({
          totalUsuarios: totalU,
          usuariosAtivos: ativosU,
          totalDocumentos: totalD,
          driveConectado: driveOk,
          driveStatusTexto: driveTxt,
          ultimaSincronizacao: agora.toISOString(),
        })
      );

    } catch (error) {
      console.error("Erro ao carregar métricas do dashboard:", error);
    } finally {
      setLoading(false);
      setAtualizando(false);
    }
  }

  // Redireciona para o fluxo OAuth2 do Backend
  function handleConectarGoogleDrive() {
    const authUrl = "https://management-system-6bb0.onrender.com/integracoes/google/login";
    
    if ((window as any).electronAPI?.openExternal) {
      (window as any).electronAPI.openExternal(authUrl);
    } else {
      window.open(authUrl, "_blank");
    }
  }

  return (
    <>
      <Navbar />

      <div className="dashboard-container">
        <header className="dashboard-header">
          <h1>Painel Geral</h1>
          <p>
            Bem-vindo ao Management System. Confira o resumo do seu ambiente.
            {atualizando && <small style={{ marginLeft: "10px", opacity: 0.7 }}>🔄 Atualizando...</small>}
          </p>
        </header>

        {/* CARTÕES DE ESTATÍSTICAS */}
        <section className="dashboard-grid">
          <div className="stat-card">
            <div className="stat-icon">📄</div>
            <div className="stat-info">
              <h3>Documentos</h3>
              <span className="stat-value">
                {loading ? "..." : totalDocumentos}
              </span>
              <p className="stat-description">Arquivos sincronizados</p>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">👥</div>
            <div className="stat-info">
              <h3>Usuários</h3>
              <span className="stat-value">
                {loading ? "..." : usuariosAtivos}
              </span>
              <p className="stat-description">
                {loading
                  ? "Carregando..."
                  : `${totalUsuarios} usuário(s) no total`}
              </p>
            </div>
          </div>

          {/* CARD DINÂMICO DO GOOGLE DRIVE */}
          <div className="stat-card">
            <div className="stat-icon">☁️</div>
            <div className="stat-info">
              <h3>Google Drive</h3>
              <span className={`stat-value ${loading ? "" : driveConectado ? "status-online" : "status-offline"}`}>
                {loading ? "..." : driveConectado ? "Conectado" : "Desconectado"}
              </span>
              <p className="stat-description">{loading ? "Checando conexão..." : driveStatusTexto}</p>
              
              {/* Exibe o botão de ação apenas para Admin */}
              {!loading && isAdmin && (
                <button 
                  onClick={handleConectarGoogleDrive}
                  style={{
                    marginTop: "10px",
                    padding: "6px 12px",
                    fontSize: "0.85rem",
                    borderRadius: "6px",
                    border: "none",
                    backgroundColor: driveConectado ? "#4b5563" : "#2563eb",
                    color: "#ffffff",
                    cursor: "pointer"
                  }}
                >
                  {driveConectado ? "Reconectar Conta" : "Conectar Google Drive"}
                </button>
              )}
            </div>
          </div>
        </section>

        {/* SEÇÃO DE AÇÕES RÁPIDAS E RECENTES */}
        <section className="dashboard-content">
          <div className="dashboard-card main-actions">
            <h2>Atalhos Rápidos</h2>
            <div className="actions-grid">
              <Link to="/documentos" className="action-btn">
                <span>📁</span>
                <div>
                  <strong>Gerenciar Documentos</strong>
                  <p>Acesse o explorador de arquivos e sincronize pasta</p>
                </div>
              </Link>

              {/* Exibe o atalho rápido apenas para Admin */}
              {isAdmin && (
                <button 
                  onClick={handleConectarGoogleDrive} 
                  className="action-btn"
                  style={{ background: "none", border: "none", textAlign: "left", cursor: "pointer", width: "100%" }}
                >
                  <span>☁️</span>
                  <div>
                    <strong>{driveConectado ? "Reconectar Google Drive" : "Conectar Google Drive"}</strong>
                    <p>Autorize a conta master para armazenar os arquivos</p>
                  </div>
                </button>
              )}

              <Link to="/configuracoes" className="action-btn">
                <span>⚙️</span>
                <div>
                  <strong>Configurações</strong>
                  <p>Altere as configurações do Sistema</p>
                </div>
              </Link>

              <Link to="/usuarios" className="action-btn">
                <span>👥</span>
                <div>
                  <strong>Cadastrar Usuário</strong>
                  <p>Adicione novos administradores ou operadores</p>
                </div>
              </Link>
            </div>
          </div>

          <div className="dashboard-card recent-activity">
            <h2>Informações do Sistema</h2>
            <ul className="info-list">
              <li>
                <span className={`bullet ${driveConectado ? "success" : "danger"}`}></span>
                <div>
                  <strong>{driveConectado ? "Sincronização OK" : "Atenção no Google Drive"}</strong>
                  <p>Última checagem realizada {tempoTexto}</p>
                </div>
              </li>
              <li>
                <span className={`bullet ${isDarkMode ? "info" : "success"}`}></span>
                <div>
                  <strong>
                    {isDarkMode ? "Modo Escuro Habilitado" : "Modo Claro Habilitado"}
                  </strong>
                  <p>Tema integrado às variáveis globais</p>
                </div>
              </li>
            </ul>
          </div>
        </section>
      </div>
    </>
  );
}