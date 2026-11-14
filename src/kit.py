"""Kit de conteúdo SEM ROSTO: gera roteiros, carrosséis, texto animado e legendas.

Uso:  python src/kit.py                 kit do dia (e Top 5 da semana, se for domingo)
      python src/kit.py --semanal       força o Top 5 da semana
      python src/kit.py --so-site       só atualiza o site (não grava em content/) - usado no Actions
      python src/kit.py --forcar        sobrescreve o arquivo do dia em content/ (cuidado: apaga suas edições!)

Como funciona: escolhe as notícias mais relevantes (Fase 2) e monta os textos a partir de MODELOS
FIXOS (sem IA paga). Os modelos são só um ponto de partida: você revisa e edita antes de publicar.
Cada notícia também traz um PROMPT pronto para colar no Claude/ChatGPT e refinar o roteiro.

Direitos autorais: usamos só título, link, fonte e o trecho curto do RSS. Nada é publicado
automaticamente. As sugestões de imagem são sempre material OFICIAL (trailer, key art, press kit).
"""
import argparse
import re
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

from coletar import RAIZ, abrir_banco
from processar import carregar_categorias, sem_acento

PASTA_SITE = RAIZ / "site"
PASTA_CONTENT = RAIZ / "content"
PASTA_TEMPLATES = RAIZ / "src" / "templates"
ARQUIVO_CATEGORIAS = RAIZ / "config" / "categories.yaml"

BRT = timezone(timedelta(hours=-3))  # horário de Brasília (sem horário de verão atualmente)
MIN_NOTICIAS, MAX_NOTICIAS = 5, 8
PLATAFORMAS = ["playstation", "xbox", "nintendo", "pc", "mobile"]

