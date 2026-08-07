import "./Navbar.css";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import { usuarioService } from "../../../services/usuario";
import type { Usuario } from "../../../types/usuario";
export default function Navbar() {
    const location = useLocation();
    const navigate = useNavigate();
    
    // 🎯 Estado para guardar o usuário logado
    const [usuarioLogado, setUsuarioLogado] = useState<Usuario | null>(null);
    
    useEffect(() => {carregarUsuarioLogado();}, []);

    async function carregarUsuarioLogado() {
        try {
            const dados = await usuarioService.obterMe();
            setUsuarioLogado(dados);
        } catch (error) {
            console.error("Erro ao carregar dados do usuário no Navbar:", error);
        }
    }
    
    function logout() {
        localStorage.removeItem("access_token");
        navigate("/");
    }


    // Helper para transformar o ENUM ("ADMIN", "ESTAGIARIO") em um texto legível
    function formatarPerfil(perfil?: string) {
        switch (perfil) {
            case "ADMIN":
                return "Administrador";
            case "ESTAGIARIO":
                return "Estagiário";
            case "EXTERNO":
                return "Acesso Externo";
            default:
                return perfil || "";
        }
    }    

    return (
        <header className="navbar">

            <div className="navbar-logo">

                <h2>Management System</h2>

            </div>

            <nav className="navbar-menu">

                <Link
                    to="/dashboard"
                    className={
                        location.pathname === "/dashboard"
                            ? "active"
                            : ""
                    }
                >
                    Dashboard
                </Link>

                <Link
                    to="/documentos"
                    className={
                        location.pathname === "/documentos"
                            ? "active"
                            : ""
                    }
                >
                    Documentos
                </Link>

                <Link
                    to="/usuarios"
                    className={
                        location.pathname === "/usuarios"
                            ? "active"
                            : ""
                    }
                >
                    Usuarios
                </Link>

                <Link
                    to="/configuracoes"
                    className={
                        location.pathname === "/configuracoes"
                            ? "active"
                            : ""
                    }
                >
                    Configurações
                </Link>

            </nav>

            <div className="navbar-user">
                {/* 🎯 Exibe o Nome e o Perfil dinamicamente */}
                <span>
                    {usuarioLogado
                        ? `${usuarioLogado.nome} (${formatarPerfil(usuarioLogado.perfil)})`
                        : "Carregando..."}
                </span>

                <button onClick={logout}>Sair</button>
            </div>

        </header>
    );
}