import React from "react";
import "./ExcluirModal.css";

interface ExcluirModalProps {
    isOpen: boolean;
    quantidade: number;
    nomeItem?: string;
    onClose: () => void;
    onConfirm: () => void;
    loading?: boolean;
}

export default function ExcluirModal({
    isOpen,
    quantidade,
    nomeItem,
    onClose,
    onConfirm,
    loading = false,
}: ExcluirModalProps) {
    if (!isOpen) return null;

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-content modal-excluir" onClick={(e) => e.stopPropagation()}>
                <div className="modal-header">
                    <h3>⚠️ Confirmar Exclusão</h3>
                    <button className="btn-close" onClick={onClose} disabled={loading}>
                        &times;
                    </button>
                </div>

                <div className="modal-body">
                    {quantidade === 1 && nomeItem ? (
                        <p>
                            Tem certeza que deseja excluir <strong>"{nomeItem}"</strong>?
                        </p>
                    ) : (
                        <p>
                            Tem certeza que deseja excluir os <strong>{quantidade} itens</strong> selecionados?
                        </p>
                    )}
                    <span className="warning-text">Essa ação não poderá ser desfeita.</span>
                </div>

                <div className="modal-footer">
                    <button className="btn-cancelar" onClick={onClose} disabled={loading}>
                        Cancelar
                    </button>
                    <button className="btn-excluir" onClick={onConfirm} disabled={loading}>
                        {loading ? "Excluindo..." : "Excluir"}
                    </button>
                </div>
            </div>
        </div>
    );
}