-- =====================================================
-- TABELA: USUÁRIOS
-- =====================================================

CREATE TABLE usuarios (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    nome VARCHAR(150) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    senha_hash TEXT NOT NULL,

    perfil VARCHAR(20) NOT NULL
        CHECK (perfil IN ('ADMIN', 'ESTAGIARIO','EXTERNO')),

    ativo BOOLEAN NOT NULL DEFAULT TRUE,

    ultimo_login TIMESTAMP,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- TABELA: CLIENTES
-- =====================================================

CREATE TABLE clientes (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    nome VARCHAR(150) NOT NULL,

    cpf_cnpj VARCHAR(18),

    telefone VARCHAR(20),

    email VARCHAR(150),

    observacao TEXT,

    ativo BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- TABELA: DIRETORIOS
-- =====================================================

CREATE TABLE diretorios (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    cliente_id INTEGER NOT NULL,

    diretorio_pai_id INTEGER,

    nome VARCHAR(100) NOT NULL,

    drive_folder_id VARCHAR(255),

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_diretorio_cliente
        FOREIGN KEY (cliente_id)
        REFERENCES clientes(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_diretorio_pai
        FOREIGN KEY (diretorio_pai_id)
        REFERENCES diretorios(id)
        ON DELETE CASCADE
);

-- =====================================================
-- TABELA: DOCUMENTOS
-- =====================================================

CREATE TABLE documentos (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    cliente_id INTEGER NOT NULL,

    diretorio_id INTEGER,

    usuario_upload INTEGER NOT NULL,

    nome_original VARCHAR(255) NOT NULL,

    nome_sistema VARCHAR(255) NOT NULL,

    descricao TEXT,

    drive_file_id VARCHAR(255) NOT NULL,

    mime_type VARCHAR(100),

    tamanho BIGINT,

    hash VARCHAR(64),

    versao INTEGER NOT NULL DEFAULT 1,

    favorito BOOLEAN NOT NULL DEFAULT FALSE,

    ativo BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_documento_cliente
        FOREIGN KEY (cliente_id)
        REFERENCES clientes(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_documento_diretorio
        FOREIGN KEY (diretorio_id)
        REFERENCES diretorios(id)
        ON DELETE SET NULL,

    CONSTRAINT fk_documento_usuario
        FOREIGN KEY (usuario_upload)
        REFERENCES usuarios(id)
);

-- =====================================================
-- TABELA: COMPARTILHAMENTOS
-- =====================================================

CREATE TABLE compartilhamentos (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    documento_id INTEGER NOT NULL,

    usuario_id INTEGER NOT NULL,

    visualizar BOOLEAN NOT NULL DEFAULT TRUE,

    download BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_comp_documento
        FOREIGN KEY (documento_id)
        REFERENCES documentos(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_comp_usuario
        FOREIGN KEY (usuario_id)
        REFERENCES usuarios(id)
        ON DELETE CASCADE
);

-- =====================================================
-- TABELA: AUDITORIA
-- =====================================================

CREATE TABLE auditoria (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    usuario_id INTEGER,

    documento_id INTEGER,

    acao VARCHAR(30) NOT NULL,

    ip VARCHAR(50),

    observacao TEXT,

    data_hora TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_auditoria_usuario
        FOREIGN KEY (usuario_id)
        REFERENCES usuarios(id)
        ON DELETE SET NULL,

    CONSTRAINT fk_auditoria_documento
        FOREIGN KEY (documento_id)
        REFERENCES documentos(id)
        ON DELETE SET NULL
);

-- =====================================================
-- TABELA: CONFIGURAÇÕES
-- =====================================================

CREATE TABLE configuracoes (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    nome_empresa VARCHAR(150) NOT NULL,

    cnpj VARCHAR(18),

    telefone VARCHAR(20),

    email VARCHAR(150),

    logo TEXT,

    pasta_drive VARCHAR(255) NOT NULL,

    tema VARCHAR(20) NOT NULL DEFAULT 'CLARO'
        CHECK (tema IN ('CLARO','ESCURO')),

    backup_automatico BOOLEAN NOT NULL DEFAULT TRUE
);

-- =====================================================
-- ÍNDICES
-- =====================================================

CREATE INDEX idx_usuario_email
ON usuarios(email);

CREATE INDEX idx_cliente_nome
ON clientes(nome);

CREATE INDEX idx_documento_cliente
ON documentos(cliente_id);

CREATE INDEX idx_documento_diretorio
ON documentos(diretorio_id);

CREATE INDEX idx_documento_hash
ON documentos(hash);

CREATE INDEX idx_documento_drive
ON documentos(drive_file_id);

CREATE INDEX idx_documento_nome
ON documentos(nome_original);

CREATE INDEX idx_auditoria_data
ON auditoria(data_hora);