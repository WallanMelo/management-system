import { useEffect } from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import Dashboard from "./pages/Dashboard/Dashboard";
import Login from "./pages/Login/Login";
import Documentos from "./pages/Documentos/Documentos";
import Configuracoes from "./pages/Configuracoes/Configuracoes";
import Usuarios from "./pages/Usuarios/Usuarios";

import ProtectedRoute from "./components/ProtectedRoute/ProtectedRoute";
import Footer from "./components/Footer/Footer"; // 👈 1. Import do Footer (ajuste o caminho)

// 🎯 IMPORTES DO UPLOAD GLOBAL
import { UploadProvider } from "./contexts/UploadContext";
import UploadWidget from "./components/UploadWidget/UploadWidget";

function App() {
    useEffect(() => {
        const temaSalvo = localStorage.getItem("tema");
        if (temaSalvo === "dark") {
            document.body.classList.add("dark-mode");
        } else {
            document.body.classList.remove("dark-mode");
        }
    }, []);

    return (
        <UploadProvider>
            {/* 2. Container Flexbox para garantir que o rodapé fique sempre na parte inferior */}
            <div style={{ display: "flex", flexDirection: "column", minHeight: "100vh" }}>
                
                {/* 3. Área principal expansível que empurra o Footer para o rodapé */}
                <div style={{ flex: 1, display: "flex", flexDirection: "column" }}>                    <Routes>
                        {/* 🌐 ROTAS PÚBLICAS */}
                        <Route path="/" element={<Login />} />
                        <Route path="/login" element={<Login />} />

                        {/* 🔒 ROTAS PROTEGIDAS */}
                        <Route element={<ProtectedRoute />}>
                            <Route path="/dashboard" element={<Dashboard />} />
                            <Route path="/documentos" element={<Documentos />} />
                            <Route path="/configuracoes" element={<Configuracoes />} />
                            <Route path="/usuarios" element={<Usuarios />} />
                        </Route>

                        {/* 🔄 FALLBACK */}
                        <Route path="*" element={<Navigate to="/" replace />} />
                    </Routes>
                </div>

                {/* 🦶 4. Navbar Inferior / Footer */}
                <Footer />

                {/* ⚡ WIDGET FIXO QUE PERMANECE VISÍVEL EM QUALQUER ROTA */}
                <UploadWidget />
            </div>
        </UploadProvider>
    );
}
export default App;