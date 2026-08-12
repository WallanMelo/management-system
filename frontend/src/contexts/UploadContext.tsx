import { createContext, useContext, useState, useEffect, type ReactNode } from "react";
import axios from "axios";
import { criarPasta } from "../services/diretorio"; // Ajuste o caminho se necessário

export interface UploadItem {
    id: string;
    file: File;
    nome: string;
    parentId: string | null;
    progresso: number;
    status: "pendente" | "carregando" | "sucesso" | "erro";
    mensagemErro?: string;
}

interface UploadContextData {
    uploads: UploadItem[];
    temUploadAtivo: boolean; 
    adicionarUploads: (files: FileList | File[], parentId: string | null) => void;
    adicionarUploadPasta: (files: FileList | File[], parentId: string | null) => Promise<void>;
    limparUploadsConcluidos: () => void;
}

const CONCURRENCY_LIMIT = 2; // Processa no máximo 2 uploads ao mesmo tempo no Google Drive

const UploadContext = createContext<UploadContextData>({} as UploadContextData);

export function UploadProvider({ children }: { children: ReactNode }) {
    const [uploads, setUploads] = useState<UploadItem[]>([]);

    // Verifica se existe algum item sendo enviado ou aguardando na fila
    const temUploadAtivo = uploads.some(
        (u) => u.status === "carregando" || u.status === "pendente"
    );

    // ⚡ GERENCIADOR DE FILA: Dispara novos envios sempre que um é concluído
    useEffect(() => {
        const emAndamento = uploads.filter((u) => u.status === "carregando").length;
        const pendentes = uploads.filter((u) => u.status === "pendente");

        if (emAndamento < CONCURRENCY_LIMIT && pendentes.length > 0) {
            const proximo = pendentes[0];
            executarUpload(proximo);
        }
    }, [uploads]);

    async function executarUpload(item: UploadItem) {
        setUploads((prev) =>
            prev.map((u) => (u.id === item.id ? { ...u, status: "carregando" } : u))
        );

        const formData = new FormData();
        formData.append("arquivo", item.file);
        if (item.parentId) {
            formData.append("parent_id", item.parentId);
        }

        // Recupera o token de autenticação
        const token = localStorage.getItem("access_token");

        // Utilize a URL do seu backend no Render (ou variável de ambiente)
        const BASE_URL = "https://management-system-6bb0.onrender.com"; 

        try {
            await axios.post(`${BASE_URL}/documentos/upload`, formData, {
                headers: {
                    Authorization: `Bearer ${token}`,
                    // O browser define o Content-Type 'multipart/form-data' automaticamente
                },
                onUploadProgress: (progressEvent) => {
                    if (progressEvent.total) {
                        const percentual = Math.round((progressEvent.loaded * 100) / progressEvent.total);
                        setUploads((prev) =>
                            prev.map((u) => (u.id === item.id ? { ...u, progresso: percentual } : u))
                        );
                    }
                },
            });

            setUploads((prev) =>
                prev.map((u) => (u.id === item.id ? { ...u, status: "sucesso", progresso: 100 } : u))
            );
        } catch (error: any) {
            console.error(`Erro no upload de ${item.nome}:`, error);
            setUploads((prev) =>
                prev.map((u) =>
                    u.id === item.id
                        ? { ...u, status: "erro", mensagemErro: error.response?.data?.detail || "Erro no envio" }
                        : u
                )
            );
        }
    }

    function adicionarUploads(files: FileList | File[], parentId: string | null) {
        const listaArquivos = Array.from(files);

        const novosItems: UploadItem[] = listaArquivos.map((file) => ({
            id: `${Date.now()}-${Math.random().toString(36).substring(2, 9)}`,
            file,
            nome: file.name,
            parentId,
            progresso: 0,
            status: "pendente",
        }));

        setUploads((prev) => [...prev, ...novosItems]);
    }

    // ⚡ CRIA A ESTRUTURA DE PASTAS DE FORMA GLOBAL (Sem travar ao trocar de rota)
    async function adicionarUploadPasta(files: FileList | File[], parentId: string | null) {
        const fileList = Array.from(files);
        const pastaMap: Record<string, string> = {};

        for (const file of fileList) {
            const relativePath = file.webkitRelativePath;
            if (!relativePath) continue;

            const partes = relativePath.split("/");
            const pastasCaminho = partes.slice(0, -1);

            let parentIdAtual = parentId;
            let caminhoAcumulado = "";

            for (const nomePasta of pastasCaminho) {
                caminhoAcumulado = caminhoAcumulado ? `${caminhoAcumulado}/${nomePasta}` : nomePasta;

                if (!pastaMap[caminhoAcumulado]) {
                    const novaPasta = await criarPasta(nomePasta, parentIdAtual);
                    const idCriado = novaPasta.drive_folder_id || novaPasta.id?.toString();
                    pastaMap[caminhoAcumulado] = idCriado;
                }

                parentIdAtual = pastaMap[caminhoAcumulado];
            }

            // Envia cada arquivo para a fila global com o caminho relativo correto
            const item: UploadItem = {
                id: `${Date.now()}-${Math.random().toString(36).substring(2, 9)}`,
                file,
                nome: relativePath,
                parentId: parentIdAtual,
                progresso: 0,
                status: "pendente",
            };

            setUploads((prev) => [...prev, item]);
        }
    }

    function limparUploadsConcluidos() {
        setUploads((prev) => prev.filter((u) => u.status === "carregando" || u.status === "pendente"));
    }

    return (
        <UploadContext.Provider
            value={{
                uploads,
                temUploadAtivo,
                adicionarUploads,
                adicionarUploadPasta,
                limparUploadsConcluidos,
            }}
        >
            {children}
        </UploadContext.Provider>
    );
}

export function useUpload() {
    return useContext(UploadContext);
}