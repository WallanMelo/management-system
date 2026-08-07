import React, { useState } from "react";
import "./Toolbar.css";

interface ToolbarProps {
    quantidadeSelecionados: number;

    onUploadArquivo: () => void;
    onUploadPasta: () => void;
    onNovaPasta: () => void;
    onAtualizar: () => void;
    desabilitarAtualizar?: boolean;

    onVoltar?: () => void;
    podeVoltar?: boolean;

    onRenomear: () => void;
    onExcluir: () => void;
    onDownload: () => void;
    onCompartilhar: () => void;
    onAbrirCom: () => void;
    
    pesquisa: string;
    setPesquisa: (value: string) => void;
}

export default function Toolbar({
    quantidadeSelecionados,
    onUploadArquivo,
    onUploadPasta,
    onNovaPasta,
    onAtualizar,
    desabilitarAtualizar = false, // 👈 Desestruturado com valor padrão false
    onVoltar,
    podeVoltar,
    onRenomear,
    onExcluir,
    onDownload,
    onCompartilhar,
    onAbrirCom,
    pesquisa,
    setPesquisa,
}: ToolbarProps) {
    const [menuUploadAberto, setMenuUploadAberto] = useState(false);

    const possuiSelecao = quantidadeSelecionados > 0;
    const somenteUm = quantidadeSelecionados === 1;

    return (
        <div className="toolbar">
            <div className="toolbar-left">
                {/* Botão de Voltar */}
                {podeVoltar && (
                    <button 
                        type="button" 
                        onClick={(e) => {
                            e.preventDefault();
                            if (onVoltar) onVoltar();
                        }} 
                        title="Voltar para a pasta anterior"
                    >
                        ⬅️ Voltar
                    </button>
                )}

                {/* Menu Dropdown para Upload */}
                <div className="upload-dropdown-container">
                    <button type="button" onClick={() => setMenuUploadAberto(!menuUploadAberto)}>
                        📤 Upload ▾
                    </button>

                    {menuUploadAberto && (
                        <div
                            className="upload-menu"
                            onMouseLeave={() => setMenuUploadAberto(false)}
                        >
                            <button 
                                type="button"
                                onClick={() => {
                                    setMenuUploadAberto(false);
                                    onUploadArquivo();
                                }}
                            >
                                📄 Carregar Arquivo(s)
                            </button>
                            <button 
                                type="button"
                                onClick={() => {
                                    setMenuUploadAberto(false);
                                    onUploadPasta();
                                }}
                            >
                                📁 Carregar Pasta
                            </button>
                        </div>
                    )}
                </div>

                <button type="button" onClick={onNovaPasta}>
                    📁 Nova Pasta
                </button>

                {/* Botão de Atualizar */}
                <button
                    onClick={onAtualizar}
                    disabled={desabilitarAtualizar}
                    title={desabilitarAtualizar ? "Uploads em andamento. Aguarde..." : "Sincronizar com o Google Drive"}
                    className={desabilitarAtualizar ? "btn-disabled" : ""}
                >
                    🔄 Atualizar
                </button>
            </div>

            <div className="toolbar-center">
                <input
                    value={pesquisa}
                    onChange={(e) => setPesquisa(e.target.value)}
                    placeholder="Pesquisar documento..."
                />
            </div>

            <div className="toolbar-right">
                <button 
                    onClick={onAbrirCom}
                    disabled={quantidadeSelecionados !== 1}
                    title="Abrir com um aplicativo do seu computador"
                >
                    📂 Abrir
                </button>

                {somenteUm && (<button type="button" onClick={onRenomear}>✏️ Renomear</button>)}

                {possuiSelecao && (<button type="button" onClick={onDownload}>⬇️ Download</button>)}

                {possuiSelecao && (<button className="danger" type="button" onClick={onExcluir}>🗑 Excluir</button>)}
            </div>
        </div>
    );
}