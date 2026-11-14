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
(Comandos das próximas fases serão adicionados aqui.)

## Fases
0 Setup · 1 Coleta · 2 Processamento · 3 Site · 4 Actions · 5 Kit de conteúdo · 6 Monetização (só planejar)

## Decisões
- Fase 1: Voxel = `rss.tecmundo.com.br/feed/voxel` (o feed geral do TecMundo mistura tecnologia, descartado). Fontes extras BR: Game Blast, Nintendo Blast, PSX Brasil.
- Fase 1: só RSS dos portais (feeds feitos para consumo por máquina); trecho limitado a 200 caracteres; links sem `utm_*`.
- `data/noticias.db` está no .gitignore por enquanto; decidir na Fase 4 como o banco persiste entre execuções do Actions.
- PyYAML adicionado para ler `sources.yaml` (feedparser/Jinja2/rapidfuzz não leem YAML).
