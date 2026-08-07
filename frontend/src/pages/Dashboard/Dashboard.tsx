import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import Navbar from "../../components/layout/Navbar/Navbar";
import { usuarioService } from "../../services/usuario";
import { listarDocumentos, sincronizarComGoogleDrive } from "../../services/documento"; 
import "./Dashboard.css";

// ⏱️ Função auxiliar para transformar o tempo em texto amigável
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

const CACHE_KEY = "dashboard_metrics_cache";

export default function Dashboard() {
  // 📦 Recupera os dados em cache no momento da criação do estado
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
  
  // 🎯 Só exibe "..." (loading) se NÃO houver nenhum cache armazenado
  const [loading, setLoading] = useState<boolean>(!cacheSalvo);
  // 🎯 Estado sutil para indicar atualização silenciosa em segundo plano
  const [atualizando, setAtualizando] = useState<boolean>(false);

  // 🎯 ESTADOS DO GOOGLE DRIVE
  const [driveConectado, setDriveConectado] = useState<boolean>(cacheSalvo?.driveConectado ?? false);
  const [driveStatusTexto, setDriveStatusTexto] = useState<string>(
    cacheSalvo?.driveStatusTexto ?? "Verificando..."
  );

  // 🎯 Data/Hora da última sincronização
  const [ultimaSincronizacao, setUltimaSincronizacao] = useState<Date | null>(
    cacheSalvo?.ultimaSincronizacao ? new Date(cacheSalvo.ultimaSincronizacao) : null
  );
  const [tempoTexto, setTempoTexto] = useState<string>("carregando...");

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

      // 1. Busca Usuários do banco
      const listaUsuarios = await usuarioService.listar();
      const totalU = listaUsuarios.length;
      const ativosU = listaUsuarios.filter((u) => u.ativo).length;

      // 2. Busca Documentos do banco
      const listaDocs = await listarDocumentos();
      const totalD = listaDocs.length;

      // 3. ☁️ Checa a saúde da integração com o Google Drive
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

      // 🔄 Atualiza estados com os novos dados
      setTotalUsuarios(totalU);
      setUsuariosAtivos(ativosU);
      setTotalDocumentos(totalD);
      setDriveConectado(driveOk);
      setDriveStatusTexto(driveTxt);
      setUltimaSincronizacao(agora);

      // 💾 Salva a foto atual no cache
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

              <Link to="/usuarios" className="action-btn">
                <span>👥</span>
                <div>
                  <strong>Cadastrar Usuário</strong>
                  <p>Adicione novos administradores ou operadores</p>
                </div>
              </Link>

              <Link to="/configuracoes" className="action-btn">
                <span>⚙️</span>
                <div>
                  <strong>Configurações do Perfil</strong>
                  <p>Altere sua senha e preferência de tema</p>
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