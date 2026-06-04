# -*- coding: utf-8 -*-
"""
seed.py — popula o banco com fornecedoras e peças de exemplo.
Roda automaticamente na primeira vez (banco vazio).
"""

from datetime import datetime
from models import db, Fornecedora, Peca


def seed():
    if Fornecedora.query.first():
        return  # já populado

    fornecedoras = [
        Fornecedora(nome="Najú (própria)", pix="—", propria=True, comissao_padrao=100),
        Fornecedora(nome="Mãe (Dona Cleide)", pix="(11) 98888-1111", comissao_padrao=0),
        Fornecedora(nome="Tia Lu", pix="tialu@pix.com", comissao_padrao=40),
        Fornecedora(nome="Cacá Vintage", pix="(11) 99812-4400", comissao_padrao=40),
        Fornecedora(nome="Mari Brechó", pix="mari.brecho@gmail.com", comissao_padrao=50),
    ]
    db.session.add_all(fornecedoras)
    db.session.flush()

    naju, mae, tialu, caca, mari = fornecedoras

    pecas = [
        # (codigo, descricao, categoria, fornecedora, comissao_pct, preco, status)
        ("NJ-001", "Vestido slip cetim tam M",   "vestido",   tialu, 40,  89,  "disponivel"),
        ("NJ-002", "Jaqueta de couro vintage G", "jaqueta",   caca,  40,  140, "disponivel"),
        ("NJ-003", "Cropped print borboleta P",  "blusa",     naju,  100, 59,  "disponivel"),
        ("NJ-004", "Calça cargo baggy G",        "calça",     mari,  50,  95,  "disponivel"),
        ("NJ-005", "Saia jeans midi M",          "saia",      tialu, 40,  72,  "disponivel"),
        ("NJ-006", "Blusa de tricô da mãe",      "blusa",     mae,   0,   45,  "disponivel"),
        ("NJ-007", "Coturno couro nº37",         "sapato",    caca,  40,  120, "disponivel"),
        ("NJ-008", "Corrente prata handmade",    "acessório", naju,  100, 45,  "disponivel"),
        ("NJ-009", "Camiseta básica (arara)",    "blusa",     tialu, 40,  5,   "disponivel"),
        ("NJ-010", "Vestido floral anos 90 G",   "vestido",   tialu, 40,  84,  "disponivel"),
        ("NJ-011", "Calça flare veludo M",       "calça",     mari,  50,  78,  "disponivel"),
        ("NJ-012", "Jaqueta jeans destroyed M",  "jaqueta",   caca,  40,  110, "reservado"),
        # vendidas hoje — aparecem no fechamento
        ("NJ-013", "Vestido vermelho festa M",   "vestido",   tialu, 40,  98,  "vendido"),
        ("NJ-014", "Bolsa baguete chrome",       "acessório", caca,  40,  67,  "vendido"),
        ("NJ-015", "Saia plissada da mãe",       "saia",      mae,   0,   55,  "vendido"),
        ("NJ-016", "Camiseta band tee (arara)",  "blusa",     mari,  50,  5,   "vendido"),
    ]

    for cod, desc, cat, forn, com, preco, status in pecas:
        p = Peca(
            codigo=cod, descricao=desc, categoria=cat,
            fornecedora_id=forn.id, comissao_pct=com,
            preco=float(preco), status=status,
        )
        if status == "vendido":
            p.vendido_em = datetime.now()
        db.session.add(p)

    db.session.commit()
    print("Banco populado com dados de exemplo.")


if __name__ == "__main__":
    from app import app
    with app.app_context():
        db.create_all()
        seed()
