# Games News Hub

Hub pessoal de notícias de games: coleta RSS de portais brasileiros e internacionais,
agrupa por assunto, classifica por categoria e publica um site estático.
Também gera um kit diário de conteúdo "sem rosto" (roteiros, carrosséis, legendas) para redes sociais.

**Custo zero:** Python + SQLite + GitHub Actions + GitHub Pages.

## Status das fases

- [x] Fase 0 – Setup inicial
- [x] Fase 1 – Coleta de feeds
- [x] Fase 2 – Processamento
- [x] Fase 3 – Site (hub)
- [x] Fase 4 – Automação (GitHub Actions)
- [x] Fase 5 – Kit de conteúdo
- [ ] Fase 6 – Monetização (planejamento)

## Estrutura

| Pasta | Conteúdo |
|---|---|
| `config/` | Configurações editáveis (fontes, palavras-chave) |
| `src/` | Código Python |
| `data/` | Banco SQLite |
| `site/` | Site estático gerado |
| `content/` | Kits de conteúdo diários (Markdown) |

## Como preparar o ambiente (Windows / PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Como usar (Fase 1 – coleta)

```powershell
# 1. Testar quais feeds de config/sources.yaml estão respondendo
.\.venv\Scripts\python.exe src\check_feeds.py

# 2. Coletar as notícias e salvar em data/noticias.db (pode rodar quantas vezes quiser: não duplica)
.\.venv\Scripts\python.exe src\coletar.py
```

- **Fontes:** edite `config/sources.yaml`. Use `ativo: false` para desligar um portal.
- **Banco:** `data/noticias.db` (SQLite). Tabela `noticias`: fonte, idioma, titulo, link (único), resumo (máx. 200 caracteres), publicado_em, coletado_em.
- **Feeds testados em 14/11/2026:** 20 funcionando (8 BR, 12 internacionais). Sem feed funcional: The Enemy, Jovem Nerd, Game Arena.

## Como usar (Fase 2 – processamento)

```powershell
# Agrupa, classifica e dá nota às notícias dos últimos 3 dias (use --dias 7 para outra janela)
.\.venv\Scripts\python.exe src\processar.py
```

- **Agrupamento:** títulos parecidos (rapidfuzz) viram um "assunto". Funciona até entre português e inglês quando os nomes próprios coincidem (ex.: "Wolfenstein 3", "Halo: Campaign Evolved").
- **Categorias:** `config/categories.yaml` (palavras-chave editáveis). Lançamentos, Indústria, Rumores, Esports, Mobile, Indie, PC, PlayStation, Xbox, Nintendo; sem palavra casando = `geral`. Portais especializados (ex.: Push Square = PlayStation) ganham a categoria automaticamente.
- **Relevância:** `10 pontos × nº de portais diferentes` + bônus de até 5 pela recência.
- **Colunas novas em `noticias`:** `grupo_id`, `n_fontes`, `categorias`, `relevancia`.
- **Ajustes finos:** constantes no topo de `src/processar.py` (limiar de similaridade, pontos) e lista `ignorar_agrupamento` em `categories.yaml` (colunas recorrentes como "Talking Point").
- **Limitações:** alguns portais (IGN) trazem cinema/tecnologia, que caem em `geral`; um filtro "só games" pode vir depois.

## Como usar (Fase 3 – site)

```powershell
# Só gera o site a partir do banco atual
.\.venv\Scripts\python.exe src\gerar_site.py

# Ou roda tudo de uma vez: coletar -> processar -> gerar site
.\.venv\Scripts\python.exe src\atualizar.py
```

Depois, abra `site/index.html` no navegador (duplo clique; não precisa de servidor).

- **Recursos:** "Mais cobertos" (assuntos com 2+ portais), lista por data, busca, filtros de período (Hoje / 3 dias), idioma, plataforma e tema. Cada card mostra título, trecho curto, fonte e link; "Também em:" lista os outros portais que cobriram o assunto.
- **Arquivos:** `src/gerar_site.py` (lê o banco), `src/templates/index.html.j2` (HTML + CSS + JS num arquivo só, com Jinja2). Os filtros rodam no navegador.
- **Aparência:** responsivo (testado em 375 px) e com tema claro/escuro automático.
- **Segurança:** o JS monta os cards com `textContent` (sem injetar HTML do feed) e só aceita links `http(s)`.
- `site/index.html` é gerado e fica no `.gitignore` (a Fase 4 o publica via Actions).

