"""Processa as notícias do banco: agrupa por assunto, classifica e dá nota de relevância.

Uso:  python src/processar.py            (processa os últimos 3 dias)
      python src/processar.py --dias 7   (outra janela)

O que faz:
  1. AGRUPA notícias parecidas (mesmo assunto) comparando os títulos com rapidfuzz.
  2. CLASSIFICA cada notícia em categorias, usando config/categories.yaml.
  3. Dá uma NOTA DE RELEVÂNCIA: quanto mais portais diferentes cobrem o assunto, maior a nota.

Resultado: colunas novas na tabela "noticias" (grupo_id, n_fontes, categorias, relevancia).
Limitação conhecida: o agrupamento compara títulos no mesmo idioma. Uma notícia em português
e a mesma em inglês normalmente NÃO se juntam (títulos muito diferentes).
"""
import argparse
import re
import unicodedata
from datetime import datetime, timedelta, timezone

import yaml
from rapidfuzz import fuzz, process

from coletar import RAIZ, abrir_banco

ARQUIVO_CATEGORIAS = RAIZ / "config" / "categories.yaml"

# ---- Ajustes (mexa aqui se o agrupamento ficar "solto" ou "apertado" demais) ----
LIMIAR_SIMILARIDADE = 78   # 0-100. Maior = só junta títulos muito parecidos.
MIN_PALAVRAS_COMUNS = 3    # exigido quando a comparação é por "subconjunto" de palavras
PONTOS_POR_FONTE = 10      # cada portal diferente cobrindo o assunto vale 10 pontos
BONUS_RECENCIA_MAX = 5     # notícia recém-publicada ganha até 5 pontos (cai até 0 em 30h)

# Palavras sem significado que atrapalham a comparação de títulos.
PALAVRAS_VAZIAS = set("""
a o as os um uma de da do das dos em no na nos nas para por com sem e ou que se
the an of in on at to for and or is are was be with from by as it its this that
new novo nova how why what when after before about
""".split())


