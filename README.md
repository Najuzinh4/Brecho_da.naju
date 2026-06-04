# Brechó da Najú · PDV ★

Sistema de ponto de venda para uso na feira — vende peça por peça, controla estoque, cadastra peças e fornecedoras, e fecha o dia com o **pix de cada fornecedora** (inclui PDF individual pra mandar pra cada uma).

---

## Como rodar

> Precisa ter **Python 3.10+** instalado.

```bash
# 1. criar e ativar o ambiente virtual
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Mac / Linux

# 2. instalar dependências
pip install -r requirements.txt

# 3. rodar
python app.py
```

Abre em **<http://localhost:5000>**

O banco (`brecho.db`) é criado e populado com dados de exemplo na primeira vez automaticamente.

### Usar no iPad na feira

Com notebook e iPad na **mesma rede Wi-Fi**, o terminal mostra o IP:

```txt
Running on http://192.168.x.x:5000
```

Acessa esse endereço no iPad.

---

## As 4 telas

- **PDV** `/` — busca peça por código/descrição → seleciona → "DAR BAIXA"
- **Estoque** `/estoque` — tabela com filtros: categoria, fornecedora, status
- **Cadastrar** `/cadastro` — cadastro de nova **peça** ou nova **fornecedora**
- **Fechamento** `/relatorio` — totais do dia + pix por fornecedora + PDFs

---

## Regras de comissão

- `comissao_pct` = **% que o brechó (Najú) retém** de cada peça
- A fornecedora recebe o resto: `pix = preço × (100 − comissao_pct) / 100`
- Padrão **40% Najú / 60% fornecedora** — personalizável por peça
- **0%** = 100% pra fornecedora (ex: peças da mãe)
- **100%** = peça própria da Najú (não entra nos repasses)
- **Regra da arara:** peça de **exatamente R$5** vai 100% pra fornecedora, independente da % combinada

---

## Banco de dados

SQLite — arquivo `brecho.db` gerado localmente, funciona **sem internet**.
Pra resetar pros dados de exemplo: botão **↺** no topo do app.
