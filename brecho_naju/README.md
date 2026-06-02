# brechó da najú ★ PDV

Sistema de ponto de venda + gestão de estoque para a feira.

## Como rodar

```bash
# 1. instalar dependências (só na primeira vez)
pip install -r requirements.txt

# 2. rodar o app
python app.py

# 3. abrir no navegador
# http://localhost:5000
```

## O que o app faz

- **PDV**: digita o código da peça → mostra info → dá baixa na venda
- **Estoque**: visualiza todas as peças, filtra por status/fornecedora
- **Cadastro**: adiciona peças com código, descrição, fornecedora e % de comissão
- **Relatório**: mostra total vendido, quanto fica pra Najú e **quanto enviar no pix pra cada fornecedora**

## Claude AI (precisa de internet)

No PDV e no cadastro tem botões pra usar o Claude:
- Gerar legenda pro Instagram
- Sugerir preço baseado na descrição
- Auto-categorizar a peça

## Banco de dados

Tudo salvo em `pecas.xlsx` na mesma pasta — pode abrir no Excel também.

## Comissões

- Padrão: 40% fica pra Najú, 60% vai pra fornecedora
- Personalizável por peça no momento do cadastro (campo "comissão najú %")
- O relatório já calcula tudo automaticamente ★
