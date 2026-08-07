import React, { useState } from "react";
import "./CriarPastaModal.css";

interface CriarPastaModalProps {
    isOpen: boolean;
    onClose: () => void;
    onConfirm: (nome: string) => void;
}

export default function CriarPastaModal({
    isOpen,
    onClose,
    onConfirm,
}: CriarPastaModalProps) {
    const [nome, setNome] = useState("");

    if (!isOpen) return null;

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (nome.trim()) {
            onConfirm(nome.trim());
            setNome("");
            onClose();
        }
    };

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-container" onClick={(e) => e.stopPropagation()}>
                <div className="modal-header">
                    <h3>📁 Nova Pasta</h3>
                    <button className="modal-close-btn" onClick={onClose}>
                        ✕
                    </button>
                </div>

                <form onSubmit={handleSubmit}>
                    <div className="modal-body">
                        <label>Nome da pasta</label>
                        <input
                            type="text"
                            placeholder="Ex: Documentos Financeiros"
                            value={nome}
                            onChange={(e) => setNome(e.target.value)}
                            autoFocus
                        />
                    </div>

                    <div className="modal-actions">
                        <button type="button" className="btn-cancelar" onClick={onClose}>
                            Cancelar
                        </button>
                        <button
                            type="submit"
                            className="btn-confirmar"
                            disabled={!nome.trim()}
                        >
                            Criar Pasta
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}