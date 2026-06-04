# -*- coding: utf-8 -*-
"""
app.py — Brechó da Najú · PDV de feira (Flask + SQLite)

Rodar:
    .venv\\Scripts\\activate
    python app.py

Abre em http://127.0.0.1:5000
No iPad (mesma rede Wi-Fi): http://IP-DO-NOTEBOOK:5000
"""

import os
from datetime import datetime
from flask import (Flask, render_template, request, redirect,
                   url_for, flash, abort)
from models import (db, Fornecedora, Peca, CATEGORIAS, STATUS,
                    PRECO_ARARA, fmt_brl, proximo_codigo, build_relatorio)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "brecho-naju-2025"
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        "sqlite:///" + os.path.join(BASE_DIR, "brecho.db")
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    app.jinja_env.filters["brl"] = fmt_brl

    with app.app_context():
        db.create_all()
        from seed import seed
        seed()

    # injeta disponiveis em todos os templates automaticamente
    @app.context_processor
    def _globals():
        try:
            return {"disponiveis": Peca.query.filter_by(status="disponivel").count()}
        except Exception:
            return {"disponiveis": 0}

    register_routes(app)
    return app


def register_routes(app):

    # ── PDV ──────────────────────────────────────────────────────────────
    @app.route("/")
    def pdv():
        q = (request.args.get("q") or "").strip()
        query = Peca.query.filter(Peca.status != "vendido")
        if q:
            like = f"%{q}%"
            query = query.filter(
                db.or_(Peca.codigo.ilike(like), Peca.descricao.ilike(like))
            )
        pecas = query.order_by(Peca.codigo).all()
        sel = None
        sid = request.args.get("sel", type=int)
        if sid:
            sel = db.session.get(Peca, sid)
        return render_template("pdv.html", pecas=pecas, sel=sel, q=q, active="pdv")

    @app.route("/vender/<int:peca_id>", methods=["POST"])
    def vender(peca_id):
        p = db.session.get(Peca, peca_id)
        if p is None:
            abort(404)
        if p.status != "vendido":
            p.status = "vendido"
            p.vendido_em = datetime.now()
            db.session.commit()
            flash(f"✓ {p.codigo} vendido · {fmt_brl(p.preco)}", "venda")
        return redirect(url_for("pdv"))

    # ── Estoque ───────────────────────────────────────────────────────────
    @app.route("/estoque")
    def estoque():
        q = (request.args.get("q") or "").strip()
        cat = request.args.get("categoria") or "todas"
        forn = request.args.get("fornecedora") or "todas"
        stat = request.args.get("status") or "todos"

        query = Peca.query
        if q:
            like = f"%{q}%"
            query = query.filter(
                db.or_(Peca.codigo.ilike(like), Peca.descricao.ilike(like))
            )
        if cat != "todas":
            query = query.filter_by(categoria=cat)
        if forn != "todas":
            query = query.filter_by(fornecedora_id=int(forn))
        if stat != "todos":
            query = query.filter_by(status=stat)

        pecas = query.order_by(Peca.codigo.desc()).all()
        valor = sum(p.preco for p in pecas if p.status != "vendido")
        return render_template(
            "estoque.html", pecas=pecas,
            fornecedoras=Fornecedora.query.all(),
            categorias=CATEGORIAS, status_list=STATUS,
            f={"q": q, "categoria": cat, "fornecedora": forn, "status": stat},
            valor=valor, active="estoque",
        )

    # ── Cadastro de peça ──────────────────────────────────────────────────
    @app.route("/cadastro", methods=["GET", "POST"])
    def cadastro():
        if request.method == "POST":
            try:
                preco = float(
                    (request.form.get("preco") or "0").replace(",", ".")
                )
            except ValueError:
                preco = 0
            descricao = (request.form.get("descricao") or "").strip()
            categoria = request.form.get("categoria")
            if not descricao or not categoria or preco <= 0:
                flash("Preencha descrição, categoria e preço.", "erro")
                return redirect(url_for("cadastro"))

            p = Peca(
                codigo=request.form.get("codigo") or proximo_codigo(),
                descricao=descricao,
                categoria=categoria,
                fornecedora_id=int(request.form.get("fornecedora")),
                comissao_pct=int(request.form.get("comissao", 40)),
                preco=preco,
                status=request.form.get("status", "disponivel"),
            )
            db.session.add(p)
            db.session.commit()
            flash(f"★ Peça {p.codigo} salva no estoque", "ok")
            return redirect(url_for("cadastro"))

        return render_template(
            "cadastro.html",
            fornecedoras=Fornecedora.query.all(),
            categorias=CATEGORIAS,
            proximo=proximo_codigo(),
            preco_arara=PRECO_ARARA,
            active="cadastro",
        )

    # ── Nova fornecedora (modal) ──────────────────────────────────────────
    @app.route("/fornecedora/nova", methods=["POST"])
    def nova_fornecedora():
        nome = (request.form.get("nome") or "").strip()
        if len(nome) < 2:
            flash("Nome da fornecedora muito curto.", "erro")
            return redirect(request.referrer or url_for("pdv"))
        f = Fornecedora(
            nome=nome,
            pix=(request.form.get("pix") or "—").strip() or "—",
            comissao_padrao=int(request.form.get("comissao", 40)),
        )
        db.session.add(f)
        db.session.commit()
        flash(f"★ Fornecedora {f.nome} cadastrada", "ok")
        return redirect(request.referrer or url_for("cadastro"))

    # ── Relatório / fechamento ────────────────────────────────────────────
    @app.route("/relatorio")
    def relatorio():
        r = build_relatorio()
        return render_template(
            "relatorio.html", r=r, hoje=datetime.now(), active="relatorio"
        )

    # ── PDFs imprimíveis ──────────────────────────────────────────────────
    @app.route("/relatorio/pdf")
    def relatorio_pdf():
        r = build_relatorio()
        linhas = [l for l in r["linhas"] if not l["fornecedora"].propria]
        return render_template(
            "pdf_fechamento.html", r=r, linhas=linhas,
            single=None, agora=datetime.now()
        )

    @app.route("/relatorio/pdf/<int:forn_id>")
    def relatorio_pdf_forn(forn_id):
        r = build_relatorio()
        linha = next(
            (l for l in r["linhas"] if l["fornecedora"].id == forn_id), None
        )
        if not linha:
            abort(404)
        return render_template(
            "pdf_fechamento.html", r=r, linhas=[linha],
            single=linha["fornecedora"], agora=datetime.now()
        )

    # ── Reset (volta aos dados de exemplo) ────────────────────────────────
    @app.route("/reset", methods=["POST"])
    def reset():
        db.drop_all()
        db.create_all()
        from seed import seed
        seed()
        flash("Banco resetado pros dados de exemplo.", "ok")
        return redirect(url_for("pdv"))


app = create_app()

if __name__ == "__main__":
    print("Brecho da Naju PDV em http://localhost:5000")
    print("No iPad (mesma Wi-Fi): http://SEU-IP:5000")
    # host=0.0.0.0 permite acesso pelo iPad na mesma rede
    app.run(debug=True, host="0.0.0.0", port=5000)
