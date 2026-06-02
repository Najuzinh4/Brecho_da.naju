"""
code_service.py — geração automática de códigos de peça

Regra:
  código = INICIAL(fornecedora) + número sequencial com 3 dígitos

Exemplos:
  Najú      → N001, N002, N003…
  Leticia   → L001, L002, L003…
  Ana Paula → A001, A002…

A inicial é extraída via regex: primeiro caractere alfabético do nome,
normalizado (sem acento, uppercase).
"""

import re
import unicodedata
import pandas as pd


# ── normalização ──────────────────────────────────────────────────────────────

def _normalizar_inicial(nome: str) -> str:
    """
    Extrai e normaliza a inicial do nome da fornecedora.
    Remove acentos, pega o primeiro caractere alfabético, uppercase.

    'Najú'      → 'N'
    'leticia'   → 'L'
    'ângela'    → 'A'
    '123Ana'    → 'A'   (ignora números no início)
    ''          → 'X'   (fallback)
    """
    if not nome or not nome.strip():
        return "X"

    # remove acentos via NFD + strip de combining chars
    normalizado = unicodedata.normalize("NFD", nome.strip())
    sem_acento = "".join(c for c in normalizado if unicodedata.category(c) != "Mn")

    # pega o primeiro caractere alfabético via regex
    match = re.search(r"[A-Za-z]", sem_acento)
    if not match:
        return "X"

    return match.group(0).upper()


# ── geração de código ─────────────────────────────────────────────────────────

def gerar_codigo(fornecedora: str, codigos_existentes: list[str]) -> str:
    """
    Gera o próximo código disponível para a fornecedora.

    Args:
        fornecedora: nome da fornecedora (ex: "Leticia")
        codigos_existentes: lista de todos os códigos já cadastrados

    Returns:
        Próximo código no formato LNNN (ex: "L007")
    """
    inicial = _normalizar_inicial(fornecedora)

    # regex pra encontrar todos os códigos da mesma inicial: L001, L002, etc.
    padrao = re.compile(rf"^{re.escape(inicial)}(\d+)$", re.IGNORECASE)

    numeros_usados = []
    for cod in codigos_existentes:
        m = padrao.match(str(cod).strip())
        if m:
            numeros_usados.append(int(m.group(1)))

    proximo = max(numeros_usados, default=0) + 1
    return f"{inicial}{proximo:03d}"


# ── integração com o Excel ────────────────────────────────────────────────────

def proximo_codigo_para(fornecedora: str, df: pd.DataFrame) -> str:
    """
    Wrapper conveniente: recebe o DataFrame atual e retorna o próximo código.

    Uso no app.py:
        from code_service import proximo_codigo_para
        df = load_pecas()
        codigo = proximo_codigo_para("Leticia", df)  # → "L001"
    """
    codigos = df["codigo"].astype(str).tolist() if not df.empty else []
    return gerar_codigo(fornecedora, codigos)
