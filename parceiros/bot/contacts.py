import re
import pandas as pd
from typing import List, Optional
from dataclasses import dataclass


COLUNAS_OBRIGATORIAS = ["nome", "telefone", "endereco", "CONTATO_FEITO"]
COLUNAS_OPCIONAIS = ["INTERESSADO", "FECHADO", "FESTAS GERADAS"]

STATUS_VALUES = ["NAO", "ENVIADO", "RESPONDEU", "INTERESSADO", "SEM_INTERESSE", "PARCERIA_FECHADA"]


@dataclass
class Parceiro:
    nome: str
    telefone: str
    telefone_formatado: str
    endereco: str
    status: str
    interessado: str
    fechado: str
    festas_geradas: str
    indice: int

    @property
    def pode_enviar(self) -> bool:
        return self.status == "NAO"


def formatar_telefone(telefone: str) -> Optional[str]:
    """Converte telefone para formato internacional 55XXXXXXXXXXX."""
    if pd.isna(telefone) or not str(telefone).strip():
        return None

    apenas_digitos = re.sub(r"\D", "", str(telefone))

    if len(apenas_digitos) < 8:
        return None

    # Remove código de país se já tiver
    if apenas_digitos.startswith("55") and len(apenas_digitos) > 11:
        apenas_digitos = apenas_digitos[2:]

    # Adiciona 9 para celulares de 8 dígitos (sem o 9)
    if len(apenas_digitos) == 10:
        ddd = apenas_digitos[:2]
        numero = apenas_digitos[2:]
        if not numero.startswith("9"):
            apenas_digitos = ddd + "9" + numero

    return "55" + apenas_digitos


def carregar_parceiros(caminho: str) -> pd.DataFrame:
    """Carrega e valida a planilha de parceiros."""
    df = pd.read_excel(caminho, dtype=str)
    df.columns = [c.strip() for c in df.columns]

    # Garante colunas opcionais existam
    for col in COLUNAS_OPCIONAIS:
        if col not in df.columns:
            df[col] = ""

    # Preenche NaN
    df = df.fillna("")

    # Garante status padrão
    df["CONTATO_FEITO"] = df["CONTATO_FEITO"].apply(
        lambda x: x.strip().upper() if x.strip().upper() in STATUS_VALUES else "NAO"
    )

    return df


def dataframe_para_parceiros(df: pd.DataFrame) -> List[Parceiro]:
    """Converte DataFrame em lista de Parceiro."""
    parceiros = []
    for idx, row in df.iterrows():
        tel_fmt = formatar_telefone(row.get("telefone", ""))
        parceiros.append(Parceiro(
            nome=str(row.get("nome", "")).strip(),
            telefone=str(row.get("telefone", "")).strip(),
            telefone_formatado=tel_fmt or "",
            endereco=str(row.get("endereco", "")).strip(),
            status=str(row.get("CONTATO_FEITO", "NAO")).strip().upper(),
            interessado=str(row.get("INTERESSADO", "")).strip(),
            fechado=str(row.get("FECHADO", "")).strip(),
            festas_geradas=str(row.get("FESTAS GERADAS", "")).strip(),
            indice=int(idx),
        ))
    return parceiros


def atualizar_status(caminho: str, indice: int, coluna: str, valor: str):
    """Atualiza uma célula específica na planilha e salva."""
    df = pd.read_excel(caminho, dtype=str)
    df = df.fillna("")
    df.at[indice, coluna] = valor
    df.to_excel(caminho, index=False)


def exportar_para_excel(df: pd.DataFrame, caminho: str):
    """Salva DataFrame no Excel."""
    df.to_excel(caminho, index=False)
