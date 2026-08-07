import FileExplorer from "../../components/documentos/FileExplorer/FileExplorer";
import Navbar from "../../components/layout/Navbar/Navbar";
import "./Documentos.css"; // 👈 Import dos estilos da página

export default function Documentos() {
    return (
        <div className="documentos-page">
            <Navbar />
            <main className="documentos-content">
                <FileExplorer />
            </main>
        </div>
    );
}