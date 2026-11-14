# Games News Hub

Hub pessoal de notícias de games: coleta RSS de portais brasileiros e internacionais,
agrupa por assunto, classifica por categoria e publica um site estático.
Também gera um kit diário de conteúdo "sem rosto" (roteiros, carrosséis, legendas) para redes sociais.

**Custo zero:** Python + SQLite + GitHub Actions + GitHub Pages.

## Status das fases

- [x] Fase 0 – Setup inicial
- [x] Fase 1 – Coleta de feeds
- [ ] Fase 2 – Processamento
- [ ] Fase 3 – Site (hub)
- [ ] Fase 4 – Automação (GitHub Actions)
- [ ] Fase 5 – Kit de conteúdo
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

## Regras de direitos autorais

Guardamos e exibimos apenas: título, link, fonte, data e trecho curto (máx. ~200 caracteres) vindo do RSS.
Nunca copiamos texto completo nem imagens de outros portais. Sempre creditamos e linkamos a fonte.

## Segurança

O repositório é público: nunca coloque senhas, tokens ou chaves no código.
