import json
import os
from dataclasses import dataclass, field
from typing import List

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, "config", "config.json")


@dataclass
class EmpresaConfig:
    nome: str
    responsavel: str
    instagram: str
    site: str
    whatsapp: str


@dataclass
class AppConfig:
    modo: str
    numeros_teste: List[str]
    empresa: EmpresaConfig
    pausa_entre_envios_segundos: int
    pausa_variacao_segundos: int
    arquivo_parceiros: str
    arquivo_log: str
    template_ativo: str

    @property
    def is_teste(self) -> bool:
        return self.modo.upper() == "TESTE"

    @property
    def caminho_parceiros(self) -> str:
        return os.path.join(BASE_DIR, self.arquivo_parceiros)

    @property
    def caminho_log(self) -> str:
        return os.path.join(BASE_DIR, self.arquivo_log)

    @property
    def caminho_template(self) -> str:
        return os.path.join(BASE_DIR, "templates", self.template_ativo)


def carregar_config() -> AppConfig:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        dados = json.load(f)

    empresa = EmpresaConfig(**dados["empresa"])

    return AppConfig(
        modo=dados["modo"],
        numeros_teste=dados["numeros_teste"],
        empresa=empresa,
        pausa_entre_envios_segundos=dados["pausa_entre_envios_segundos"],
        pausa_variacao_segundos=dados["pausa_variacao_segundos"],
        arquivo_parceiros=dados["arquivo_parceiros"],
        arquivo_log=dados["arquivo_log"],
        template_ativo=dados["template_ativo"],
    )


def salvar_modo(modo: str):
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        dados = json.load(f)
    dados["modo"] = modo.upper()
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
