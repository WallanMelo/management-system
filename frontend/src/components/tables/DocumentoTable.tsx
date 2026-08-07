import "./DocumentoTable.css";
import type { Documento } from "../../types/documento";
import { getFileIcon } from "../../utils/getFileIcon";
import { formatFileSize } from "../../utils/formatFileSize";
import { formatDate } from "../../utils/formatDate";

interface DocumentoTableProps {
    documentos: Documento[];
    pesquisa: string;
    pastaAtual: string | null;
    selecionados: Documento[];
    setSelecionados: (docs: Documento[]) => void;
}

export default function DocumentoTable({
    documentos,
    pesquisa,
    pastaAtual, // 👈 Incluído para alinhar com a interface
    selecionados,
    setSelecionados,
}: DocumentoTableProps) {

    const documentosFiltrados = documentos.filter((doc) =>
        (doc.nome_original || "")
            .toLowerCase()
            .includes((pesquisa || "").toLowerCase())
    );

    // 🎯 Seleciona o arquivo atualizando a lista de selecionados
    function selecionar(doc: Documento) {
        setSelecionados([doc]);
    }

    return (
        <table className="document-table">
            <thead>
                <tr>
                    <th>Nome</th>
                    <th>Tamanho</th>
                    <th>Atualizado</th>
                </tr>
            </thead>
            <tbody>
                {documentosFiltrados.map((doc) => {
                    const isSelected = selecionados.some((s) => s.id === doc.id);
                    
                    return (
                        <tr
                            key={doc.id}
                            onClick={() => selecionar(doc)}
                            className={isSelected ? "selected" : ""}
                        >
                            <td>
                                {getFileIcon(doc.mime_type)}{" "}
                                {doc.nome_original}
                            </td>
                            <td>{formatFileSize(doc.tamanho)}</td>
                            <td>{formatDate(doc.modified_time || doc.updated_at || doc.created_at)}</td>                        </tr>
                    );
                })}

                {documentosFiltrados.length === 0 && (
                    <tr>
                        <td colSpan={3} style={{ textAlign: "center", color: "#888", padding: "20px" }}>
                            Nenhum documento encontrado.
                        </td>
                    </tr>
                )}
            </tbody>
        </table>
    );
}