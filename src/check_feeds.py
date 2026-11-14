"""Testa quais feeds RSS realmente funcionam.

Uso:  python src/check_feeds.py
Lê config/sources.yaml (ou a lista CANDIDATOS abaixo, se o arquivo ainda não existir)
e mostra, para cada feed, se respondeu e quantas notícias trouxe.
"""
import sys
from pathlib import Path

import feedparser
import yaml

# Identificação educada: dizemos quem somos ao pedir o feed.
USER_AGENT = "GamesNewsHub/0.1 (leitor RSS pessoal)"

# Candidatos usados na primeira checagem (Fase 1).
CANDIDATOS = [
    # Brasil
    ("Adrenaline", "pt", "https://adrenaline.com.br/feed/"),
    ("Voxel", "pt", "https://voxel.com.br/feed/"),
    ("Voxel (alt)", "pt", "https://www.tecmundo.com.br/voxel/feed"),
    ("IGN Brasil", "pt", "https://br.ign.com/feed.xml"),
    ("TecMundo Games", "pt", "https://rss.tecmundo.com.br/feed"),
    ("Arkade", "pt", "https://arkade.com.br/feed/"),
    ("Memória BIT", "pt", "https://www.memoriabit.com.br/feed/"),
    ("The Enemy", "pt", "https://www.theenemy.com.br/feed"),
    ("Jovem Nerd", "pt", "https://jovemnerd.com.br/feed/"),
    ("Game Arena", "pt", "https://gamearena.com.br/feed/"),
    # Internacional
    ("IGN", "en", "https://feeds.feedburner.com/ign/all"),
    ("IGN (alt)", "en", "https://www.ign.com/rss/articles/feed?tags=games"),
    ("GameSpot", "en", "https://www.gamespot.com/feeds/mashup/"),
    ("Eurogamer", "en", "https://www.eurogamer.net/feed"),
    ("PC Gamer", "en", "https://www.pcgamer.com/rss/"),
    ("Polygon", "en", "https://www.polygon.com/rss/index.xml"),
    ("Kotaku", "en", "https://kotaku.com/rss"),
    ("VGC", "en", "https://www.videogameschronicle.com/feed/"),
    ("Rock Paper Shotgun", "en", "https://www.rockpapershotgun.com/feed"),
    ("GamesIndustry.biz", "en", "https://www.gamesindustry.biz/feed"),
    ("Nintendo Life", "en", "https://www.nintendolife.com/feeds/latest"),
    ("Push Square", "en", "https://www.pushsquare.com/feeds/latest"),
    ("Pure Xbox", "en", "https://www.purexbox.com/feeds/latest"),
]


def carregar_lista():
    cfg = Path(__file__).resolve().parent.parent / "config" / "sources.yaml"
    if cfg.exists():
        dados = yaml.safe_load(cfg.read_text(encoding="utf-8"))
        return [(s["nome"], s["idioma"], s["url"]) for s in dados["fontes"]]
    return CANDIDATOS


def main():
    ok = 0
    for nome, idioma, url in carregar_lista():
        f = feedparser.parse(url, agent=USER_AGENT)
        status = getattr(f, "status", "sem resposta")
        n = len(f.entries)
        marca = "OK  " if n > 0 else "FALHA"
        ok += n > 0
        print(f"{marca} {nome:<20} [{idioma}] status={status} itens={n}  {url}")
    print(f"\n{ok} feeds funcionando.")


if __name__ == "__main__":
    sys.exit(main())