# ---------------------------------------------------------------- MODELOS DE TEXTO (edite à vontade!)
# Gancho de abertura (primeiros 3 segundos), por categoria principal. {t} = título curto.
GANCHOS = {
    "rumores": "Olha esse rumor: {t}",
    "lancamentos": "Novidade quente: {t}",
    "industria": "Movimento forte na indústria: {t}",
    "esports": "Esports em alta: {t}",
    "mobile": "Quem joga no celular, atenção: {t}",
    "indie": "Joia indie na área: {t}",
    "pc": "Jogador de PC, olha isso: {t}",
    "playstation": "Quem joga de PlayStation precisa saber: {t}",
    "xbox": "Quem joga de Xbox precisa saber: {t}",
    "nintendo": "Fã de Nintendo, olha isso: {t}",
    "geral": "Você viu isso? {t}",
}
# Terceiro ponto ("por que importa"), por categoria principal. Os [colchetes] são para VOCÊ preencher.
POR_QUE_IMPORTA = {
    "rumores": "Ainda é rumor, sem confirmação oficial. Vale esperar o anúncio. [ADICIONE: o que falta confirmar]",
    "lancamentos": "Fique de olho na data e nas plataformas. [ADICIONE: data e plataformas confirmadas]",
    "industria": "Isso pode mexer com jogos, preços e empregos. [ADICIONE: impacto para o jogador]",
    "esports": "Quem acompanha o competitivo vai querer ver isso de perto. [ADICIONE: times ou campeonato]",
    "mobile": "Quem joga no celular pode sentir a diferença rápido. [ADICIONE: quando chega]",
    "indie": "Mais um motivo para dar chance aos jogos independentes. [ADICIONE: onde jogar]",
    "pc": "Quem joga no PC pode se beneficiar disso. [ADICIONE: requisitos ou loja]",
    "playstation": "Fãs de PlayStation vão querer acompanhar os próximos passos. [ADICIONE: detalhe]",
    "xbox": "Fãs de Xbox vão querer acompanhar os próximos passos. [ADICIONE: detalhe]",
    "nintendo": "Fãs de Nintendo vão querer acompanhar os próximos passos. [ADICIONE: detalhe]",
    "geral": "Vale ficar de olho nos próximos desdobramentos. [ADICIONE: seu ponto de vista]",
}
# Pergunta final para o público, por categoria principal.
PERGUNTAS = {
    "rumores": "Você acredita nesse rumor? Conta nos comentários.",
    "lancamentos": "Você vai jogar? Conta nos comentários.",
    "industria": "Isso é bom ou ruim para os jogadores? Comenta aí.",
    "esports": "Quem leva essa? Comenta aí.",
    "mobile": "Você joga no celular? Me conta nos comentários.",
    "indie": "Qual é o seu indie favorito? Comenta aí.",
    "pc": "Você joga no PC? Me conta nos comentários.",
    "playstation": "Você joga de PlayStation? Me conta nos comentários.",
    "xbox": "Você joga de Xbox? Me conta nos comentários.",
    "nintendo": "Você joga de Nintendo? Me conta nos comentários.",
    "geral": "E você, o que achou? Comenta aí.",
}
# Onde procurar material de imagem/vídeo OFICIAL, por categoria principal.
MATERIAL = {
    "rumores": "Sem material oficial ainda: use logo e key art oficiais (press kit) com texto na tela. Evite mostrar o 'vazamento' como se fosse confirmado.",
    "lancamentos": "Trailer oficial (canal da publicadora no YouTube), key art e screenshots oficiais (página oficial do jogo ou press kit).",
    "industria": "Logo oficial da empresa (press kit) + gráficos/texto simples feitos por você.",
    "esports": "Transmissão e canais oficiais do campeonato/organizadora (confira as regras de uso), key art do jogo (press kit).",
    "mobile": "Trailer oficial no canal da publicadora, páginas oficiais na App Store/Google Play, gameplay próprio.",
    "indie": "Trailer e screenshots oficiais na página do jogo (Steam, itch.io) ou no press kit do estúdio.",
    "pc": "Trailer oficial (canal da publicadora no YouTube), screenshots oficiais na página da Steam/Epic, gameplay próprio.",
    "playstation": "Trailer oficial no canal PlayStation/da publicadora, screenshots oficiais na PlayStation Store ou press kit.",
    "xbox": "Trailer oficial no canal Xbox/da publicadora, screenshots oficiais na Xbox Store ou press kit.",
    "nintendo": "Trailer oficial no canal Nintendo/da publicadora, screenshots oficiais na eShop ou press kit.",
    "geral": "Trailer oficial, key art e screenshots oficiais (página oficial ou press kit). Gameplay próprio, se tiver.",
}
HASHTAGS_BASE = ["#games", "#gamer", "#noticiasdegames"]
HASHTAGS = {
    "lancamentos": ["#lancamento", "#novojogo"], "rumores": ["#rumor", "#vazamento"],
    "industria": ["#industriadegames"], "esports": ["#esports"], "mobile": ["#mobilegames"],
    "indie": ["#indiegames"], "pc": ["#pcgaming"], "playstation": ["#playstation", "#ps5"],
    "xbox": ["#xbox", "#gamepass"], "nintendo": ["#nintendo", "#switch"],
}
AVISO_IMAGENS = "Nunca printe imagens de matérias de outros portais: use só material oficial."


# ---------------------------------------------------------------- utilidades de texto
def encurtar(texto, limite):
    """Corta em 'limite' caracteres sem quebrar palavra."""
    texto = texto.strip()
    if len(texto) <= limite:
        return texto
    return texto[: limite - 1].rsplit(" ", 1)[0].rstrip(" ,;:-–") + "…"


def limitar_palavras(texto, n):
    palavras = texto.split()
    return " ".join(palavras[:n]) + ("…" if len(palavras) > n else "")


def limpar_resumo(resumo):
    """Tira avisos comuns de RSS ('The post ... appeared first on', 'Leia mais')."""
    r = re.sub(r"\s*(The post .*appeared first on.*|Read more.*|Leia mais.*|Continue reading.*)$", "",
               resumo or "", flags=re.I)
    return r.strip(" …")


def primeira_frase(texto, limite=140):
    frases = re.split(r"(?<=[.!?])\s+", texto.strip())
    return encurtar(frases[0], limite) if frases and frases[0] else ""


def pedacos(texto, tamanho=6, maximo=3):
    """Quebra o texto em frases curtas de até 'tamanho' palavras (para o texto animado)."""
    p = texto.split()
    return [" ".join(p[i:i + tamanho]) for i in range(0, min(len(p), tamanho * maximo), tamanho)]


