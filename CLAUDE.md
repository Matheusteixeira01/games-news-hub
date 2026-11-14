# CLAUDE.md – Games News Hub

## Sobre o projeto
Hub pessoal de notícias de games (RSS -> SQLite -> site estático) + kit de conteúdo "sem rosto"
para Instagram/TikTok. Custo zero: GitHub Actions + GitHub Pages. Futuro: site público e monetização.

## Usuário
Iniciante em Python, ~1h/dia. Código simples, bem comentado, fácil de manter. Responder em português.

## Regras
- Trabalhar em etapas pequenas; cada fase termina com algo rodável, e um commit claro.
- Só avançar de fase depois que o usuário confirmar que testou.
- Perguntar em vez de assumir quando a decisão for do usuário.
- Confirmar com o usuário ANTES de qualquer ação que crie/altere algo na conta do GitHub.
- Repositório público: nunca colocar senhas, tokens ou chaves no código.
- Direitos autorais: guardar/exibir só título, link, fonte, data e trecho curto (máx. ~200 caracteres) do RSS.
  Nunca copiar texto completo nem reutilizar imagens de outros portais. Sempre creditar e linkar a fonte.
  Respeitar robots.txt e termos de uso.
- Nada é publicado automaticamente em redes sociais: o usuário revisa e edita tudo.

## Stack
Python, feedparser, PyYAML, SQLite (sqlite3 nativo), Jinja2, rapidfuzz. Site em HTML + JS simples.

## Estrutura
`config/` (sources.yaml etc.), `src/` (código), `data/` (SQLite), `site/` (site gerado), `content/` (kits diários).

## Como rodar
```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
- `python src/check_feeds.py` – testa os feeds de `config/sources.yaml`
- `python src/coletar.py` – coleta e grava em `data/noticias.db` (idempotente: `link` é UNIQUE)
- `python src/processar.py [--dias N]` – agrupa, classifica e pontua (grava `grupo_id`, `n_fontes`, `categorias`, `relevancia`)
- `python src/gerar_site.py [--dias N]` – gera `site/index.html` (Jinja2 + JS no navegador)
- `python src/atualizar.py` – pipeline completo: coletar -> processar -> gerar site
- `python src/kit.py [--semanal] [--so-site] [--forcar]` – kit de conteúdo: `site/kit.html` + `content/AAAA-MM-DD.md` (nunca sobrescreve sem `--forcar`)
(Comandos das próximas fases serão adicionados aqui.)

## Fases
0 Setup · 1 Coleta · 2 Processamento · 3 Site · 4 Actions · 5 Kit de conteúdo · 6 Monetização (só planejar)

## Decisões
- Fase 1: Voxel = `rss.tecmundo.com.br/feed/voxel` (o feed geral do TecMundo mistura tecnologia, descartado). Fontes extras BR: Game Blast, Nintendo Blast, PSX Brasil.
- Fase 1: só RSS dos portais (feeds feitos para consumo por máquina); trecho limitado a 200 caracteres; links sem `utm_*`.
- `data/noticias.db` está no .gitignore por enquanto; decidir na Fase 4 como o banco persiste entre execuções do Actions.
- Fase 2: agrupamento com `rapidfuzz.process.extract` (token_sort_ratio >= 78; token_set_ratio só vale com >= 3 palavras em comum). Evitei `cdist` porque exige numpy (dependência pesada).
- Fase 2: relevância = 10 × fontes distintas no grupo + bônus de recência (0–5). Títulos de colunas recorrentes (`ignorar_agrupamento`) nunca agrupam.
- Fase 2: processar só a janela recente (3 dias); notícias antigas mantêm os valores antigos.
- Fase 3: site 100% estático num único `index.html` com dados embutidos (`|tojson`); funciona abrindo o arquivo direto. Cards montados via DOM/`textContent` (feeds são dados não confiáveis). Sem imagens de terceiros.
- Fase 3: `site/index.html` no .gitignore (gerado). Para SEO/público no futuro, considerar páginas por assunto renderizadas no servidor (Jinja2).
- Fase 4: workflow `.github/workflows/atualizar.yml` (cron `7 * * * *`, manual e push em src/config). Banco persistido na branch órfã `dados` (force-push a cada rodada) para não poluir o histórico do `main`. Deploy via `actions/deploy-pages` (Pages com build_type=workflow). Site: https://matheusteixeira01.github.io/games-news-hub/
- Fase 4: banco limita-se a 30 dias (`DIAS_GUARDAR`). Primeira execução real: os 20 feeds responderam a partir dos servidores do GitHub.
- Qualquer push ao GitHub ou mudança na conta exige confirmação do usuário antes.
- Fase 5 (decisão do usuário): textos do kit por MODELOS FIXOS + prompt pronto para colar numa IA. Sem API paga e sem chaves. Notícias só em inglês recebem aviso `[TRADUZIR]` (não há tradução automática gratuita confiável).
- Fase 5: categoria principal do assunto = a mais frequente entre as notícias do grupo; 'rumores' só vale com 2+ notícias. Kit do dia usa as últimas 24h (48h se faltar notícia); Top 5 usa 7 dias, por isso `atualizar.py` roda `processar.py --dias 7`.
- Fase 5: `site/kit.html` tem `noindex`; edições do usuário ficam no localStorage (por link da notícia). `content/*.md` no .gitignore (rascunhos pessoais). Horário de referência: Brasília (UTC-3 fixo).
- Fase 5: sem imagens de terceiros; as sugestões de imagem são sempre material oficial.
- PyYAML adicionado para ler `sources.yaml` (feedparser/Jinja2/rapidfuzz não leem YAML).
