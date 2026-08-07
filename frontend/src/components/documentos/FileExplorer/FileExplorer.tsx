import "./FileExplorer.css";
import { useState, useEffect, useRef } from "react";
import Toolbar from "../Toolbar/Toolbar";
import FolderTree from "../FolderTree/FolderTree";
import PreviewPanel from "../PreviewPanel/PreviewPanel";
import DocumentoTable from "../../tables/DocumentoTable";
import type { Documento } from "../../../types/documento";
import type { Diretorio } from "../../../types/diretorio";
import CriarPastaModal from "../CriarPastaModal/CriarPastaModal";
import RenomearModal from "../../RenomearModal/RenomearModal";
import ExcluirModal from "../../ExcluirModal/ExcluirModal";
import ErroModal from "../../ErroModal/ErroModal";
import { useUpload } from "../../../contexts/UploadContext";

// 🎯 IMPORT DAS FUNÇÕES DO OFFICE E SERVIÇOS
import { executarAbrirCom } from "../../../utils/desktopLauncher";
import { listarConteudo, criarPasta, renomearPasta, excluirPasta, downloadPasta } from "../../../services/diretorio";
import {
    excluirDocumento,
    renomearDocumento,
    downloadDocumento,
    sincronizarComGoogleDrive,
} from "../../../services/documento";

