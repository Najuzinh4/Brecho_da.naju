import os
import requests

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL = "claude-haiku-4-5-20251001"  # rápido e barato pra sugestões inline


def claude_ajuda(tipo: str, descricao: str, categoria: str = "", preco: str = ""):
    if not ANTHROPIC_API_KEY:
        return {"erro": "ANTHROPIC_API_KEY não configurada"}

    system = (
        "Você é assistente da Brechó da Najú, brechó brasileiro Y2K/grunge/upcycling. "
        "A marca fala em português, lowercase, tom íntimo e slangy. "
        "Usa ★ ✦ como pontuação. Nunca usa corporativo."
    )

    if tipo == "descricao_instagram":
        prompt = (
            f"Crie uma legenda curta pra Instagram pra essa peça do brechó:\n"
            f"Peça: {descricao}\nCategoria: {categoria}\nPreço: R$ {preco}\n\n"
            f"Máximo 5 linhas. Estilo Najú: lowercase, estrelas, hashtags no final."
        )
    elif tipo == "sugerir_preco":
        prompt = (
            f"Sugira um preço justo pra brechó brasileiro pra essa peça:\n"
            f"{descricao}\nCategoria: {categoria}\n\n"
            f"Responda só com o valor em reais (ex: 45.00) e uma linha explicando."
        )
    elif tipo == "categorizar":
        prompt = (
            f"Categorize essa peça de brechó em UMA dessas categorias: "
            f"topo, calça, vestido, saia, jaqueta, acessório, sapato, bolsa, outro.\n"
            f"Peça: {descricao}\n\nResponda só com a categoria, sem mais nada."
        )
    else:
        return {"erro": "tipo inválido"}

    try:
        resp = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "Content-Type": "application/json",
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
            },
            json={
                "model": CLAUDE_MODEL,
                "max_tokens": 300,
                "system": system,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=20,
        )
        resp.raise_for_status()
        texto = resp.json()["content"][0]["text"]
        return {"resultado": texto}
    except Exception as e:
        return {"erro": str(e)}
