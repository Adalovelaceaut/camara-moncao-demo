#!/usr/bin/env python3
# Gera web/prestacao.html (painel publico de prestacao de contas) a partir do leads.db da demo.
import sqlite3, html, datetime, sys

DB = sys.argv[1] if len(sys.argv) > 1 else "/home/ada/camara-demo-hermes-dados/leads.db"
OUT = sys.argv[2] if len(sys.argv) > 2 else "/home/ada/camara-demo-hermes-app/web/prestacao.html"

db = sqlite3.connect("file:%s?mode=ro" % DB, uri=True)
leads = db.execute("SELECT count(*) FROM leads").fetchone()[0]
por_motivo = db.execute("SELECT COALESCE(NULLIF(motivo,''),'outros assuntos'), count(*) FROM chamados GROUP BY 1 ORDER BY 2 DESC").fetchall()
por_status = dict(db.execute("SELECT COALESCE(status,'?'), count(*) FROM chamados GROUP BY 1").fetchall())
msgs = db.execute("SELECT count(*) FROM mensagens").fetchone()[0]
NOMES = {"ana": "Gabinete Ver. Daerlio (atend. Ana)", "caio": "Gabinete Ver.ª Lindolene (atend. Caio)"}
por_gab = db.execute("SELECT COALESCE(NULLIF(dono,''),'(na fila, sem gabinete)'), count(*) FROM chamados GROUP BY 1 ORDER BY 2 DESC").fetchall()
total_ch = sum(por_status.values())
abertos = sum(v for k, v in por_status.items() if k not in ("fechado", "concluido", "resolvido"))
agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")

ROTULOS = {"pediu_humano": "falar com um atendente", "venda": "informações e serviços", "precisa": "resolver um problema", "retomada": "retomar a conversa", "gestor": "falar com a equipe"}
gab_rows = "".join(
    f"<tr><td>{html.escape(NOMES.get(g, g))}</td><td class='n'>{n}</td></tr>"
    for g, n in por_gab) or "<tr><td colspan='2'>Sem demandas atribuidas ainda.</td></tr>"
linhas = "".join(
    f"<tr><td>{html.escape(ROTULOS.get(m, m))}</td><td class='n'>{n}</td><td class='n'>{round(100*n/max(total_ch,1))}%</td></tr>"
    for m, n in por_motivo) or "<tr><td colspan='3'>Sem chamados ainda.</td></tr>"

pagina = f"""<!doctype html>
<html lang="pt-BR" data-tema="marinho"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Miro Câmara — Prestação de contas por gabinete (demonstração)</title>
<link rel="stylesheet" href="/web/style.css">
<style>
body{{margin:0;font-family:var(--corpo);background:var(--bg);color:var(--tinta)}}
.pag{{max-width:860px;margin:0 auto;padding:18px}}
.barra{{display:flex;align-items:center;gap:10px;margin-bottom:14px}}
.mono{{width:40px;height:40px;border-radius:50%;background:#f0a500;color:#1a1206;display:flex;align-items:center;justify-content:center;font-weight:700;font-family:var(--titulo)}}
h1{{font-family:var(--titulo);font-size:22px;margin:0}}
.sub{{color:var(--mut);font-size:13px}}
.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin:18px 0}}
.card{{background:var(--sup);border:1px solid var(--linha);border-radius:14px;padding:14px}}
.card .v{{font-family:var(--titulo);font-size:26px;font-weight:700;color:#f0a500}}
.card .l{{color:var(--mut);font-size:12px}}
table{{width:100%;border-collapse:collapse;background:var(--sup);border-radius:12px;overflow:hidden}}
th,td{{padding:9px 12px;font-size:13px;border-bottom:1px solid var(--linha);text-align:left}}
th{{background:var(--sup2);font-size:12px;color:var(--mut)}}
td.n,th.n{{text-align:right}}
h2{{font-family:var(--titulo);font-size:16px;margin:18px 0 8px}}
footer{{margin-top:22px;color:var(--mut);font-size:12px;text-align:center;border-top:1px solid var(--linha);padding-top:12px}}
</style></head><body><div class="pag">
<header class="barra"><span class="mono">CM</span><div><h1>Miro Câmara · Prestação de contas</h1>
<span class="sub">Câmara de Monção · canal do cidadão · demonstração</span></div></header>
<div class="cards">
<div class="card"><div class="v">{leads}</div><div class="l">cidadãos atendidos</div></div>
<div class="card"><div class="v">{total_ch}</div><div class="l">demandas registradas</div></div>
<div class="card"><div class="v">{abertos}</div><div class="l">em acompanhamento</div></div>
<div class="card"><div class="v">{msgs}</div><div class="l">mensagens trocadas</div></div>
</div>
<h2>Demandas por gabinete</h2>
<table><tr><th>Gabinete</th><th class="n">Demandas</th></tr>{gab_rows}</table>
<h2>Demandas por assunto (pauta para indicações)</h2>
<table><tr><th>Assunto</th><th class="n">Pedidos</th><th class="n">%</th></tr>{linhas}</table>
<footer>Painel de demonstração gerado a partir dos dados fictícios da demo em {agora}.<br>
Em produção, esta página seria pública e atualizada automaticamente — transparência do trabalho dos gabinetes.</footer>
</div></body></html>"""
open(OUT, "w").write(pagina)
print("PRESTACAO-OK", OUT, "| leads:", leads, "| chamados:", total_ch)
