"""Coletor de notícias: lê os feeds de config/sources.yaml e salva no SQLite.

Uso:  python src/coletar.py

Direitos autorais: guardamos SOMENTE título, link, fonte, data e um trecho curto
(até 200 caracteres) do que vem no RSS. Nunca o texto completo nem imagens.
"""
import html
import re
import socket
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from time import mktime
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import feedparser
import yaml

RAIZ = Path(__file__).resolve().parent.parent
ARQUIVO_FONTES = RAIZ / "config" / "sources.yaml"
ARQUIVO_BANCO = RAIZ / "data" / "noticias.db"

USER_AGENT = "GamesNewsHub/0.1 (leitor RSS pessoal)"
MAX_RESUMO = 200  # limite do trecho guardado (direitos autorais)
DIAS_GUARDAR = 30  # notícias mais antigas que isso são apagadas (mantém o banco pequeno)

# Se um portal travar, desistimos depois de 20 segundos e seguimos para o próximo.
socket.setdefaulttimeout(20)


# ---------------------------------------------------------------- banco de dados
def abrir_banco():
    """Abre (e cria, se preciso) o banco SQLite."""
    ARQUIVO_BANCO.parent.mkdir(exist_ok=True)
    banco = sqlite3.connect(ARQUIVO_BANCO)
    banco.execute(
        """
        CREATE TABLE IF NOT EXISTS noticias (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            fonte        TEXT NOT NULL,
            idioma       TEXT NOT NULL,
            titulo       TEXT NOT NULL,
            link         TEXT NOT NULL UNIQUE,   -- UNIQUE = evita duplicatas
            resumo       TEXT,                   -- trecho curto (máx. 200 caracteres)
            publicado_em TEXT NOT NULL,          -- data ISO em UTC
            coletado_em  TEXT NOT NULL
        )
        """
    )
    banco.execute("CREATE INDEX IF NOT EXISTS idx_pub ON noticias(publicado_em)")
    return banco


# ---------------------------------------------------------------- limpeza de dados
def limpar_texto(texto):
    """Tira tags HTML e espaços extras."""
    texto = re.sub(r"<[^>]+>", " ", texto or "")
    texto = html.unescape(texto)
    return re.sub(r"\s+", " ", texto).strip()


def cortar(texto, limite=MAX_RESUMO):
    """Corta o texto em no máximo 'limite' caracteres, sem quebrar palavra no meio."""
    if len(texto) <= limite:
        return texto
    corte = texto[: limite - 1].rsplit(" ", 1)[0]
    return corte + "…"


def limpar_link(link):
    """Remove parâmetros de rastreamento (utm_*) para o mesmo link não entrar duas vezes."""
    partes = urlsplit(link.strip())
    consulta = [(k, v) for k, v in parse_qsl(partes.query) if not k.startswith("utm_")]
    return urlunsplit((partes.scheme, partes.netloc, partes.path, urlencode(consulta), ""))


def data_da_entrada(entrada):
    """Devolve a data da notícia em ISO/UTC (usa a data atual se o feed não informar)."""
    parsed = entrada.get("published_parsed") or entrada.get("updated_parsed")
    if parsed:
        dt = datetime.fromtimestamp(mktime(parsed), timezone.utc)
    else:
        dt = datetime.now(timezone.utc)
    return dt.isoformat(timespec="seconds")


# ---------------------------------------------------------------- coleta
def coletar_fonte(banco, fonte):
    """Lê um feed e grava as notícias novas. Devolve (novas, total_no_feed)."""
    feed = feedparser.parse(fonte["url"], agent=USER_AGENT)
    agora = datetime.now(timezone.utc).isoformat(timespec="seconds")
    limite = (datetime.now(timezone.utc) - timedelta(days=DIAS_GUARDAR)).isoformat(timespec="seconds")
    novas = 0
    for e in feed.entries:
        titulo = limpar_texto(e.get("title"))
        link = e.get("link")
        if not titulo or not link:
            continue
        if data_da_entrada(e) < limite:  # velha demais: nem entra (senão seria apagada em seguida)
            continue
        resumo = cortar(limpar_texto(e.get("summary")))
        # INSERT OR IGNORE: se o link já existe, simplesmente ignora.
        cur = banco.execute(
            "INSERT OR IGNORE INTO noticias "
            "(fonte, idioma, titulo, link, resumo, publicado_em, coletado_em) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (fonte["nome"], fonte["idioma"], titulo, limpar_link(link),
             resumo, data_da_entrada(e), agora),
        )
        novas += cur.rowcount
    return novas, len(feed.entries)


def main():
    fontes = yaml.safe_load(ARQUIVO_FONTES.read_text(encoding="utf-8"))["fontes"]
    banco = abrir_banco()
    total_novas = 0
    for fonte in fontes:
        if not fonte.get("ativo", True):
            continue
        try:
            novas, total = coletar_fonte(banco, fonte)
            banco.commit()
            total_novas += novas
            print(f"{fonte['nome']:<20} {total:>3} no feed, {novas:>3} novas")
        except Exception as erro:  # um portal com problema não derruba os outros
            print(f"{fonte['nome']:<20} ERRO: {erro}")
    # Limpeza: apaga notícias com mais de DIAS_GUARDAR dias.
    limite = (datetime.now(timezone.utc) - timedelta(days=DIAS_GUARDAR)).isoformat(timespec="seconds")
    apagadas = banco.execute("DELETE FROM noticias WHERE publicado_em < ?", (limite,)).rowcount
    banco.commit()
    if apagadas:
        print(f"Apagadas {apagadas} notícias com mais de {DIAS_GUARDAR} dias")
    total_banco = banco.execute("SELECT COUNT(*) FROM noticias").fetchone()[0]
    print(f"\nNovas nesta rodada: {total_novas} | Total no banco: {total_banco}")
    banco.close()


if __name__ == "__main__":
    main()
