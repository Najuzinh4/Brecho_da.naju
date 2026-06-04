import pandas as pd


def calcular_relatorio(df):
    vendidas = df[df["status"] == "vendido"].copy()
    vendidas["comissao_pct"] = pd.to_numeric(vendidas["comissao_pct"], errors="coerce").fillna(40)
    vendidas["preco"] = pd.to_numeric(vendidas["preco"], errors="coerce").fillna(0)
    vendidas["val_naju"]        = vendidas["preco"] * vendidas["comissao_pct"] / 100
    vendidas["val_fornecedora"] = vendidas["preco"] - vendidas["val_naju"]

    total_vendido = vendidas["preco"].sum()
    total_naju    = vendidas["val_naju"].sum()

    por_fornecedora = (
        vendidas.groupby("fornecedora")
        .agg(
            pecas=("codigo", "count"),
            total_vendas=("preco", "sum"),
            total_a_pagar=("val_fornecedora", "sum"),
        )
        .reset_index()
        .to_dict(orient="records")
    )

    return {
        "total_vendido": round(total_vendido, 2),
        "total_naju": round(total_naju, 2),
        "por_fornecedora": [
            {
                **r,
                "total_vendas": round(r["total_vendas"], 2),
                "total_a_pagar": round(r["total_a_pagar"], 2),
            }
            for r in por_fornecedora
        ],
    }
