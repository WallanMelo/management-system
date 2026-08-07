import React, { useState } from "react";
import { useUpload } from "../../contexts/UploadContext";
import "./UploadWidget.css"; // Estilize como desejar

export default function UploadWidget() {
    const { uploads, limparUploadsConcluidos } = useUpload();
    const [minimizado, setMinimizado] = useState(false);

    if (uploads.length === 0) return null;

    const ativos = uploads.filter((u) => u.status === "carregando" || u.status === "pendente").length;

    return (
        <div className={`upload-widget ${minimizado ? "minimizado" : ""}`}>
            <div className="upload-header">
                <span>
                    {ativos > 0 ? `Enviando ${ativos} arquivo(s)...` : "Uploads concluídos"}
                </span>
                <div>
                    <button onClick={() => setMinimizado(!minimizado)}>
                        {minimizado ? "▲" : "▼"}
                    </button>
                    <button onClick={limparUploadsConcluidos}>✕</button>
                </div>
            </div>

            {!minimizado && (
                <div className="upload-lista">
                    {uploads.map((item) => (
                        <div key={item.id} className="upload-item">
                            <div className="upload-info">
                                <span className="upload-nome">{item.nome}</span>
                                <span className="upload-percent">{item.progresso}%</span>
                            </div>
                            
                            <div className="bar-container">
                                <div
                                    className={`bar ${item.status}`}
                                    style={{ width: `${item.progresso}%` }}
                                />
                            </div>

                            {item.status === "erro" && (
                                <span className="erro-texto">{item.mensagemErro}</span>
                            )}
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}