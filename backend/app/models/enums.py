from enum import Enum

class PerfilUsuario(str, Enum):
    ADMIN = "ADMIN"
    ESTAGIARIO = "ESTAGIARIO"
    EXTERNO = "EXTERNO"

class TemaSistema(str,Enum):
    CLARO = "CLARO"
    ESCURO = "ESCURO"