def hashtags(categorias):
    tags = list(HASHTAGS_BASE)
    for c in categorias:
        tags += HASHTAGS.get(c, [])
    tags = list(dict.fromkeys(tags))
    for extra in ["#gamesbrasil", "#tiktokgames"]:  # garante o mínimo de 5
        if len(tags) < 5:
            tags.append(extra)
    return tags[:8]


def categoria_principal(contagem):
    """Categoria que aparece em MAIS notícias do assunto (empate: temas antes de plataformas).
    Evita que uma única fonte com a palavra 'rumor' defina o assunto inteiro."""
    ordem = ["lancamentos", "industria", "rumores", "esports", "indie"] + PLATAFORMAS
    validas = [c for c in ordem if contagem.get(c)]
    if contagem.get("rumores", 0) < 2 and "rumores" in validas:
        validas.remove("rumores")  # 'rumor' só vale se mais de uma fonte indicar (evita falso rumor)
    if not validas:
        return "geral"
    return max(validas, key=lambda c: (contagem[c], -ordem.index(c)))


def sem_aspas(texto):
    """Troca aspas duplas por simples (os textos falados ficam entre aspas duplas)."""
    return texto.replace('"', "'").replace("“", "'").replace("”", "'")


# ---------------------------------------------------------------- seleção das notícias
def carregar_grupos(banco, desde, ignorar):
    """Lê as notícias da janela e junta por assunto. Devolve lista de dicionários."""
    linhas = banco.execute(
        "SELECT grupo_id, fonte, idioma, titulo, link, resumo, publicado_em, categorias, "
        "n_fontes, relevancia FROM noticias WHERE publicado_em >= ? AND grupo_id IS NOT NULL "
        "ORDER BY publicado_em", (desde,)).fetchall()
    grupos = {}
    for r in linhas:
        if any(t in sem_acento(r["titulo"].lower()) for t in ignorar):
            continue  # colunas recorrentes ("Talking Point"...) não viram kit
        g = grupos.setdefault(r["grupo_id"], {"id": r["grupo_id"], "itens": [], "cats": set(),
                                              "cont": Counter(), "n": r["n_fontes"], "rel": r["relevancia"]})
        g["itens"].append(r)
        g["cats"].update(r["categorias"].split(","))
        g["cont"].update(set(r["categorias"].split(",")) - {"geral"})  # em quantas notícias cada categoria aparece
        g["rel"] = max(g["rel"], r["relevancia"])
    # "geral" sozinho costuma ser assunto fora de games (cinema, Black Friday): fora do kit.
    return [g for g in grupos.values() if g["cats"] != {"geral"}]


def escolher_item(itens):
    """Prefere a notícia em português (para o resumo); entre iguais, a de trecho mais longo."""
    base = [i for i in itens if i["idioma"] == "pt"] or itens
    return max(base, key=lambda i: len(i["resumo"] or ""))


def fontes_unicas(itens):
    vistas, saida = set(), []
    for i in itens:
        if i["fonte"] not in vistas:
            vistas.add(i["fonte"])
            saida.append({"nome": i["fonte"], "link": i["link"]})
    return saida


