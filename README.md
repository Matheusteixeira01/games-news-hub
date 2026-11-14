# Games News Hub

Hub pessoal de notícias de games: coleta RSS de portais brasileiros e internacionais,
agrupa por assunto, classifica por categoria e publica um site estático.
Também gera um kit diário de conteúdo "sem rosto" (roteiros, carrosséis, legendas) para redes sociais.

**Custo zero:** Python + SQLite + GitHub Actions + GitHub Pages.

## Status das fases

- [x] Fase 0 – Setup inicial
- [x] Fase 1 – Coleta de feeds
- [x] Fase 2 – Processamento
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

## Regras de direitos autorais

Guardamos e exibimos apenas: título, link, fonte, data e trecho curto (máx. ~200 caracteres) vindo do RSS.
Nunca copiamos texto completo nem imagens de outros portais. Sempre creditamos e linkamos a fonte.

## Segurança

O repositório é público: nunca coloque senhas, tokens ou chaves no código.
