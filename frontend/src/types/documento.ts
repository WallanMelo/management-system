export interface Documento {

    id: number;

    nome_original: string;

    nome_sistema: string;

    mime_type: string | null;

    tamanho: number;
    
    modified_time?: string;

    diretorio_id: number | null;

    favorito: boolean;

    created_at: string;

    updated_at: string;

    drive_file_id?: string | null;

    descricao?: string | null;

}