# ---------------------------------------------------------------- montagem do kit de UMA notícia
def montar_kit(g, nomes):
    item = escolher_item(g["itens"])
    cats = sorted(g["cats"] - {"geral"}) or ["geral"]
    cp = categoria_principal(g["cont"])
    fontes = fontes_unicas(g["itens"])
    n = len(fontes)
    em_ingles = item["idioma"] != "pt"

    titulo = item["titulo"]
    resumo = limpar_resumo(item["resumo"]) or titulo
    aviso = ("⚠️ Fonte em inglês: traduza e ajuste o texto antes de gravar." if em_ingles else "")
    resumo_pt = (f"[TRADUZIR] {resumo}" if em_ingles else resumo)
    curto = sem_aspas(encurtar(titulo, 80))
    cobertura = (f"{n} portais já noticiaram, como {fontes[0]['nome']} e {fontes[1]['nome']}."
                 if n >= 2 else f"A informação vem de {item['fonte']}. Vale conferir a matéria original.")
    p1 = sem_aspas(primeira_frase(resumo)) or curto
    p3 = POR_QUE_IMPORTA[cp]
    p3_sem_colchetes = re.sub(r"\s*\[.*?\]", "", p3)  # tira os [ADICIONE...] dos slides
    pergunta = PERGUNTAS[cp]
    gancho = GANCHOS[cp].format(t=curto)

    roteiro = "\n".join([
        f'- [0–3s] GANCHO: "{gancho}"',
        f'- [3–12s] PONTO 1: "{p1}"',
        f'- [12–24s] PONTO 2: "{cobertura}"',
        f'- [24–36s] PONTO 3: "{p3}"',
        f'- [36–42s] FECHAMENTO: "{pergunta}"',
        "- MEU COMENTÁRIO (opinião pessoal, ~5s, opcional): ______________________",
    ])
    material = MATERIAL[cp]
    busca = encurtar(titulo, 50)
    visuais = "\n".join([
        f'- [0–3s] {material} Busca sugerida no YouTube: "{busca} trailer oficial" (confirme que o canal é o oficial).',
        "- [3–12s] Screenshots/key art oficiais da página do jogo ou do press kit; ou gameplay próprio.",
        "- [12–24s] Texto na tela com o nome dos portais (sem usar imagens deles) sobre material oficial.",
        "- [24–36s] Trecho do trailer oficial ou gameplay próprio; logo oficial da empresa/plataforma.",
        "- [36–42s] Key art oficial desfocada com a pergunta em texto grande.",
        f"- ⚠️ {AVISO_IMAGENS}",
    ])
    carrossel = "\n".join([
        f"- CAPA: {encurtar(titulo, 60)}",
        f"- Slide 1: {limitar_palavras(p1, 20)}",
        f"- Slide 2: {limitar_palavras(cobertura, 20)}",
        f"- Slide 3: {limitar_palavras(p3_sem_colchetes, 20)}",
        f"- Slide 4: {limitar_palavras(pergunta, 20)}",
        f"- SLIDE FINAL: Fonte: {item['fonte']}. Quer mais notícias de games? Siga e ative o sininho!",
    ])
    linhas_anim = [encurtar(gancho, 60)] + pedacos(p1, 6, 3)
    if n >= 2:
        linhas_anim.append(f"{n} portais noticiaram")
    linhas_anim += [primeira_frase(pergunta), f"Fonte: {item['fonte']}", "Siga para mais notícias de games!"]
    texto_animado = "\n".join(f"{i}. {l}" for i, l in enumerate(linhas_anim, 1))
    tags = hashtags(cats)
    outras = ", ".join(f["nome"] for f in fontes if f["nome"] != item["fonte"])
    legenda = "\n".join([
        f"{gancho}",
        "",
        f"{limitar_palavras(p1, 25)}",
        "",
        f"{pergunta}",
        "",
        f"Fonte: {item['fonte']} ({item['link']})" + (f" | Também em: {outras}" if outras else ""),
        "",
        " ".join(tags),
    ])
    prompt = "\n".join([
        "Você é roteirista de vídeos curtos de games para Instagram/TikTok (canal sem rosto, narração em off em português do Brasil).",
        "Escreva com SUAS palavras; não copie trechos da matéria.",
        "",
        "NOTÍCIA",
        f"- Título: {titulo}",
        f"- Fonte: {item['fonte']} ({item['link']})",
        f"- Trecho do RSS: {resumo}",
        f"- Categorias: {', '.join(nomes.get(c, c) for c in cats)}",
        f"- Portais que cobriram: {', '.join(f['nome'] for f in fontes)}",
        "",
        "ENTREGUE",
        "1) Roteiro de narração de 30–45s com marcação de tempo: gancho de 1 frase (0–3s), 3 pontos curtos e fechamento com pergunta ao público. Frases curtas, escritas para serem faladas.",
        "2) Resumo de 1–2 linhas.",
        "3) Carrossel de Instagram: capa (manchete curta), 3 a 5 slides (máx. 20 palavras cada) e slide final com crédito à fonte e chamada para seguir.",
        "4) Texto animado (frases curtas, na ordem em que aparecem na tela).",
        "5) Legenda com crédito à fonte e 5 a 8 hashtags.",
        "",
        "REGRAS: não invente fatos além do título e do trecho; se faltar informação, escreva [CONFIRMAR]. Sugira imagens/vídeos apenas OFICIAIS (trailer, key art e screenshots do press kit ou do canal oficial da publicadora), nunca prints de matérias de outros portais.",
    ])
    return {
        "titulo": titulo, "fonte": item["fonte"], "link": item["link"], "idioma": item["idioma"],
        "categorias": [nomes.get(c, c) for c in cats], "n_fontes": n, "fontes": fontes,
        "resumo": resumo_pt, "aviso": aviso,
        "blocos": [
            {"id": "roteiro", "nome": "🎙️ Roteiro de narração (30–45s)", "texto": roteiro},
            {"id": "visuais", "nome": "🎞️ Imagens e vídeos por trecho (só material oficial)", "texto": visuais},
            {"id": "carrossel", "nome": "🖼️ Carrossel de Instagram", "texto": carrossel},
            {"id": "animado", "nome": "✨ Texto animado (sem voz)", "texto": texto_animado},
            {"id": "legenda", "nome": "📝 Legenda + hashtags", "texto": legenda},
            {"id": "prompt", "nome": "🤖 Prompt pronto para colar no Claude/ChatGPT (opcional)", "texto": prompt},
        ],
    }


