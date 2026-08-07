import React, { useState, useEffect } from "react";
import "./RenomearModal.css";

interface RenomearModalProps {
    isOpen: boolean;
    nomeAtual: string;
    onClose: () => void;
    onConfirm: (novoNome: string) => void;
}

export default function RenomearModal({
    isOpen,
    nomeAtual,
    onClose,
    onConfirm,
}: RenomearModalProps) {
    const [novoNome, setNovoNome] = useState(nomeAtual);

    // Atualiza o input com o nome do arquivo selecionado sempre que o modal abre
    useEffect(() => {
        setNovoNome(nomeAtual);
    }, [nomeAtual, isOpen]);

    if (!isOpen) return null;

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (novoNome.trim() && novoNome !== nomeAtual) {
            onConfirm(novoNome.trim());
        } else {
            onClose();
        }
    };

    return (
        <div className="modal-overlay">
            <div className="modal-container">
                <h3>Renomear Documento</h3>
                <form onSubmit={handleSubmit}>
                    <div className="modal-body">
                        <label htmlFor="nome-documento">Novo nome:</label>
                        <input
                            id="nome-documento"
                            type="text"
                            value={novoNome}
                            onChange={(e) => setNovoNome(e.target.value)}
                            autoFocus
                        />
                    </div>
                    <div className="modal-actions">
                        <button type="button" className="btn-cancelar" onClick={onClose}>
                            Cancelar
                        </button>
                        <button type="submit" className="btn-salvar">
                            Salvar
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}