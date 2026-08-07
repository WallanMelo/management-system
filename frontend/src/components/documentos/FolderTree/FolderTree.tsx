import React from "react";
import "./FolderTree.css";
import type { Diretorio } from "../../../types/diretorio";

interface FolderTreeProps {
    pastas: Diretorio[];
    pastaAtual: string | null;
    onSelecionarPasta: (driveFolderId: string | null) => void;
    pastaSelecionada: Diretorio | null;
    onClickPasta: (pasta: Diretorio | null) => void;
    nomePastaRaiz?: string;
}

export default function FolderTree({
    pastas,
    pastaAtual,
    onSelecionarPasta,
    pastaSelecionada,
    onClickPasta,
    nomePastaRaiz, //nome real da pasta raiz direto do drive
}: FolderTreeProps) {

    // 1 CLIQUE: Apenas seleciona visualmente a pasta (agora avisa o componente pai)
    function handleSingleClick(pasta: Diretorio | null) {
        onClickPasta(pasta);
    }

    // DUPLO CLIQUE: Entra na pasta de fato (mantive sua lógica original)
    function handleDoubleClick(driveFolderId: string | null) {
        onSelecionarPasta(driveFolderId);
    }

    return (
        <aside className="folder-tree">
            <h3>Pastas</h3>

            <ul>
                {/* Pasta Raiz */}
                <li
                    className={`
                        ${pastaAtual === null ? "active" : ""} 
                        ${pastaSelecionada === null ? "selected" : ""}
                    `.trim()}
                    onClick={() => handleSingleClick(null)}
                    onDoubleClick={() => handleDoubleClick(null)}
                >
                    🏠 {nomePastaRaiz ? `Raiz (${nomePastaRaiz})` : "Raiz (Meu Drive)"}
                </li>

                {/* Lista de Pastas */}
                {pastas.map((pasta) => {
                    const isFolderActive = pasta.drive_folder_id === pastaAtual;
                    // Compara usando o id (ou drive_folder_id) para saber qual está destacada
                    const isFolderSelected = pastaSelecionada?.drive_folder_id === pasta.drive_folder_id;

                    return (
                        <li
                            key={pasta.id}
                            className={`
                                ${isFolderActive ? "active" : ""} 
                                ${isFolderSelected ? "selected" : ""}
                            `.trim()}
                            onClick={() => handleSingleClick(pasta)}
                            onDoubleClick={() => handleDoubleClick(pasta.drive_folder_id)}
                        >
                            📁 {pasta.nome}
                        </li>
                    );
                })}

                {pastas.length === 0 && (
                    <li className="empty">
                        Nenhuma pasta encontrada
                    </li>
                )}
            </ul>
        </aside>
    );
}