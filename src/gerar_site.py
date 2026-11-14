"""Gera o site estático (site/index.html) a partir do banco de notícias.

Uso:  python src/gerar_site.py            (últimos 3 dias)
      python src/gerar_site.py --dias 7

Como funciona: lê as notícias já processadas (Fase 2), monta uma lista de "assuntos"
(grupos) e injeta tudo no template src/templates/index.html.j2 com Jinja2.
Os filtros e a busca rodam no navegador (JavaScript), sem servidor.
"""
import argparse
import json
from datetime import datetime, timedelta, timezone

import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

from coletar import RAIZ, abrir_banco

PASTA_TEMPLATES = RAIZ / "src" / "templates"
ARQUIVO_SAIDA = RAIZ / "site" / "index.html"
ARQUIVO_CATEGORIAS = RAIZ / "config" / "categories.yaml"

# Quais categorias aparecem como "Plataforma" e quais como "Tema" nos filtros.
PLATAFORMAS = ["pc", "playstation", "xbox", "nintendo", "mobile"]
TEMAS = ["lancamentos", "industria", "rumores", "esports", "indie"]


def montar_grupos(banco, desde):
    """Junta as notícias por grupo_id. Devolve uma lista de assuntos, mais relevantes primeiro."""
    linhas = banco.execute(
        "SELECT grupo_id, fonte, idioma, titulo, link, resumo, publicado_em, categorias, "
        "n_fontes, relevancia FROM noticias "
        "WHERE publicado_em >= ? AND grupo_id IS NOT NULL ORDER BY publicado_em", (desde,)
    ).fetchall()

    grupos = {}
    for r in linhas:
        g = grupos.setdefault(r["grupo_id"], {
            "id": r["grupo_id"], "n": r["n_fontes"], "rel": r["relevancia"],
            "cats": set(), "itens": [],
        })
        g["cats"].update(r["categorias"].split(","))
        g["rel"] = max(g["rel"], r["relevancia"])
        g["itens"].append({
            "f": r["fonte"], "i": r["idioma"], "t": r["titulo"], "l": r["link"],
            "r": r["resumo"] or "", "p": r["publicado_em"],
        })

    lista = []
    for g in grupos.values():
        g["cats"] = sorted(g["cats"])
        lista.append(g)
    lista.sort(key=lambda g: -g["rel"])
    return lista


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dias", type=int, default=3, help="quantos dias de notícias no site")
    args = ap.parse_args()

    banco = abrir_banco()
    banco.row_factory = lambda cur, row: {d[0]: v for d, v in zip(cur.description, row)}
    agora = datetime.now(timezone.utc)
    desde = (agora - timedelta(days=args.dias)).isoformat(timespec="seconds")

    try:
        grupos = montar_grupos(banco, desde)
    except Exception as erro:  # acontece se o processar.py nunca foi rodado
        raise SystemExit(f"Erro lendo o banco ({erro}). Rode antes: python src/coletar.py e python src/processar.py")
    banco.close()

    nomes = {k: v["nome"] for k, v in
             yaml.safe_load(ARQUIVO_CATEGORIAS.read_text(encoding="utf-8"))["categorias"].items()}
    nomes["geral"] = "Geral"

    dados = {
        "geradoEm": agora.isoformat(timespec="seconds"),
        "nomes": nomes,
        "plataformas": PLATAFORMAS,
        "temas": TEMAS,
        "grupos": grupos,
    }

    ambiente = Environment(loader=FileSystemLoader(PASTA_TEMPLATES),
                           autoescape=select_autoescape(["html", "j2"]))
    html = ambiente.get_template("index.html.j2").render(dados=dados)
    ARQUIVO_SAIDA.parent.mkdir(exist_ok=True)
    ARQUIVO_SAIDA.write_text(html, encoding="utf-8")
    total = sum(len(g["itens"]) for g in grupos)
    print(f"Site gerado: {ARQUIVO_SAIDA}  ({len(grupos)} assuntos, {total} notícias, "
          f"{ARQUIVO_SAIDA.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
