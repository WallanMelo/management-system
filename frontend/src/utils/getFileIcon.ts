export function getFileIcon(mimeType?: string | null): string {
    // Se o mimeType for nulo, indefinido ou vazio, retorna o ícone de arquivo padrão
    if (!mimeType) return "📄";

    const type = mimeType.toLowerCase();

    if (type.includes("pdf")) return "📕";
    if (type.includes("image")) return "🖼️";
    if (type.includes("word") || type.includes("document")) return "📘";
    if (type.includes("excel") || type.includes("spreadsheet") || type.includes("sheet")) return "📗";
    if (type.includes("powerpoint") || type.includes("presentation")) return "📙";
    if (type.includes("zip") || type.includes("compressed") || type.includes("tar")) return "🗜️";
    if (type.includes("video")) return "🎥";
    if (type.includes("audio")) return "🎵";
    if (type.includes("text")) return "📄";

    return "📁";
}