## Automação (Fase 4 – GitHub Actions + Pages)

**Site no ar:** https://matheusteixeira01.github.io/games-news-hub/ (atualiza sozinho de hora em hora, no minuto 7).

Como funciona (`.github/workflows/atualizar.yml`):
1. O GitHub liga uma máquina Linux, baixa o código e o banco (guardado na branch `dados`).
2. Roda `python src/atualizar.py` (coletar, processar e gerar o site).
3. Salva o banco atualizado na branch `dados` (sobrescrita a cada rodada, sem poluir o `main`).
4. Publica a pasta `site/` no GitHub Pages.

Dia a dia, pelo site do GitHub (aba **Actions**):
- **Ver execuções:** Actions, depois "Atualizar hub". Verde = ok, vermelho = erro (clique e abra o passo com ❌ para ver o log).
- **Rodar na hora:** Actions, "Atualizar hub", **Run workflow**. Ou pelo terminal: `gh workflow run "Atualizar hub"`.
- **Mudar fontes ou categorias:** edite `config/sources.yaml` ou `config/categories.yaml`, faça commit e push. O workflow roda sozinho e republica.
- **Se o Pages sumir:** Settings, Pages, e confira se "Source" está em **GitHub Actions**.
- **Agendamento pausado:** o GitHub pausa agendamentos de repositórios públicos sem atividade por 60 dias. Se acontecer, ative de novo em Actions.
- O banco guarda só **30 dias** de notícias (`DIAS_GUARDAR` em `src/coletar.py`).

## Kit de conteúdo sem rosto (Fase 5)

**Na web:** https://matheusteixeira01.github.io/games-news-hub/kit.html (link "🎬 Kit de conteúdo" no topo do hub). Atualiza de hora em hora.

**No seu computador (arquivos para editar):**

```powershell
.\.venv\Scripts\python.exe src\atualizar.py   # atualiza notícias e site (inclui kit.html)
.\.venv\Scripts\python.exe src\kit.py         # grava content/AAAA-MM-DD.md (e o Top 5 aos domingos)
.\.venv\Scripts\python.exe src\kit.py --semanal   # força o Top 5 da semana em qualquer dia
```

`kit.py` **nunca sobrescreve** um arquivo que já existe em `content/` (para proteger suas edições). Use `--forcar` só se quiser regerar.

**O que cada notícia do kit traz** (5 a 8 por dia, escolhidas pela relevância):
1. Dados base: título, fonte, link original, categorias, portais que cobriram e resumo.
2. Roteiro de narração 30–45 s, com tempos: gancho (0–3 s), 3 pontos, fechamento com pergunta e campo "meu comentário".
3. Sugestão de imagens/vídeos por trecho (só material oficial: trailer, key art, press kit, canal oficial da publicadora).
4. Carrossel de Instagram: capa, slides de até 20 palavras e slide final com crédito.
5. Texto animado (frases curtas para legenda sobre música).
6. Legenda pronta com crédito à fonte e 5 a 8 hashtags.
7. Prompt pronto para colar no Claude/ChatGPT e refinar o roteiro (opcional).

**Top 5 da semana:** ranking das 5 notícias mais cobertas dos últimos 7 dias, com roteiro em contagem regressiva, carrossel, texto animado e legenda.

**Como funciona o texto:** modelos fixos (sem IA paga) no topo de `src/kit.py` (`GANCHOS`, `POR_QUE_IMPORTA`, `PERGUNTAS`, `MATERIAL`, `HASHTAGS`). Edite-os para ajustar o tom. Os trechos `[ADICIONE: ...]` e `[TRADUZIR]` são para você completar. Notícias só em inglês vêm marcadas com um aviso.

**Na página do kit** cada bloco é um campo editável com botões **Copiar** e **Restaurar**; suas edições ficam salvas no navegador (por notícia). Nada é publicado automaticamente.

## Regras de direitos autorais

Guardamos e exibimos apenas: título, link, fonte, data e trecho curto (máx. ~200 caracteres) vindo do RSS.
Nunca copiamos texto completo nem imagens de outros portais. Sempre creditamos e linkamos a fonte.

## Segurança

O repositório é público: nunca coloque senhas, tokens ou chaves no código.