# ---------------------------------------------------------------- Top 5 da semana
def montar_top5(grupos, nomes):
    """Ranking das 5 notícias mais cobertas da semana + roteiro/carrossel/texto animado únicos."""
    ranking = sorted(grupos, key=lambda g: (-len({i["fonte"] for i in g["itens"]}), -g["rel"]))[:5]
    pos = []  # lista na ordem do ranking (1 = mais coberta)
    for g in ranking:
        item = escolher_item(g["itens"])
        cats = sorted(g["cats"] - {"geral"}) or ["geral"]
        pos.append({"titulo": item["titulo"], "fonte": item["fonte"], "link": item["link"],
                    "idioma": item["idioma"], "fontes": fontes_unicas(g["itens"]),
                    "n_fontes": len(fontes_unicas(g["itens"])),
                    "categorias": [nomes.get(c, c) for c in cats], "cp": categoria_principal(g["cont"])})
    if not pos:
        return None
    tem_ingles = any(p["idioma"] != "pt" for p in pos)
    # Contagem regressiva: do 5º para o 1º.
    falas, anim, slides, visuais, t = [], [], [], [], 3
    for p in reversed(pos):
        rank = pos.index(p) + 1
        curto = sem_aspas(encurtar(p["titulo"], 70))
        falas.append(f'- [{t}–{t + 8}s] Nº {rank}: "{curto}". {p["n_fontes"]} portais falaram disso.')
        anim.append(f"Nº {rank}: {encurtar(p['titulo'], 50)}")
        slides.append(f"- Slide {6 - rank}: Nº {rank} — {limitar_palavras(p['titulo'], 14)} ({p['n_fontes']} portais)")
        visuais.append(f"- [{t}–{t + 8}s] Nº {rank}: {MATERIAL[p['cp']]}")
        t += 8
    roteiro = "\n".join([
        '- [0–3s] GANCHO: "As 5 notícias de games que dominaram a semana. Fica até o fim!"',
        *falas,
        f'- [{t}–{t + 6}s] FECHAMENTO: "Qual foi a notícia da semana para você? Comenta o número!"',
        "- MEU COMENTÁRIO (opinião pessoal, ~5s, opcional): ______________________",
    ])
    base = "\n".join(f"{i}. {p['titulo']} — {p['fonte']} ({p['n_fontes']} portais) {p['link']}"
                     for i, p in enumerate(pos, 1))
    fontes_txt = ", ".join(dict.fromkeys(p["fonte"] for p in pos))
    cats_all = sorted({c for g in ranking for c in g["cats"]} - {"geral"})
    legenda = "\n".join([
        "As 5 notícias de games mais comentadas da semana!", "",
        *[f"{i}. {encurtar(p['titulo'], 90)} ({p['fonte']})" for i, p in enumerate(pos, 1)], "",
        "Qual foi a sua favorita? Comenta o número!", "",
        f"Fontes: {fontes_txt}", "", " ".join(hashtags(cats_all)),
    ])
    prompt = "\n".join([
        "Você é roteirista de vídeos curtos de games (canal sem rosto, narração em off em português do Brasil).",
        "Crie o 'Top 5 da semana' com as notícias abaixo, usando SUAS palavras (sem copiar matérias).",
        "", "RANKING (1 = mais coberta)", base, "",
        "ENTREGUE: roteiro de narração 40–50s em contagem regressiva (5 ao 1) com marcação de tempo, gancho de 3s e pergunta final; carrossel de Instagram (capa + 5 slides de até 20 palavras + slide final com créditos); texto animado; legenda com créditos e 5 a 8 hashtags.",
        "REGRAS: não invente fatos; marque [CONFIRMAR] quando faltar informação; sugira só imagens oficiais (trailer, key art, press kit).",
    ])
    return {
        "titulo": "Top 5 da semana", "tem_ingles": tem_ingles, "itens": pos,
        "aviso": "⚠️ Há notícias em inglês: traduza e ajuste os títulos antes de gravar." if tem_ingles else "",
        "blocos": [
            {"id": "base", "nome": "📋 Ranking e fontes (dados base)", "texto": base},
            {"id": "roteiro", "nome": "🎙️ Roteiro de narração (contagem regressiva)", "texto": roteiro},
            {"id": "visuais", "nome": "🎞️ Imagens e vídeos por trecho (só material oficial)",
             "texto": "\n".join(visuais) + f"\n- ⚠️ {AVISO_IMAGENS}"},
            {"id": "carrossel", "nome": "🖼️ Carrossel de Instagram", "texto": "\n".join([
                "- CAPA: Top 5 notícias de games da semana", *slides,
                f"- SLIDE FINAL: Fontes: {encurtar(fontes_txt, 80)}. Siga para o próximo Top 5!"])},
            {"id": "animado", "nome": "✨ Texto animado (sem voz)", "texto": "\n".join(
                f"{i}. {l}" for i, l in enumerate(
                    ["Top 5 da semana nos games", *anim, "Qual foi a sua favorita?", f"Fontes: {encurtar(fontes_txt, 50)}",
                     "Siga para o próximo Top 5!"], 1))},
            {"id": "legenda", "nome": "📝 Legenda + hashtags", "texto": legenda},
            {"id": "prompt", "nome": "🤖 Prompt pronto para colar no Claude/ChatGPT (opcional)", "texto": prompt},
        ],
    }