# ---------------------------------------------------------------- texto
def sem_acento(texto):
    """'Lançamento' -> 'lancamento' (facilita comparações)."""
    return "".join(c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn")


def palavras_do_titulo(titulo):
    """Lista de palavras 'importantes' do título, em minúsculas e sem acento/pontuação."""
    texto = re.sub(r"[^\w\s]", " ", sem_acento(titulo).lower())
    return [p for p in texto.split() if p not in PALAVRAS_VAZIAS and len(p) > 1]


# ---------------------------------------------------------------- categorias
def carregar_categorias():
    cfg = yaml.safe_load(ARQUIVO_CATEGORIAS.read_text(encoding="utf-8"))
    regras = {}
    for chave, dados in cfg["categorias"].items():
        # Uma expressão regular por categoria: palavra inteira, sem acento, sem maiúscula.
        palavras = [re.escape(sem_acento(str(p).lower())) for p in dados["palavras"]]
        regras[chave] = re.compile(r"(?<!\w)(?:" + "|".join(palavras) + r")(?!\w)")
    ignorar = [sem_acento(str(t).lower()) for t in cfg.get("ignorar_agrupamento", [])]
    return regras, cfg.get("categorias_por_fonte", {}), ignorar


def classificar(titulo, resumo, fonte, regras, por_fonte):
    """Devolve as categorias da notícia, separadas por vírgula (ex.: 'xbox,lancamentos')."""
    texto = sem_acento(f"{titulo} {resumo or ''}".lower())
    achadas = [chave for chave, padrao in regras.items() if padrao.search(texto)]
    if fonte in por_fonte and por_fonte[fonte] not in achadas:
        achadas.append(por_fonte[fonte])
    return ",".join(achadas) if achadas else "geral"


# ---------------------------------------------------------------- agrupamento
def agrupar(noticias, ignorar):
    """Junta notícias com títulos parecidos. Devolve uma lista: o grupo (id) de cada notícia."""
    n = len(noticias)
    palavras = [palavras_do_titulo(t["titulo"]) for t in noticias]
    textos = [" ".join(p) for p in palavras]
    # Títulos de colunas recorrentes ficam sozinhos (nunca entram em grupo).
    sozinhas = {i for i, t in enumerate(noticias)
                if any(trecho in sem_acento(t["titulo"].lower()) for trecho in ignorar)}

    # "Union-find": estrutura simples para ir juntando notícias em grupos.
    pai = list(range(n))

    def raiz(i):
        while pai[i] != i:
            pai[i] = pai[pai[i]]
            i = pai[i]
        return i

    for i in range(n):
        if i in sozinhas:
            continue
        outros = textos[i + 1:]
        # Títulos com as mesmas palavras (em qualquer ordem) -> similaridade alta.
        # extract devolve (texto, nota, posição) só dos que passam do limiar.
        for _, _, k in process.extract(textos[i], outros, scorer=fuzz.token_sort_ratio,
                                       score_cutoff=LIMIAR_SIMILARIDADE, limit=None):
            if i + 1 + k not in sozinhas:
                pai[raiz(i + 1 + k)] = raiz(i)
        # Um título "contido" no outro só vale se tiverem várias palavras em comum
        # (evita juntar "Zelda" com qualquer título que cite Zelda).
        for _, _, k in process.extract(textos[i], outros, scorer=fuzz.token_set_ratio,
                                       score_cutoff=LIMIAR_SIMILARIDADE, limit=None):
            j = i + 1 + k
            if j not in sozinhas and len(set(palavras[i]) & set(palavras[j])) >= MIN_PALAVRAS_COMUNS:
                pai[raiz(j)] = raiz(i)

    return [raiz(i) for i in range(n)]


def nota_recencia(publicado_em, agora):
    horas = (agora - datetime.fromisoformat(publicado_em)).total_seconds() / 3600
    return max(0.0, BONUS_RECENCIA_MAX * (1 - horas / 30))


# ---------------------------------------------------------------- principal
def preparar_colunas(banco):
    """Cria as colunas novas na primeira vez (não mexe se já existirem)."""
    existentes = {c["name"] for c in banco.execute("PRAGMA table_info(noticias)")}
    novas = {"grupo_id": "INTEGER", "n_fontes": "INTEGER", "categorias": "TEXT", "relevancia": "REAL"}
    for nome, tipo in novas.items():
        if nome not in existentes:
            banco.execute(f"ALTER TABLE noticias ADD COLUMN {nome} {tipo}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dias", type=int, default=3, help="janela de dias a processar")
    args = ap.parse_args()

    banco = abrir_banco()
    banco.row_factory = lambda cur, row: {d[0]: v for d, v in zip(cur.description, row)}
    preparar_colunas(banco)

    agora = datetime.now(timezone.utc)
    desde = (agora - timedelta(days=args.dias)).isoformat(timespec="seconds")
    noticias = banco.execute(
        "SELECT id, fonte, titulo, resumo, publicado_em FROM noticias "
        "WHERE publicado_em >= ? ORDER BY publicado_em", (desde,)
    ).fetchall()
    if not noticias:
        print("Nenhuma notícia na janela. Rode primeiro: python src/coletar.py")
        return

    regras, por_fonte, ignorar = carregar_categorias()
    raizes = agrupar(noticias, ignorar)

    # Quantas fontes DIFERENTES há em cada grupo?
    fontes_do_grupo = {}
    for noticia, r in zip(noticias, raizes):
        fontes_do_grupo.setdefault(r, set()).add(noticia["fonte"])

    for noticia, r in zip(noticias, raizes):
        n_fontes = len(fontes_do_grupo[r])
        relevancia = n_fontes * PONTOS_POR_FONTE + nota_recencia(noticia["publicado_em"], agora)
        banco.execute(
            "UPDATE noticias SET grupo_id=?, n_fontes=?, categorias=?, relevancia=? WHERE id=?",
            (noticias[r]["id"], n_fontes,  # grupo_id = id da notícia "líder" do grupo
             classificar(noticia["titulo"], noticia["resumo"], noticia["fonte"], regras, por_fonte),
             round(relevancia, 1), noticia["id"]),
        )
    banco.commit()
    relatorio(banco, desde, len(noticias), len(fontes_do_grupo))
    banco.close()


def relatorio(banco, desde, total, n_grupos):
    print(f"{total} notícias processadas -> {n_grupos} assuntos distintos\n")
    print("Categorias:")
    contagem = {}
    for linha in banco.execute("SELECT categorias FROM noticias WHERE publicado_em >= ?", (desde,)):
        for c in linha["categorias"].split(","):
            contagem[c] = contagem.get(c, 0) + 1
    for c, q in sorted(contagem.items(), key=lambda x: -x[1]):
        print(f"  {c:<12} {q}")

    print("\nAssuntos mais cobertos:")
    top = banco.execute(
        "SELECT grupo_id, MAX(n_fontes) AS f, MAX(relevancia) AS r FROM noticias "
        "WHERE publicado_em >= ? GROUP BY grupo_id ORDER BY f DESC, r DESC LIMIT 10", (desde,)
    ).fetchall()
    for g in top:
        lider = banco.execute("SELECT titulo, categorias FROM noticias WHERE grupo_id=? "
                              "ORDER BY relevancia DESC LIMIT 1", (g["grupo_id"],)).fetchone()
        print(f"  [{g['f']} fontes | nota {g['r']}] {lider['titulo'][:80]}  ({lider['categorias']})")


if __name__ == "__main__":
    main()
