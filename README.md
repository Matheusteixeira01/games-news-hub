# Games News Hub

Hub pessoal de notícias de games: coleta RSS de portais brasileiros e internacionais,
agrupa por assunto, classifica por categoria e publica um site estático.
Também gera um kit diário de conteúdo "sem rosto" (roteiros, carrosséis, legendas) para redes sociais.

**Custo zero:** Python + SQLite + GitHub Actions + GitHub Pages.

## Status das fases

- [x] Fase 0 – Setup inicial
- [ ] Fase 1 – Coleta de feeds
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

## Regras de direitos autorais

Guardamos e exibimos apenas: título, link, fonte, data e trecho curto (máx. ~200 caracteres) vindo do RSS.
Nunca copiamos texto completo nem imagens de outros portais. Sempre creditamos e linkamos a fonte.

## Segurança

O repositório é público: nunca coloque senhas, tokens ou chaves no código.
