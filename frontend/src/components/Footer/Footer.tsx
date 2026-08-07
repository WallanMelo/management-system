import React from "react";
import "./Footer.css";

export default function Footer() {
    const anoAtual = new Date().getFullYear();

    return (
        <footer className="bottom-navbar">
            <div className="footer-content">
                <span>
                    © {anoAtual} Sistema de Gestão • Todos os direitos reservados
                </span>
                <span className="developer-credit">
                    Desenvolvido por{" "}
                    <a
                        href="https://beacons.ai/Wallan7Melo"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="developer-link"
                    >
                        Wallan Melo
                    </a>
                </span>
            </div>
        </footer>
    );
}