# ---------------------------------------------------------------- saídas (Markdown)
def kit_para_markdown(kits, titulo_doc, data_txt):
    out = [f"# {titulo_doc} — {data_txt}", "",
           "> Rascunho gerado por modelos. **Revise e edite tudo antes de publicar.** Nada é publicado automaticamente.",
           f"> {AVISO_IMAGENS}", ""]
    for i, k in enumerate(kits, 1):
        out += [f"## {i}. {k['titulo']}", ""]
        if k.get("aviso"):
            out += [k["aviso"], ""]
        if "fonte" in k:  # kit diário: dados base
            out += [f"- **Fonte:** {k['fonte']} — [matéria original]({k['link']})",
                    f"- **Categorias:** {', '.join(k['categorias'])}",
                    f"- **Portais que cobriram ({k['n_fontes']}):** " +
                    ", ".join(f"[{f['nome']}]({f['link']})" for f in k["fontes"]),
                    f"- **Resumo:** {k['resumo']}", ""]
        for b in k["blocos"]:
            out += [f"### {b['nome']}", "", b["texto"], ""]
        out += ["---", ""]
    return "\n".join(out)


def top5_para_markdown(t, data_txt):
    out = [f"# Top 5 da semana — {data_txt}", "",
           "> Rascunho gerado por modelos. **Revise e edite tudo antes de publicar.**", f"> {AVISO_IMAGENS}", ""]
    if t["aviso"]:
        out += [t["aviso"], ""]
    for b in t["blocos"]:
        out += [f"## {b['nome']}", "", b["texto"], ""]
    return "\n".join(out)


