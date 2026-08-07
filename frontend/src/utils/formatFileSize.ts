export function formatFileSize(bytes?: number | string | null): string {
    // 1. Se for nulo, indefinido ou vazio, retorna "0 B"
    if (bytes === null || bytes === undefined || bytes === "") return "0 B";

    // 2. Converte para número (PostgreSQL/FastAPI às vezes enviam números grandes como String)
    const num = typeof bytes === "string" ? Number(bytes) : bytes;

    // 3. Se não for um número válido ou for menor/igual a zero
    if (isNaN(num) || num <= 0) return "0 B";

    const sizes = ["B", "KB", "MB", "GB", "TB"];

    // 4. Calcula o índice da unidade (KB, MB, GB...)
    const i = Math.floor(Math.log(num) / Math.log(1024));

    // 5. Retorna o valor formatado
    return (num / Math.pow(1024, i)).toFixed(2) + " " + sizes[i];
}