import { Navigate, Outlet } from "react-router-dom";

export default function ProtectedRoute() {
  const token = localStorage.getItem("access_token");

  // Se não houver token, redireciona o usuário para o login
  if (!token) {return <Navigate to="/login" replace />;}

  // Se o token existe, renderiza as rotas filhas (documentos, configuracoes, etc.)
  return <Outlet />;
}