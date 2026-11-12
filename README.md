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