export default function FileExplorer() {
    // ⚡ Contexto Global de Upload (com controle de uploads ativos)
    const { adicionarUploads, adicionarUploadPasta, temUploadAtivo } = useUpload();
    
    const [selecionados, setSelecionados] = useState<Documento[]>([]);
    const [pastaSelecionada, setPastaSelecionada] = useState<Diretorio | null>(null);
    const [pastaRaizDrive, setPastaRaizDrive] = useState<Diretorio | null>(null);
    const [pesquisa, setPesquisa] = useState("");
    const [loading, setLoading] = useState(false);
    const [pastaAtual, setPastaAtual] = useState<string | null>(null);
    const [pastas, setPastas] = useState<Diretorio[]>([]);
    const [documentos, setDocumentos] = useState<Documento[]>([]);

    const [historicoPastas, setHistoricoPastas] = useState<(string | null)[]>([]);
    
    // 🛡️ REFERÊNCIA DE CONTROLE DE MONTAGEM DA TELA
    const isMounted = useRef(true);
    const prevTemUploadAtivo = useRef(temUploadAtivo);

    // Modais
    const [modalPastaAberto, setModalPastaAberto] = useState(false);
    const [modalRenomearAberto, setModalRenomearAberto] = useState(false);
    const [modalExcluirAberto, setModalExcluirAberto] = useState(false);

    const fileInputRef = useRef<HTMLInputElement | null>(null);
    const folderInputRef = useRef<HTMLInputElement | null>(null);

    const quantidadeSelecionados = selecionados.length + (pastaSelecionada ? 1 : 0);

    // Modais de Erro
    const [modalErroAberto, setModalErroAberto] = useState(false);
    const [mensagemErro, setMensagemErro] = useState("");

    const [toastSync, setToastSync] = useState<{ visivel: boolean; mensagem: string; tipo: 'sucesso' | 'erro' } | null>(null);

    const nomeItemExcluir = selecionados.length === 1 
        ? selecionados[0].nome_original 
        : (pastaSelecionada?.nome || "");

    function handleAbrirCom() {
        if (selecionados.length !== 1) return;
        executarAbrirCom(selecionados[0]);
    }

    // =========================================================================================
    // 🧠 FUNÇÕES AUXILIARES DE NOME ÚNICO
    // =========================================================================================
    function gerarNomeUnicoPasta(nomeDesejado: string, idItemAtual?: number | string): string {
        const nomesExistentes = pastas
            .filter((p) => p.id !== idItemAtual)
            .map((p) => p.nome.trim().toLowerCase());

        let nomeFinal = nomeDesejado.trim();
        let contador = 1;

        while (nomesExistentes.includes(nomeFinal.toLowerCase())) {
            nomeFinal = `${nomeDesejado.trim()} (${contador})`;
            contador++;
        }

        return nomeFinal;
    }

    function gerarNomeUnicoArquivo(nomeDesejado: string, idItemAtual?: number | string): string {
        const nomesExistentes = documentos
            .filter((d) => d.id !== idItemAtual)
            .map((d) => d.nome_original.trim().toLowerCase());

        let nomeFinal = nomeDesejado.trim();
        let contador = 1;

        const pontoIndex = nomeDesejado.lastIndexOf(".");
        let baseName = nomeDesejado;
        let ext = "";

        if (pontoIndex !== -1) {
            baseName = nomeDesejado.substring(0, pontoIndex);
            ext = nomeDesejado.substring(pontoIndex);
        }

        while (nomesExistentes.includes(nomeFinal.toLowerCase())) {
            nomeFinal = `${baseName.trim()} (${contador})${ext}`;
            contador++;
        }

        return nomeFinal;
    }

    // ============ CARREGAR CONTEUDO =========================================================
    async function carregarConteudo(parentId: string | null) {
        setLoading(true);
        try {
            const response = await listarConteudo(parentId);
            if (!isMounted.current) return;

            setPastas(response.pastas || []);
            setDocumentos(response.documentos || []);
            if (response.pasta_raiz) { setPastaRaizDrive(response.pasta_raiz); }
        } catch (error) {
            if (!isMounted.current) return;
            console.error("Erro ao carregar conteúdo:", error);
        } finally {
            if (isMounted.current) setLoading(false);
        }
    }

    // ============ ATUALIZAR AUTOMÁTICA QUANDO FINALIZAR UPLOADS ============================
    useEffect(() => {
        // Detecta quando a fila transita de 'ocupada' para 'vazia/concluída'
        if (prevTemUploadAtivo.current && !temUploadAtivo) {
            carregarConteudo(pastaAtual);
        }
        prevTemUploadAtivo.current = temUploadAtivo;
    }, [temUploadAtivo, pastaAtual]);

    // ============ ATUALIZAR / SINCRONIZAR COM O GOOGLE DRIVE ==================================
    async function handleAtualizar() {
        if (loading) return;

        // 🛡️ TRAVA: Impede sincronização enquanto há uploads rodando
        if (temUploadAtivo) {
            setToastSync({
                visivel: true,
                mensagem: "⏳ Aguarde a conclusão dos uploads para sincronizar com o Drive.",
                tipo: "erro",
            });
            setTimeout(() => {
                if (isMounted.current) setToastSync(null);
            }, 3000);
            return;
        }

        setLoading(true);
        try {
            await sincronizarComGoogleDrive();
            if (!isMounted.current) return;

            await carregarConteudo(pastaAtual);
            if (!isMounted.current) return;

            setToastSync({
                visivel: true,
                mensagem: "⚡ Sincronização com o Google Drive concluída!",
                tipo: "sucesso",
            });

            setTimeout(() => {
                if (isMounted.current) setToastSync(null);
            }, 3000);

        } catch (error: any) {
            if (!isMounted.current) return;
            console.error("Erro na sincronização:", error);

            let msg = "Erro ao sincronizar com o Google Drive.";
            if (error.response?.data?.detail) {
                const detail = error.response.data.detail;
                if (typeof detail === "string") {
                    msg = detail;
                } else if (Array.isArray(detail)) {
                    msg = detail.map((err) => `${err.loc?.join(" -> ")}: ${err.msg}`).join(" | ");
                } else {
                    msg = JSON.stringify(detail);
                }
            }

            setMensagemErro(msg);
            setModalErroAberto(true);
        } finally {
            if (isMounted.current) setLoading(false);
        }
    }

    // 🛡️ MONTAGEM E DESMONTAGEM DO COMPONENTE
    useEffect(() => {
        isMounted.current = true;
        carregarConteudo(pastaAtual);

        if (window.electronAPI?.onSyncStatus) {
            window.electronAPI.onSyncStatus((dados: any) => {
                if (!isMounted.current) return;

                if (dados.success) {
                    setToastSync({ 
                        visivel: true, 
                        mensagem: `✅ Arquivo "${dados.nomeArquivo}" salvo no Drive!`, 
                        tipo: 'sucesso' 
                    });
                } else {
                    setToastSync({ 
                        visivel: true, 
                        mensagem: `❌ Erro ao salvar "${dados.nomeArquivo}"`, 
                        tipo: 'erro' 
                    });
                }

                setTimeout(() => {
                    if (isMounted.current) setToastSync(null);
                }, 4000);
            });
        }

        return () => {
            isMounted.current = false;
        };
    }, []);

    // ============ UPLOAD ARQUIVOS (GLOBAL) ===================================================
    function handleUploadArquivos(event: React.ChangeEvent<HTMLInputElement>) {
        const files = event.target.files;
        if (!files || files.length === 0) return;

        adicionarUploads(files, pastaAtual);

        if (event.target) event.target.value = "";
    }

    // ============ UPLOAD PASTA (GLOBAL) ======================================================
    function handleUploadPasta(event: React.ChangeEvent<HTMLInputElement>) {
        const files = event.target.files;
        if (!files || files.length === 0) return;

        adicionarUploadPasta(files, pastaAtual);

        if (event.target) event.target.value = "";
    }

// ============ NAVEGAÇÃO =================================================================
    function handleEntrarPasta(novoFolderId: string | null) {
        if (novoFolderId === pastaAtual) return;

        const ehPastaRaiz = novoFolderId === null || 
            (pastaRaizDrive && String(novoFolderId) === String(pastaRaizDrive.id));

        if (ehPastaRaiz) {
            setHistoricoPastas([]);
        } else {
            setHistoricoPastas((prev) => [...prev, pastaAtual]);
        }

        setPastaAtual(novoFolderId);
        setSelecionados([]);
        setPastaSelecionada(null);
        carregarConteudo(novoFolderId);
    }
    function handleVoltarPasta() {
        if (historicoPastas.length === 0) return;

        const historicoCopia = [...historicoPastas];
        const pastaAnterior = historicoCopia.pop() ?? null;

        setHistoricoPastas(historicoCopia);
        setPastaAtual(pastaAnterior);
        setSelecionados([]);
        setPastaSelecionada(null);
        carregarConteudo(pastaAnterior);
    }
    
    // ============ CRIAR PASTA ================================================================
    async function handleConfirmarCriacaoPasta(nome: string) {
        try {
            setLoading(true);
            const nomeSeguro = gerarNomeUnicoPasta(nome);
            await criarPasta(nomeSeguro, pastaAtual);
            if (!isMounted.current) return;
            await carregarConteudo(pastaAtual);
        } catch (error) {
            if (!isMounted.current) return;
            console.error("Erro ao criar pasta:", error);
        } finally {
            if (isMounted.current) setLoading(false);
        }
    }

    // ============ ABRIR MODAL DE EXCLUSÃO ====================================================
    function handleAbrirModalExcluir() {
        if (quantidadeSelecionados === 0) return;
        setModalExcluirAberto(true);
    }

    // ============ CONFIRMAR EXCLUSÃO ========================================================
    async function handleConfirmarExclusao() {
        if (quantidadeSelecionados === 0) return;

        try {
            setLoading(true);
            for (const doc of selecionados) { await excluirDocumento(doc.id); }
            if (pastaSelecionada) { await excluirPasta(pastaSelecionada.id); }

            if (!isMounted.current) return;

            setSelecionados([]);
            setPastaSelecionada(null);
            setModalExcluirAberto(false);
            await carregarConteudo(pastaAtual);

        } catch (error: any) {
            if (!isMounted.current) return;
            console.error("Erro ao excluir:", error);
            
            const msg = error.response?.data?.detail || "Erro inesperado ao excluir o item.";
            
            setModalExcluirAberto(false);
            setMensagemErro(msg);
            setModalErroAberto(true);
            
        } finally {
            if (isMounted.current) setLoading(false);
        }
    }

    // ============ RENOMEAR ===================================================================
    function handleAbrirModalRenomear() {
        if (quantidadeSelecionados !== 1) return;
        setModalRenomearAberto(true);
    }

    async function handleConfirmarRenomear(novoNome: string) {
        if (quantidadeSelecionados !== 1) return;

        try {
            setLoading(true);
            
            if (selecionados.length === 1) {
                const doc = selecionados[0];
                const nomeSeguro = gerarNomeUnicoArquivo(novoNome, doc.id);
                await renomearDocumento(doc.id, nomeSeguro);
            } else if (pastaSelecionada) {
                const nomeSeguro = gerarNomeUnicoPasta(novoNome, pastaSelecionada.id);
                await renomearPasta(pastaSelecionada.id, nomeSeguro);
            }

            if (!isMounted.current) return;

            setSelecionados([]);
            setPastaSelecionada(null);
            setModalRenomearAberto(false);
            await carregarConteudo(pastaAtual);

        } catch (error) {
            if (!isMounted.current) return;
            console.error("Erro ao renomear:", error);
        } finally { 
            if (isMounted.current) setLoading(false); 
        }
    }

    // ============ DOWNLOAD ===================================================================
    async function handleDownload() {
        if (quantidadeSelecionados === 0) return;

        try {
            setLoading(true);
            
            for (const doc of selecionados) {
                const blob = await downloadDocumento(doc.id);
                const url = window.URL.createObjectURL(new Blob([blob]));
                const link = document.createElement("a");
                link.href = url;
                link.setAttribute("download", doc.nome_original || "download");

                document.body.appendChild(link);
                link.click();
                link.parentNode?.removeChild(link);
            }

            if (pastaSelecionada) {
                const blob = await downloadPasta(pastaSelecionada.id);
                const url = window.URL.createObjectURL(new Blob([blob]));
                const link = document.createElement("a");
                link.href = url;
                link.setAttribute("download", `${pastaSelecionada.nome}.zip`);

                document.body.appendChild(link);
                link.click();
                link.parentNode?.removeChild(link);
            }

        } catch (error) {
            if (!isMounted.current) return;
            console.error("Erro no download:", error);
        } finally {
            if (isMounted.current) setLoading(false);
        }
    }

    return (
        <div className="file-explorer">
            <input
                type="file"
                ref={fileInputRef}
                style={{ display: "none" }}
                multiple
                onChange={handleUploadArquivos}
            />

            <input
                type="file"
                ref={folderInputRef}
                style={{ display: "none" }}
                {...({ webkitdirectory: "", directory: "" } as any)}
                onChange={handleUploadPasta}
            />

            <Toolbar
                quantidadeSelecionados={quantidadeSelecionados}
                pesquisa={pesquisa}
                setPesquisa={setPesquisa}
                onUploadArquivo={() => fileInputRef.current?.click()}
                onUploadPasta={() => folderInputRef.current?.click()}
                onNovaPasta={() => setModalPastaAberto(true)}
                onAtualizar={handleAtualizar}
                desabilitarAtualizar={loading || temUploadAtivo}
                onVoltar={handleVoltarPasta}
                podeVoltar={historicoPastas.length > 0}
                onRenomear={handleAbrirModalRenomear}
                onDownload={handleDownload}
                onExcluir={handleAbrirModalExcluir}
                onCompartilhar={() => {}}
                onAbrirCom={handleAbrirCom}
            />

            <div className="content">
                {loading && pastas.length === 0 && documentos.length === 0 ? (
                    <div style={{ display: "flex", justifyContent: "center", alignItems: "center", flex: 1 }}>
                        <h2>Sincronizando e carregando conteúdo...</h2>
                    </div>
                ) : (
                    <>
                        <FolderTree
                            pastas={pastas}
                            pastaAtual={pastaAtual}
                            onSelecionarPasta={handleEntrarPasta}
                            pastaSelecionada={pastaSelecionada}
                            onClickPasta={(pasta) => {
                                setPastaSelecionada(pasta);
                                if (pasta) setSelecionados([]);
                            }}
                            nomePastaRaiz={pastaRaizDrive?.nome}
                        />

                        <div className="table-area">
                            <DocumentoTable
                                documentos={documentos}
                                pesquisa={pesquisa}
                                pastaAtual={pastaAtual}
                                selecionados={selecionados}
                                setSelecionados={(docs) => {
                                    setSelecionados(docs);
                                    if (docs.length > 0) setPastaSelecionada(null);
                                }}
                            />
                        </div>
                    </>
                )}
            </div>

            <PreviewPanel 
                key={selecionados[0]?.id || "vazio"} 
                documento={selecionados.length === 1 ? selecionados[0] : null} 
            />

            <CriarPastaModal
                isOpen={modalPastaAberto}
                onClose={() => setModalPastaAberto(false)}
                onConfirm={handleConfirmarCriacaoPasta}
            />

            <RenomearModal
                isOpen={modalRenomearAberto}
                nomeAtual={selecionados.length === 1 ? (selecionados[0].nome_original || "") : (pastaSelecionada?.nome || "")}
                onClose={() => setModalRenomearAberto(false)}
                onConfirm={handleConfirmarRenomear}
            />

            <ExcluirModal
                isOpen={modalExcluirAberto}
                quantidade={quantidadeSelecionados}
                nomeItem={nomeItemExcluir}
                loading={loading}
                onClose={() => setModalExcluirAberto(false)}
                onConfirm={handleConfirmarExclusao}
            />

            <ErroModal 
                isOpen={modalErroAberto} 
                mensagem={mensagemErro} 
                onClose={() => setModalErroAberto(false)} 
            />

            {toastSync && toastSync.visivel && (
                <div style={{
                    position: 'fixed',
                    bottom: '24px',
                    right: '24px',
                    zIndex: 9999,
                    backgroundColor: toastSync.tipo === 'sucesso' ? '#2e7d32' : '#d32f2f',
                    color: 'white',
                    padding: '16px 24px',
                    borderRadius: '8px',
                    boxShadow: '0 4px 12px rgba(0,0,0,0.3)',
                    fontWeight: '500',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px',
                    animation: 'fadeIn 0.3s ease-in-out'
                }}>
                    {toastSync.mensagem}
                </div>
            )}
        </div>
    );
}