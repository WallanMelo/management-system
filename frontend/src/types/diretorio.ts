export interface Diretorio {

    id: number;

    nome: string;

    cliente_id?: number | null;

    diretorio_pai_id?: number | null;

    drive_folder_id: string;

    drive_parent_id?: string | null;

    sincronizado: boolean;

    created_at: string;

    updated_at?: string;
}