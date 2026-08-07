import React from "react";
import "./ErroModal.css";

interface ErroModalProps {
    isOpen: boolean;
    mensagem: string;
    onClose: () => void;
}

export default function ErroModal({ isOpen, mensagem, onClose }: ErroModalProps) {
    if (!isOpen) return null;

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-content modal-erro" onClick={(e) => e.stopPropagation()}>
                <div className="modal-header-erro">
                    <h3>❌ Acesso Negado</h3>
                    <button className="btn-close" onClick={onClose}>
                        &times;
                    </button>
                </div>

                <div className="modal-body">
                    <p>{mensagem}</p>
                </div>

                <div className="modal-footer justify-center">
                    <button className="btn-entendi" onClick={onClose}>
                        Entendi
                    </button>
                </div>
            </div>
        </div>
    );
}