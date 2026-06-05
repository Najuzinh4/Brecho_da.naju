# -*- coding: utf-8 -*-
import re
import unicodedata
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

PRECO_ARARA = 5.0
CATEGORIAS = ["vestido", "blusa", "calça", "saia", "jaqueta", "conjunto", "acessório", "sapato"]
STATUS = ["disponivel", "reservado", "vendido"]


class Fornecedora(db.Model):
    __tablename__ = "fornecedoras"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    pix = db.Column(db.String(160), default="—")
    propria = db.Column(db.Boolean, default=False)
    comissao_padrao = db.Column(db.Integer, default=40)

    pecas = db.relationship("Peca", backref="fornecedora", lazy=True)

    def to_dict(self):
        return {"id": self.id, "nome": self.nome, "pix": self.pix,
                "propria": self.propria, "comissao_padrao": self.comissao_padrao}


class Peca(db.Model):
    __tablename__ = "pecas"

    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(24), unique=True, nullable=False)
    descricao = db.Column(db.String(240), nullable=False)
    categoria = db.Column(db.String(40), nullable=False)
    fornecedora_id = db.Column(db.Integer, db.ForeignKey("fornecedoras.id"), nullable=False)
    comissao_pct = db.Column(db.Integer, default=40)
    preco = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(16), default="disponivel")
    vendido_em = db.Column(db.DateTime, nullable=True)

    # ── Regra da arara: peça de R$5 vai 100% pra fornecedora ─────────────
    @property
    def is_arara(self):
        return float(self.preco) == PRECO_ARARA

    @property
    def comissao_efetiva(self):
        return 0 if self.is_arara else (self.comissao_pct or 0)

    @property
    def fica_naju(self):
        return round(self.preco * self.comissao_efetiva / 100.0, 2)

    @property
    def pix_fornecedora(self):
        return round(self.preco * (100 - self.comissao_efetiva) / 100.0, 2)

    @property
    def vendido_hoje(self):
        if not self.vendido_em:
            return False
        return self.vendido_em.date() == datetime.now().date()

    def to_dict(self):
        return {
            "id": self.id, "codigo": self.codigo, "descricao": self.descricao,
            "categoria": self.categoria, "fornecedora_id": self.fornecedora_id,
            "fornecedora": self.fornecedora.nome if self.fornecedora else "",
            "comissao_pct": self.comissao_pct, "comissao_efetiva": self.comissao_efetiva,
            "preco": self.preco, "status": self.status, "is_arara": self.is_arara,
            "fica_naju": self.fica_naju, "pix_fornecedora": self.pix_fornecedora,
            "vendido_em": self.vendido_em.isoformat() if self.vendido_em else None,
        }


def fmt_brl(valor):
    s = f"{float(valor or 0):,.2f}"
    s = s.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {s}"


def _inicial(nome: str) -> str:
    """Retorna a primeira letra do nome sem acento, maiúscula."""
    sem_acento = unicodedata.normalize("NFD", nome or "")
    sem_acento = "".join(c for c in sem_acento if unicodedata.category(c) != "Mn")
    for ch in sem_acento:
        if ch.isalpha():
            return ch.upper()
    return "X"


def proximo_codigo(fornecedora_id=None):
    """Gera o próximo código com a inicial da fornecedora: N001, T002…"""
    inicial = "N"
    if fornecedora_id:
        f = db.session.get(Fornecedora, fornecedora_id)
        if f:
            inicial = _inicial(f.nome)

    padrao = re.compile(rf"^{re.escape(inicial)}(\d+)$", re.IGNORECASE)
    maior = 0
    for p in Peca.query.all():
        m = padrao.match(p.codigo or "")
        if m:
            maior = max(maior, int(m.group(1)))
    return f"{inicial}{maior + 1:03d}"


def build_relatorio():
    vendidas = [p for p in Peca.query.filter_by(status="vendido").all() if p.vendido_hoje]

    por_forn = {}
    for p in vendidas:
        fid = p.fornecedora_id
        if fid not in por_forn:
            por_forn[fid] = {
                "fornecedora": p.fornecedora, "qtd": 0,
                "bruto": 0.0, "comissao": 0.0, "pix": 0.0, "pecas": [],
            }
        r = por_forn[fid]
        r["qtd"] += 1
        r["bruto"] += p.preco
        r["comissao"] += p.fica_naju
        r["pix"] += p.pix_fornecedora
        r["pecas"].append(p)

    linhas = sorted(por_forn.values(), key=lambda r: r["pix"], reverse=True)
    return {
        "linhas": linhas,
        "qtd": len(vendidas),
        "total_bruto": round(sum(p.preco for p in vendidas), 2),
        "total_comissao": round(sum(p.fica_naju for p in vendidas), 2),
        "total_pix": round(sum(p.pix_fornecedora for p in vendidas), 2),
    }