# ---------------------------------------------------------------- principal
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--semanal", action="store_true", help="gera também o Top 5 da semana")
    ap.add_argument("--so-site", action="store_true", help="não grava em content/")
    ap.add_argument("--forcar", action="store_true", help="sobrescreve arquivos existentes em content/")
    args = ap.parse_args()

    agora = datetime.now(timezone.utc)
    hoje = agora.astimezone(BRT)
    data_arq = hoje.strftime("%Y-%m-%d")
    data_txt = hoje.strftime("%d/%m/%Y")
    domingo = hoje.weekday() == 6

    banco = abrir_banco()
    banco.row_factory = lambda cur, row: {d[0]: v for d, v in zip(cur.description, row)}
    nomes = {k: v["nome"] for k, v in
             yaml.safe_load(ARQUIVO_CATEGORIAS.read_text(encoding="utf-8"))["categorias"].items()}
    nomes["geral"] = "Geral"
    _, _, ignorar = carregar_categorias()

    def janela(horas):
        return (agora - timedelta(hours=horas)).isoformat(timespec="seconds")

    try:
        # Kit do dia: últimas 24h; se houver poucas notícias, amplia para 48h.
        grupos = carregar_grupos(banco, janela(24), ignorar)
        if len(grupos) < MIN_NOTICIAS:
            grupos = carregar_grupos(banco, janela(48), ignorar)
        grupos_semana = carregar_grupos(banco, janela(24 * 7), ignorar)
    except Exception as erro:
        raise SystemExit(f"Erro lendo o banco ({erro}). Rode antes: python src/atualizar.py")
    banco.close()

    escolhidos = sorted(grupos, key=lambda g: -g["rel"])[:MAX_NOTICIAS]
    kits = [montar_kit(g, nomes) for g in escolhidos]
    top5 = montar_top5(grupos_semana, nomes)
    if not kits:
        raise SystemExit("Sem notícias suficientes. Rode antes: python src/atualizar.py")
    if top5:
        top5["semana"] = hoje.strftime("%G-W%V")  # identifica a semana (para salvar suas edições)

    md_dia = kit_para_markdown(kits, "Kit de conteúdo do dia", data_txt)
    md_top5 = top5_para_markdown(top5, data_txt) if top5 else None

    # --- site: kit.html + downloads .md
    (PASTA_SITE / "kit").mkdir(parents=True, exist_ok=True)
    (PASTA_SITE / "kit" / "kit-do-dia.md").write_text(md_dia, encoding="utf-8")
    if md_top5:
        (PASTA_SITE / "kit" / "top5-semana.md").write_text(md_top5, encoding="utf-8")
    ambiente = Environment(loader=FileSystemLoader(PASTA_TEMPLATES),
                           autoescape=select_autoescape(["html", "j2"]))
    html = ambiente.get_template("kit.html.j2").render(
        kits=kits, top5=top5, data=data_txt, gerado=hoje.strftime("%d/%m/%Y %H:%M"), aviso_imagens=AVISO_IMAGENS)
    (PASTA_SITE / "kit.html").write_text(html, encoding="utf-8")
    print(f"Site: site/kit.html ({len(kits)} notícias no kit do dia"
          f"{', Top 5 da semana' if top5 else ''})")

    # --- content/: arquivos Markdown para você editar (nunca sobrescreve sem --forcar)
    if not args.so_site:
        PASTA_CONTENT.mkdir(exist_ok=True)
        alvos = [(PASTA_CONTENT / f"{data_arq}.md", md_dia)]
        if md_top5 and (domingo or args.semanal):
            alvos.append((PASTA_CONTENT / f"{data_arq}-top5-semana.md", md_top5))
        for caminho, texto in alvos:
            if caminho.exists() and not args.forcar:
                print(f"Já existe (não sobrescrevi, para proteger suas edições): {caminho.relative_to(RAIZ)}")
            else:
                caminho.write_text(texto, encoding="utf-8")
                print(f"Gravado: {caminho.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
