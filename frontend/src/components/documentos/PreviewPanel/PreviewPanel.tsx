import "./PreviewPanel.css";
import type { Documento } from "../../../types/documento";
import { formatDate } from "../../../utils/formatDate";
import { formatFileSize } from "../../../utils/formatFileSize";
import { getFileIcon } from "../../../utils/getFileIcon";

interface PreviewPanelProps {
    documento: Documento | null;
}

export default function PreviewPanel({ documento }: PreviewPanelProps) {
    if (!documento) {
        return (
            <div className="preview-panel empty">
                <h3>Visualização</h3>
                <p>Nenhum documento selecionado.</p>
            </div>
        );
    }

    // Prioriza o modified_time vindo do Google Drive
    const dataAtualizacao = documento.modified_time || documento.updated_at || documento.created_at;

    return (
        <div className="preview-panel">
            <h3>Visualização</h3>

            <h2>
                {getFileIcon(documento.mime_type)} {documento.nome_original}
            </h2>

            <div className="preview-details">
                <p><strong>Tamanho:</strong> {formatFileSize(documento.tamanho)}</p>
                <p><strong>Criado em:</strong> {formatDate(documento.created_at)}</p>
                <p><strong>Atualizado:</strong> {formatDate(dataAtualizacao)}</p>
                {documento.descricao && (
                    <p><strong>Descrição:</strong> {documento.descricao}</p>
                )}
            </div>
        </div>
    );
}