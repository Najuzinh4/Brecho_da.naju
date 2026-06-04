import re
import unicodedata
import pandas as pd


def _normalizar_inicial(nome: str) -> str:
    if not nome or not nome.strip():
        return "X"
    normalizado = unicodedata.normalize("NFD", nome.strip())
    sem_acento = "".join(c for c in normalizado if unicodedata.category(c) != "Mn")
    match = re.search(r"[A-Za-z]", sem_acento)
    if not match:
        return "X"
    return match.group(0).upper()


def gerar_codigo(fornecedora: str, codigos_existentes: list) -> str:
    inicial = _normalizar_inicial(fornecedora)
    padrao = re.compile(rf"^{re.escape(inicial)}(\d+)$", re.IGNORECASE)
    numeros_usados = []
    for cod in codigos_existentes:
        m = padrao.match(str(cod).strip())
        if m:
            numeros_usados.append(int(m.group(1)))
    proximo = max(numeros_usados, default=0) + 1
    return f"{inicial}{proximo:03d}"


def proximo_codigo_para(fornecedora: str, df: pd.DataFrame) -> str:
    codigos = df["codigo"].astype(str).tolist() if not df.empty else []
    return gerar_codigo(fornecedora, codigos)
