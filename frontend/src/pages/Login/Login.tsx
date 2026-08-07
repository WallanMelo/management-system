import "./Login.css";
import { useState } from "react";
import { login } from "../../services/auth";
import { useNavigate } from "react-router-dom";
import '../../styles/global.css'

export default function Login() {
  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const [erro, setErro] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const navigate = useNavigate();

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    setErro(null);
    setLoading(true);

    try {
      await login({ email, senha });
      navigate("/documentos"); // Após o login joga o usuário para o dashboard
    } catch (error: any) {
      console.error("Erro no login:", error);
      
      // Captura a mensagem vinda do FastAPI (ex: "E-mail ou senha incorretos") ou exibe uma mensagem padrão
      const mensagemErro = 
        error.response?.data?.detail || 
        "E-mail ou senha incorretos. Verifique suas credenciais.";
      
      setErro(mensagemErro);
      setSenha(""); // limpa o campo de senha se o login falhar
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="login-container">
      <form className="login-card" onSubmit={handleLogin}>
        <h1>Management System</h1>
        <p>Faça login para continuar</p>

        {/* 🌟 MENSAGEM DE ERRO COM FEEDBACK VISUAL */}
        {erro && (
          <div className="login-error-banner">
            <span>⚠️ {erro}</span>
          </div>
        )}

        <div className="input-group">
          <label>Email</label>
          <input
            type="email"
            placeholder="Digite seu email"
            value={email}
            onChange={(e) => {
              setEmail(e.target.value);
              if (erro) setErro(null); // Limpa a mensagem ao começar a digitar
            }}
            required
          />
        </div>

        <div className="input-group">
          <label>Senha</label>
          <input
            type="password"
            placeholder="Digite sua senha"
            value={senha}
            onChange={(e) => {
              setSenha(e.target.value);
              if (erro) setErro(null); // Limpa a mensagem ao começar a digitar
            }}
            required
          />
        </div>

        <button type="submit" disabled={loading}>
          {loading ? "Entrando..." : "Entrar"}
        </button>
      </form>
    </div>
  );
}