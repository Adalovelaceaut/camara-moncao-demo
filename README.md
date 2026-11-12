# Demo "Câmara de Monção" — Atende Leads

Configuração, roteiro e scripts da demonstração de atendimento automatizado para uma câmara municipal, feita sobre o [Atende Leads](https://github.com/inematds/atende-leads) (código aberto, licença MIT, comunidade INEMA). Fork de referência: [Adalovelaceaut/atende-leads](https://github.com/Adalovelaceaut/atende-leads).

A demo roda 100% local (ou em qualquer máquina), sem WhatsApp, sem Telegram, sem custo: o canal é o chat do próprio site (widget web). Todos os atendentes, cidadãos e textos são fictícios.

## Conteúdo

- `config/negocio.exemplo.json` — configuração "Câmara de Monção": horários, equipe fictícia (Ana/Caio), menu de assuntos e base de conhecimento (falta d'água, ponte, ouvidoria, vereador, horário). **Tokens e códigos são placeholders (`TROQUE-ME`) — gere os seus.**
- `docs/roteiro-demo-camara-moncao.pdf` — roteiro de 5 minutos da apresentação (falas e respostas esperadas).
- `scripts/demo2.py` — grava a demo de ponta a ponta (dirige o chat, a equipe e o gestor via API + Chrome/CDP + ffmpeg).
- `scripts/cdp.js` — driver mínimo do Chrome DevTools Protocol usado pelo demo2.py.
- `scripts/watchdog.sh` — mantém um túnel temporário (cloudflared) apontado para o servidor local.

## Como rodar a demo localmente

1. Baixe o Atende Leads (fork acima ou o upstream) — o binário `atende` acompanha o repositório.
2. Copie `config/negocio.exemplo.json` para `dados/negocio.json` e troque `token_gestor` e os `codigo` da equipe por valores aleatórios (ex.: `openssl rand -hex 16`).
3. Suba o servidor: `./atende serve --porta 8097 --dados dados`
4. Acesse:
   - Chat do cidadão: `http://localhost:8097/`
   - Painel da equipe: `http://localhost:8097/equipe` (código do atendente)
   - Painel do gestor: `http://localhost:8097/gestor` (token do gestor)

## Avisos

- Nenhum dado real de cidadão foi usado ou deve ser usado nesta configuração.
- WhatsApp real exige Evolution API e número dedicado (risco de banimento em número pessoal) — fora do escopo desta demo.
- Atende Leads é um projeto de terceiros (INEMA); este repositório contém apenas configuração e scripts da demonstração.

Licença deste repositório: MIT.

## Identidade visual de Monção (12/11)

A configuração usa a identidade do site oficial da Câmara (cmmoncao.ma.gov.br): tema `marinho` com destaque dourado `#f0a500` e nome exibido "Câmara de Monção — demonstração". A base de conhecimento inclui dados públicos reais: endereço (Praça Presidente Kennedy, Centro), horário (seg-sex 8h-12h, 13h30-17h), mesa diretora, bairros/povoados e contatos oficiais. Sem brasão ou logotipo — só cores, nome e informações públicas, sempre marcado como demonstração.

## Cérebro LLM (opcional)

A demo pode responder com um agente Hermes local em vez de só regras: `cerebro: {"tipo": "openai", "url": "http://127.0.0.1:8644", "modelo": "hermes-agent"}` + variáveis `CEREBRO_API_KEY` e `CEREBRO_HOSTS_PERMITIDOS=127.0.0.1`. O agente roda isolado (HERMES_HOME próprio, api_server só em localhost, sem ferramentas) com persona em `SOUL.md`. Na instalação de referência ele usa uma conta ChatGPT pessoal já existente — válido só para demonstração, não para produção.

## Página inicial do cidadão (12/11)

`web/index.html` substitui a página inicial do Atende Leads por uma landing da Câmara de Monção: hero com chamada, ações (falar com a Câmara, agendar com vereador, ouvidoria), "como funciona", serviços, mesa diretora e contatos públicos. O chat original fica embutido e abre a partir dos botões (sem mudar rotas nem o servidor). Para usar: copie por cima de `web/index.html` na instalação do Atende Leads (o arquivo original fica salvo como `index.original-chat.html.bak`).

## Módulo Gabinete (proposta + protótipo, 12/11)

- `docs/nota-gabinete-camara-moncao.pdf` — nota estratégica (2 páginas): papel da Câmara (legislar, fiscalizar, representar, indicações), o que a demo já cobre e a proposta do Módulo Gabinete (fila por vereador, rascunho de indicação, prazos, prestação de contas pública, agenda).
- `scripts/gera_prestacao.py` — gera `web/prestacao.html` (painel público de prestação de contas: atendidos, demandas por assunto, acompanhamento) a partir do `leads.db`. Protótipo em staging: rota `/prestacao` adicionada em `ESTATICOS` no `src/server.py` (só na instância de teste).
- `scripts/gera_gabinete.py` — gera `web/gabinete.html` (página do gabinete: LEGISLAR + FISCALIZAR). Legislar: demandas do chat agrupadas por assunto/bairro, rascunhos de indicação/requerimento/projeto de lei gerados pelo agente Hermes (sempre "para revisão", sem parecer jurídico) e tramitação simulada. Fiscalizar: protocolos com a Prefeitura com prazo e alerta de vencimento, histórico por assunto e lembretes de pauta/sessões. Abas por gabinete (Gabinete-piloto Ana / Caio) + visão geral. Tema Monção, mobile-first, dados fictícios marcados. Rota `/gabinete` em `ESTATICOS` no `src/server.py`; em produção na demo pública.
