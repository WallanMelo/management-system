import React, { useState, useEffect } from "react";
import "./Configuracoes.css";
import Navbar from "../../components/layout/Navbar/Navbar"; // 👈 Ajuste o caminho conforme a estrutura da sua pasta
import { obterPerfil, atualizarPerfil, alterarSenha } from "../../services/configuracoes";

export default function Configuracoes() {
    const [abaAtiva, setAbaAtiva] = useState<"perfil" | "aparencia">("perfil");

    // Estados de Perfil
    const [nome, setNome] = useState("");
    const [email, setEmail] = useState("");
    const [loadingPerfil, setLoadingPerfil] = useState(false);

    // 🎯 Estados para Troca de Senha
    const [senhaAtual, setSenhaAtual] = useState("");
    const [novaSenha, setNovaSenha] = useState("");
    const [confirmarSenha, setConfirmarSenha] = useState("");
    const [loadingSenha, setLoadingSenha] = useState(false);

    // Estados de Aparência
    const [temaEscuro, setTemaEscuro] = useState(false);

    // Carrega os dados do perfil vindos do Backend
    useEffect(() => {
        async function carregarDados() {
            try {
                const dados = await obterPerfil();
                setNome(dados.nome || "");
                setEmail(dados.email || "");
            } catch (error) {
                console.error("Erro ao carregar perfil:", error);
            }
        }
        carregarDados();

        // Carrega o tema salvo
        const temaSalvo = localStorage.getItem("tema");
        if (temaSalvo === "dark") {
            setTemaEscuro(true);
            document.body.classList.add("dark-mode");
        }
    }, []);

    // Salva Informações Pessoais
    async function handleSalvarPerfil(e: React.FormEvent) {
        e.preventDefault();
        setLoadingPerfil(true);
        try {
            await atualizarPerfil({ nome, email });
            alert("Perfil atualizado com sucesso!");
        } catch (error: any) {
            console.error("Erro ao salvar perfil:", error);
            const msg = error.response?.data?.detail || "Erro ao atualizar o perfil.";
            alert(msg);
        } finally {
            setLoadingPerfil(false);
        }
    }

    // 🎯 Função para Trocar a Senha
    async function handleTrocarSenha(e: React.FormEvent) {
        e.preventDefault();

        // Validação no Front-end: verifica se as senhas batem
        if (novaSenha !== confirmarSenha) {
            alert("A nova senha e a confirmação não coincidem!");
            return;
        }

        setLoadingSenha(true);
        try {
            await alterarSenha({ senha_atual: senhaAtual, nova_senha: novaSenha });
            alert("Senha alterada com sucesso!");
            
            // Limpa os campos após o sucesso
            setSenhaAtual("");
            setNovaSenha("");
            setConfirmarSenha("");
        } catch (error: any) {
            console.error("Erro ao alterar senha:", error);
            const msg = error.response?.data?.detail || "Erro ao alterar senha.";
            alert(msg);
        } finally {
            setLoadingSenha(false);
        }
    }

    // Alterna Tema
    function handleToggleTema() {
        const novoTema = !temaEscuro;
        setTemaEscuro(novoTema);

        if (novoTema) {
            document.body.classList.add("dark-mode");
            localStorage.setItem("tema", "dark");
        } else {
            document.body.classList.remove("dark-mode");
            localStorage.setItem("tema", "light");
        }
    }

    return (
        <div className="page-wrapper">
            {/* 🎯 Painel Superior / Navbar */}
            <Navbar />

            {/* Conteúdo da Página de Configurações */}
            <div className="configuracoes-container">
                <div className="config-header">
                    <h2>Configurações</h2>
                    <p>Gerencie sua conta e preferências do sistema.</p>
                </div>

                <div className="config-body">
                    {/* MENU LATERAL */}
                    <aside className="config-sidebar">
                        <button 
                            className={abaAtiva === "perfil" ? "active" : ""} 
                            onClick={() => setAbaAtiva("perfil")}
                        >
                            👤 Perfil
                        </button>
                        <button 
                            className={abaAtiva === "aparencia" ? "active" : ""} 
                            onClick={() => setAbaAtiva("aparencia")}
                        >
                            🎨 Aparência
                        </button>
                    </aside>

                    {/* CONTEÚDO DA ABA */}
                    <main className="config-content">
                        {/* --- ABA DE PERFIL --- */}
                        {abaAtiva === "perfil" && (
                            <div>
                                {/* FORMULÁRIO 1: INFORMAÇÕES PESSOAIS */}
                                <div className="config-section">
                                    <h3>Informações Pessoais</h3>
                                    <form onSubmit={handleSalvarPerfil}>
                                        <div className="form-group">
                                            <label>Nome Completo</label>
                                            <input 
                                                type="text" 
                                                value={nome} 
                                                onChange={(e) => setNome(e.target.value)} 
                                                required 
                                            />
                                        </div>
                                        <div className="form-group">
                                            <label>E-mail</label>
                                            <input 
                                                type="email" 
                                                value={email} 
                                                onChange={(e) => setEmail(e.target.value)} 
                                                required 
                                            />
                                        </div>

                                        <button type="submit" className="btn-salvar" disabled={loadingPerfil}>
                                            {loadingPerfil ? "Salvando..." : "Salvar Alterações"}
                                        </button>
                                    </form>
                                </div>

                                {/* FORMULÁRIO 2: SEGURANÇA / TROCA DE SENHA */}
                                <div className="config-section" style={{ marginTop: "32px" }}>
                                    <h3>Alterar Senha</h3>
                                    <form onSubmit={handleTrocarSenha}>
                                        <div className="form-group">
                                            <label>Senha Atual</label>
                                            <input 
                                                type="password" 
                                                value={senhaAtual} 
                                                onChange={(e) => setSenhaAtual(e.target.value)} 
                                                required 
                                            />
                                        </div>
                                        
                                        <div className="form-group">
                                            <label>Nova Senha</label>
                                            <input 
                                                type="password" 
                                                value={novaSenha} 
                                                onChange={(e) => setNovaSenha(e.target.value)} 
                                                minLength={6}
                                                required 
                                            />
                                        </div>

                                        <div className="form-group">
                                            <label>Confirmar Nova Senha</label>
                                            <input 
                                                type="password" 
                                                value={confirmarSenha} 
                                                onChange={(e) => setConfirmarSenha(e.target.value)} 
                                                required 
                                            />
                                        </div>

                                        <button type="submit" className="btn-salvar" disabled={loadingSenha}>
                                            {loadingSenha ? "Atualizando..." : "Alterar Senha"}
                                        </button>
                                    </form>
                                </div>
                            </div>
                        )}

                        {/* --- ABA DE APARÊNCIA --- */}
                        {abaAtiva === "aparencia" && (
                            <div className="config-section">
                                <h3>Personalização</h3>
                                
                                <div className="setting-item">
                                    <div className="setting-info">
                                        <h4>Modo Escuro</h4>
                                        <p>Altera as cores do sistema para reduzir o cansaço visual.</p>
                                    </div>
                                    <div className="setting-action">
                                        <label className="toggle-switch">
                                            <input 
                                                type="checkbox" 
                                                checked={temaEscuro} 
                                                onChange={handleToggleTema} 
                                            />
                                            <span className="slider round"></span>
                                        </label>
                                    </div>
                                </div>
                            </div>
                        )}
                    </main>
                </div>
            </div>
        </div>
    );
}