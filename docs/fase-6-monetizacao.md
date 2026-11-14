# Fase 6 — Plano de monetização e ferramentas extras (só planejamento)

> Nada aqui foi implementado. É um mapa para decidir o que fazer depois, em etapas de ~1 h por dia.
> Pesquisa feita em 14/11/2026. **As fontes abaixo são blogs e agregadores de terceiros, não as páginas oficiais.** Antes de investir tempo ou dinheiro, confirme cada regra no site oficial do programa.

## 1. Diagnóstico honesto

- **A meta de R$ 1.000/mês é possível, mas não vem do hub sozinho.** Hoje o site mostra título + trecho + link de outros portais. Isso é ótimo para você se informar, mas tem pouco valor próprio para anunciantes e para o Google.
- **AdSense é o maior risco.** Os materiais que encontrei são consistentes: sites montados a partir de feeds RSS/conteúdo agregado costumam ser reprovados por "conteúdo de baixo valor", mesmo creditando a fonte ([guia sobre rejeição](https://toolpod.dev/blog/adsense-rejection-low-value-content), [discussão no fórum do AdSense](https://support.google.com/adsense/community-guide/241032356/how-can-you-solve-the-low-value-content-adsense-disapproval-challenge?hl=en)). O que o Google valoriza é conteúdo **original**. Por isso o plano abaixo põe o seu conteúdo próprio (vídeos sem rosto, resumos semanais com opinião, calendário, promoções) no centro, e o feed agregado em segundo plano.
- **Ordem recomendada:** audiência nas redes → afiliados → newsletter → só depois AdSense. A receita mais rápida e realista no começo é **afiliados**.
- **Ordem de grandeza (estimativa minha, não verificada):** com comissão média de ~R$ 10 por venda, R$ 1.000/mês pedem ~100 vendas. Se só 0,05%–0,1% dos visitantes comprarem, isso é algo como 100 a 200 mil visitas/mês. Redes sociais com links na bio e newsletter costumam converter melhor que tráfego frio, e por isso entram antes. Espere **vários meses de constância (6 a 18)** até chegar lá.

## 2. Canais de receita (do mais ao menos prioritário)

### A. Afiliados (dá para começar mesmo com audiência pequena)
| Programa | O que saber | Verificar no site oficial |
|---|---|---|
| **Amazon Associados (BR)** | Terceiros dizem que é preciso **3 vendas qualificadas em 180 dias** ou a conta é desativada; comissão de games varia nas fontes (de ~3% a ~8%); cookie de 24 h; pagamento ~60 dias após o mês. Compras suas pelos próprios links não contam ([exemplo](https://www.divulganinja.com.br/blog/como-se-afiliar-na-amazon-passo-a-passo-2026)) | Taxas atuais; se links em **e-mail/newsletter** são permitidos (a Amazon costuma restringir) |
| **Lojas de jogos/keys e marketplaces** (ex.: Nuuvem, Shopee, Mercado Livre) | Têm programas de afiliados; comissões e regras variam | Se o programa existe hoje, taxas e se aceitam sites com link para promoções |
| **Hardware gamer** (cadeiras, periféricos, SSD) | Bom ticket médio: um item de R$ 300 a 5% rende R$ 15 | Disponibilidade nas lojas acima |

**Regras que valem para todos:** avise que há link de afiliado (ex.: "Links com comissão para o site, sem custo extra para você"), e confira as diretrizes de publicidade do CONAR para influenciadores. Nunca faça pedido por link próprio para "bater meta".

### B. Newsletter semanal
- **Formato:** o "Top 5 da semana" que você já recebe do kit, com 2 ou 3 linhas de opinião sua + 1 oferta/promoção da semana.
- **Ferramentas com plano gratuito** (verificar limites atuais): Buttondown, Substack, Beehiiv, MailerLite.
- **LGPD:** cadastro com consentimento claro, link de descadastro em todo e-mail e política de privacidade.
- **Monetização:** afiliados (conferir regra da Amazon para e-mail) e, com audiência, patrocínio de estúdios indie.
- **Quando começar:** quando houver gente pedindo (pergunte nos vídeos e no site). Um formulário no hub custa pouco.

### C. AdSense (só depois de ter conteúdo original)
Pré-requisitos práticos:
1. **Domínio próprio** (ex.: `.com.br` pelo Registro.br, a partir de ~R$ 40/ano; confirmar preço). Será o primeiro custo do projeto. Subdomínios gratuitos como `github.io` em geral não são aceitos no AdSense (confirmar).
2. Páginas **Sobre**, **Contato**, **Política de Privacidade** e **Termos**.
3. Dezenas de páginas **originais** (artigos, guias, resumos semanais com opinião), não só links de terceiros.
4. Aviso de cookies/consentimento (LGPD) quando entrarem anúncios e métricas.
GitHub Pages e Cloudflare Pages aceitam domínio próprio de graça.

### D. Redes sociais
- **YouTube:** pelos materiais encontrados, o Programa de Parcerias exige 1.000 inscritos + 4.000 h de exibição em 12 meses, ou 10 milhões de views de Shorts em 90 dias. **A partir de 01/02/2027 a regra de entrada passa para 8.000 h ou 20 milhões de views de Shorts** (fonte: [AIR Media-Tech](https://air.io/pt/monetization/youtube-partner-program-requirements-2026-the-complete-guide), [Canaltech](https://canaltech.com.br/internet-e-redes-sociais/youtube-muda-regras-e-dificulta-monetizacao-de-novos-canais-veja-exigencias)). Ou seja: monetizar direto pelo YouTube é difícil; use o canal principalmente para **tráfego e afiliados**.
- **TikTok/Instagram:** programas de pagamento por visualização no Brasil não foram verificados. Trate como **vitrine**: link na bio para o hub, a página de promoções e a newsletter.
- **Comunidades gratuitas de alto retorno:** canal do Telegram, canal do WhatsApp e servidor do Discord com as "notícias do dia" e as promoções. O Actions pode postar sozinho (exigiria um token do bot guardado em *Secrets* do GitHub, nunca no código).

### E. Outras fontes
- **Doações/apoio** (Pix, Apoia.se, Catarse): funcionam se a audiência for fiel.
- **Publis e parcerias com estúdios indie:** cobrar por post/vídeo quando houver alcance. Comece com tabela simples de preços.
- **Cuidado fiscal:** AdSense e afiliados pagam a pessoa física/CNPJ. Informe-se sobre MEI/carnê-leão com um contador antes de a renda ficar recorrente.

## 3. Ferramentas extras para o site

| Ferramenta | Como fazer (grátis) | Esforço | Valor |
|---|---|---|---|
| **Calendário de lançamentos** | Começar com um arquivo `config/lancamentos.yaml` mantido **à mão** (10–20 grandes jogos) e uma página gerada pelo Actions, com botão "adicionar ao calendário" (.ics). Depois, automatizar com **IGDB** ou **RAWG** (APIs gratuitas; exigem chave guardada em *Secrets* e têm regras de uso/atribuição, **não verificadas aqui**) | Baixo (manual) / Médio (API) | Alto: gera visitas recorrentes e SEO |
| **Promoções de jogos** | API **CheapShark** (sem chave e gratuita segundo agregadores; **confirmar os termos**) para ofertas de Steam/GOG/Epic. Página "Promoções do dia" gerada a cada hora, com links de afiliado onde houver programa | Médio | Alto: é onde o afiliado converte |
| **Páginas por assunto/jogo** | Uma página estática por assunto mais coberto, com os links dos portais e o seu comentário | Médio | Alto para SEO e para AdSense (conteúdo original) |
| **Arquivo semanal** | Publicar cada "Top 5 da semana" como página própria (hoje o kit sobrescreve) | Baixo | Médio/alto: cresce o acervo original |
| **RSS próprio** | `feed.xml` com os destaques para outros leitores assinarem | Baixo | Médio |
| **Bot Telegram/Discord** | Posta o "Mais cobertos" automaticamente | Médio | Médio: tráfego grátis |
| **Estatísticas de visita** | Ferramenta privada e sem cookies (ex.: Cloudflare Web Analytics ou GoatCounter; confirmar planos) | Baixo | Necessário para medir tudo acima |

## 4. Roteiro sugerido (1 h por dia)

| Quando | Foco | Entregável | Medida de sucesso |
|---|---|---|---|
| **Semanas 1–2** | Rotina de conteúdo | Perfis criados; 3 a 5 posts/semana usando o kit; link do hub na bio | Rotina mantida 2 semanas |
| **Semanas 3–4** | Base profissional | Domínio próprio; páginas Sobre/Contato/Privacidade; conta de afiliados; contador de visitas | Site no domínio próprio; 1ª visita medida |
| **Mês 2** | Ferramentas que convertem | Calendário de lançamentos (manual) + "Promoções do dia" | Cliques em links de afiliado |
| **Mês 3** | Audiência própria | Formulário de newsletter; canal Telegram/WhatsApp | 50–100 inscritos |
| **Meses 4–6** | Conteúdo original no site | Arquivo semanal; páginas por assunto; 20+ páginas originais | Visitas orgânicas crescendo |
| **Mês 6+** | Avaliar AdSense | Candidatar-se só com conteúdo original e domínio próprio | Aprovação / receita inicial |

A cada marco: veja o que deu retorno e corte o que não deu. Nada de gastar com anúncios antes de ter um funil que pague.

## 5. Riscos e cuidados

1. **Termos dos portais de origem.** Hoje o uso é pessoal. Ao monetizar, revise os termos de cada fonte e, se houver dúvida, peça autorização ou remova a fonte. Mantenha o limite de 200 caracteres e a regra de nunca usar imagens de terceiros. **Monetize o seu conteúdo (vídeos, resumos, calendário, promoções), não a cópia de manchetes.**
2. **Direitos de imagem/vídeo nos conteúdos para redes:** só material oficial (trailers, key art, press kit), como o kit já orienta.
3. **Dependência de plataformas** (algoritmo, regras de monetização mudam): por isso newsletter e site próprio.
4. **LGPD:** política de privacidade, consentimento para e-mail, aviso de cookies quando houver anúncios/métricas.
5. **Segredos:** chaves de API/bots só em *Settings → Secrets* do GitHub, nunca no código nem no repositório público.

## 6. Decisões que dependem de você (quando for a hora)

- Orçamento para o **domínio** (~R$ 40/ano)? É o primeiro gasto do projeto.
- Vai receber como **pessoa física ou MEI**?
- Qual rede é a **prioridade** (Instagram, TikTok ou YouTube)?
- Prefere **newsletter** (e-mail) ou **comunidade** (Telegram/WhatsApp/Discord) primeiro?
- Autoriza, no futuro, usar **chaves de API gratuitas** (guardadas em *Secrets*) para calendário e promoções?

## Fontes consultadas (terceiros; confirme nos sites oficiais)
- [AdSense e "conteúdo de baixo valor" (toolpod.dev)](https://toolpod.dev/blog/adsense-rejection-low-value-content)
- [Comunidade AdSense: solucionar "conteúdo de baixo valor"](https://support.google.com/adsense/community-guide/241032356/how-can-you-solve-the-low-value-content-adsense-disapproval-challenge?hl=en)
- [Como se afiliar à Amazon em 2026 (Divulga Ninja)](https://www.divulganinja.com.br/blog/como-se-afiliar-na-amazon-passo-a-passo-2026)
- [Afiliado Amazon: como ser afiliado em 2026 (Plusdin)](https://plusdin.com.br/como-ser-afiliado-da-amazon/)
- [Requisitos para monetizar no YouTube 2026 (AIR Media-Tech)](https://air.io/pt/monetization/youtube-partner-program-requirements-2026-the-complete-guide)
- [YouTube muda regras para novos canais (Canaltech)](https://canaltech.com.br/internet-e-redes-sociais/youtube-muda-regras-e-dificulta-monetizacao-de-novos-canais-veja-exigencias)
- [CheapShark API (diretório)](https://www.freepublicapis.com/cheapshark-api)
