#!/usr/bin/env python3
# Gera web/gabinete.html: pagina do gabinete (LEGISLAR + FISCALIZAR) da demo Moncao.
# Rascunhos de proposituras sao gerados pelo assistente virtual local (LLM) com fallback.
# URL, modelo e chave do modelo local vem de variaveis de ambiente (nunca versionar segredos).
import html, json, os, re, sys, urllib.request, datetime

OUT = sys.argv[1] if len(sys.argv) > 1 else "web/gabinete.html"
CEREBRO_URL = os.environ.get("CEREBRO_URL", "http://127.0.0.1:8644/v1/chat/completions")
CEREBRO_KEY = os.environ.get("CEREBRO_API_KEY", "")
CEREBRO_MODELO = os.environ.get("CEREBRO_MODELO", "assistente-local")
HOJE = datetime.date(2026, 11, 12)  # data de referencia da demonstracao

def assistente(prompt, max_tokens=520):
    corpo = json.dumps({
        "model": CEREBRO_MODELO,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
    }).encode()
    req = urllib.request.Request(CEREBRO_URL, data=corpo, headers={
        "Content-Type": "application/json",
        "Authorization": "Bearer " + CEREBRO_KEY,
    })
    with urllib.request.urlopen(req, timeout=40) as r:
        d = json.loads(r.read())
    return d["choices"][0]["message"]["content"].strip()

FALLBACK = {
"indicacao": """EMENTA: Indica ao Chefe do Executivo Municipal a recuperacao da iluminacao publica da Praca Presidente Kennedy, no Centro de Moncao.

FUNDAMENTACAO: A Praca Presidente Kennedy e o principal ponto de encontro do Centro de Moncao. Nos ultimos dias, o canal de atendimento deste gabinete recebeu 2 manifestacoes de moradores relatando lampadas apagadas e sensacao de inseguranca no periodo noturno. A recuperacao da iluminacao e medida simples, de baixo custo e alto impacto para a populacao.

Indico, com fundamento no art. 230 do Regimento Interno, que seja providenciada a revisao e o reparo da iluminacao publica da referida praca.""",
"requerimento": """EMENTA: Requer informacoes ao Chefe do Executivo Municipal sobre as interrupcoes no abastecimento de agua no Bairro Centro, Moncao.

FUNDAMENTACAO: O canal de atendimento deste gabinete registrou 3 relatos de moradores do Centro sobre falta d'agua recorrente. A agua e servico essencial, e a populacao precisa de previsao e transparencia sobre o problema.

Diante disso, requer seja informado: 1) qual a causa das interrupcoes; 2) qual o prazo previsto para normalizacao; 3) quais obras ou medidas estao programadas para o bairro.""",
"projeto": """EMENTA: Institui o Programa Municipal de Manutencao Preventiva de Vias e Pracas e da outras providencias.

Art. 1o Fica instituido o Programa Municipal de Manutencao Preventiva de Vias e Pracas, com inspecao periodica e reparo programado de pisos, drenagem e sinalizacao.

Art. 2o O Executivo publicara relatorio semestral das vias e pracas inspecionadas e dos reparos realizados.

Art. 3o Esta Lei entra em vigor na data de sua publicacao.

JUSTIFICACAO: Relatos recebidos pelo gabinete apontam rua escorregadia e buracos em vias do municipio. A manutencao preventiva evita acidentes e reduz custos de emergencia.""",
}

PROMPTS = {
"indicacao": "Voce e o assistente virtual legislativo do gabinete de uma vereadora da Camara Municipal de Moncao (MA). Escreva um RASCUNHO curto de INDICACAO ao Chefe do Executivo municipal. Tema: recuperacao da iluminacao publica da Praca Presidente Kennedy, Centro de Moncao, motivada por 2 manifestacoes de moradores recebidas pelo canal de atendimento do gabinete. Formato exato: primeira linha 'EMENTA: <uma linha>', depois 'FUNDAMENTACAO:' com 3 frases curtas citando que a praca e ponto de encontro e que moradores relatam inseguranca a noite, e por fim 1 paragrafo com a indicacao formal. Linguagem simples, sem parecer juridico.",
"requerimento": "Voce e o assistente virtual legislativo do gabinete de uma vereadora da Camara Municipal de Moncao (MA). Escreva um RASCUNHO curto de REQUERIMENTO DE INFORMACOES ao Chefe do Executivo sobre interrupcoes no abastecimento de agua no Bairro Centro de Moncao, apos 3 relatos de moradores no canal do gabinete. Formato exato: primeira linha 'EMENTA: <uma linha>', depois 'FUNDAMENTACAO:' com 3 frases curtas, depois 3 perguntas objetivas numeradas sobre causa, prazo de normalizacao e medidas programadas. Linguagem simples, sem parecer juridico.",
"projeto": "Voce e o assistente virtual legislativo do gabinete de um vereador da Camara Municipal de Moncao (MA). Escreva um RASCUNHO curto de PROJETO DE LEI que institui o Programa Municipal de Manutencao Preventiva de Vias e Pracas, apos relatos de rua escorregadia e buracos. Formato exato: primeira linha 'EMENTA: <uma linha>', depois 3 artigos curtos (Art. 1o, Art. 2o, Art. 3o) e uma JUSTIFICACAO de 2 frases. Linguagem simples, sem parecer juridico.",
}

gerado_por = {}
rascunhos = {}
try:
    assistente("Responda apenas: ok", max_tokens=8)  # aquecimento
except Exception:
    pass
for chave, prompt in PROMPTS.items():
    try:
        rascunhos[chave] = assistente(prompt)
        gerado_por[chave] = "assistente virtual"
    except Exception as e:
        print("ASSISTENTE-FALHOU", chave, e, file=sys.stderr)
        rascunhos[chave] = FALLBACK[chave]
        gerado_por[chave] = "modelo local (fallback)"

def corpo_rascunho(txt):
    txt = txt.replace("**", "")
    linhas = [l.strip() for l in txt.splitlines()]
    partes = []
    for l in linhas:
        if not l:
            continue
        if l.upper().startswith("EMENTA:"):
            partes.append("<p class='em'><b>Ementa:</b> " + html.escape(l.split(":",1)[1].strip()) + "</p>")
        elif re.match(r"^(FUNDAMENTA|JUSTIFICATIVA|JUSTIFICACAO)", l.upper()):
            resto = l.split(":",1)
            partes.append("<p><b>" + html.escape(resto[0].strip().title()) + ":</b> " + html.escape(resto[1].strip() if len(resto)>1 else "") + "</p>")
        else:
            partes.append("<p>" + html.escape(l) + "</p>")
    return "".join(partes)

def dias_para(prazo):
    return (prazo - HOJE).days

# ---------- dados ficticios da demonstracao ----------
GABINETES = [
    ("daerlio", "Gabinete Ver. Daerlio", "Ana e Rafa"),
    ("lindolene", "Gabinete Ver.\u00aa Lindolene", "Bia e Rui"),
    ("moizaniel", "Gabinete Ver. Moizaniel", "T\u00e9o"),
    ("luis-alfredo", "Gabinete Ver. Lu\u00eds Alfredo", "Zeca"),
    ("amorim", "Gabinete Ver. Amorim", "L\u00eda"),
    ("chapreu", "Gabinete Ver. Chapreu", "Nando"),
    ("chixolinha", "Gabinete Ver. Chixolinha", "Mara"),
    ("dr-abrao-muniz", "Gabinete Ver. Dr. Abr\u00e3o Muniz", "Ivo"),
    ("dr-anderson-carvalho", "Gabinete Ver. Dr. Anderson Carvalho", "Sol"),
    ("flavio-campos", "Gabinete Ver. Fl\u00e1vio Campos", "Du"),
    ("junior-da-pesca", "Gabinete Ver. Junior da Pesca", "Kiko"),
    ("nonato-do-sindicato", "Gabinete Ver. Nonato do Sindicato", "Dani"),
    ("uerickson-do-castelo", "Gabinete Ver. Uerickson do Castelo", "L\u00e9o"),
]

DEMANDAS = [
    ("daerlio", "Falta d'agua recorrente", "Bairro Centro", 3, "3 manifestacoes no canal do gabinete"),
    ("lindolene", "Iluminacao apagada", "Praca Presidente Kennedy", 2, "2 manifestacoes no canal do gabinete"),
    ("moizaniel", "Rua escorregadia / buracos", "Rua do Porto", 1, "1 manifestacao no canal do gabinete"),
    ("luis-alfredo", "Limpeza publica", "Mercado Municipal", 1, "1 manifestacao no canal do gabinete"),
]

RASCUNHOS = [
    ("lindolene", "INDICACAO", "n\u00ba ___/2026", "Iluminacao da Praca Presidente Kennedy", "indicacao", ["Rascunho pronto", "Revisao do(a) vereador(a)", "Protocolo", "Comissao", "Plenario"], 0),
    ("daerlio", "REQUERIMENTO", "n\u00ba ___/2026", "Informacoes sobre a falta d'agua no Centro", "requerimento", ["Rascunho pronto", "Revisao do(a) vereador(a)", "Protocolo", "Comissao", "Plenario"], 1),
    ("moizaniel", "PROJETO DE LEI", "n\u00ba ___/2026", "Programa de Manutencao Preventiva de Vias e Pracas", "projeto", ["Rascunho pronto", "Revisao do(a) vereador(a)", "Protocolo", "Comissao", "Plenario"], 2),
]

# protocolo: (gab, numero, assunto, bairro, enviado, prazo, respondido_em ou None)
PROTOCOLOS = [
    ("daerlio", "REQ 012/2026", "Falta d'agua", "Bairro Centro", datetime.date(2026,10,20), datetime.date(2026,11,19), None),
    ("lindolene", "IND 034/2026", "Iluminacao publica", "Praca Pres. Kennedy", datetime.date(2026,11,5), datetime.date(2026,12,5), None),
    ("moizaniel", "OF 007/2026", "Rua escorregadia", "Rua do Porto", datetime.date(2026,9,10), datetime.date(2026,10,10), None),
    ("luis-alfredo", "REQ 011/2026", "Limpeza publica", "Mercado Municipal", datetime.date(2026,11,2), datetime.date(2026,12,2), datetime.date(2026,11,8)),
]

HISTORICO = [
    ("Abastecimento de agua", 3, 1),
    ("Iluminacao publica", 2, 0),
    ("Vias e pracas", 1, 0),
    ("Limpeza publica", 1, 1),
]

LEMBRETES = [
    ("*", "Sessao ordinaria (simulada) - terca e quinta, 15h. Proxima: quinta, 13/11."),
    ("daerlio", "REQ 012/2026 (falta d'agua) vence em %d dias (19/11) - cobrar resposta da Prefeitura." % dias_para(datetime.date(2026,11,19))),
    ("moizaniel", "OF 007/2026 (rua escorregadia) aguarda resposta ha %d dias - reiterar cobranca." % -dias_para(datetime.date(2026,10,10))),
    ("*", "Levar rascunhos revisados ao protocolo ate sexta, 14/11, para entrar na pauta da proxima sessao."),
]

# ---------- monta HTML ----------
demandas_html = "".join(
    f"<div class='gitem card' data-gab='{g}'><div class='card-top'><b>{html.escape(a)}</b>"
    f"<span class='qtd'>{n} pedido{'s' if n>1 else ''}</span></div>"
    f"<div class='mut'>{html.escape(b)}</div><div class='mut peq'>{html.escape(obs)}</div></div>"
    for g, a, b, n, obs in DEMANDAS)

def trilha(etapas, atual):
    passos = "".join(
        f"<span class='passo {'feito' if i <= atual else ''}'><i></i>{html.escape(e)}</span>"
        for i, e in enumerate(etapas))
    return f"<div class='trilha'>{passos}</div>"

rascunhos_html = "".join(
    f"<div class='gitem rasc' data-gab='{g}'>"
    f"<div class='rasc-head'><span class='badge'>{tipo}</span><span class='mut'>{num}</span>"
    f"<span class='tag-ia'>rascunho gerado por IA - para revisao</span></div>"
    f"<h3>{html.escape(titulo)}</h3>"
    f"{corpo_rascunho(rascunhos[chave])}"
    f"{trilha(etapas, etapa)}"
    f"<div class='mut peq'>Tramitacao simulada para demonstracao. Origem do texto: {gerado_por[chave]}.</div></div>"
    for g, tipo, num, titulo, chave, etapas, etapa in RASCUNHOS)

def linha_protocolo(g, num, assunto, bairro, enviado, prazo, respondido):
    if respondido:
        st = "<span class='pill ok'>respondido em %s</span>" % respondido.strftime("%d/%m")
        d = "—"
    else:
        drest = dias_para(prazo)
        if drest < 0:
            st = "<span class='pill venc'>aguardando resposta</span>"
            d = f"<b class='venc'>{-drest}d de atraso</b>"
        elif drest <= 7:
            st = "<span class='pill warn'>vence em breve</span>"
            d = f"<b class='warn'>{drest}d restantes</b>"
        else:
            st = "<span class='pill ok'>no prazo</span>"
            d = f"{drest}d restantes"
    return (f"<tr class='gitem' data-gab='{g}'><td><b>{num}</b></td><td>{html.escape(assunto)}</td>"
            f"<td>{html.escape(bairro)}</td><td>{enviado.strftime('%d/%m')}</td>"
            f"<td>{prazo.strftime('%d/%m')}</td><td>{d}</td><td>{st}</td></tr>")

prot_html = "".join(linha_protocolo(*p) for p in PROTOCOLOS)

hist_html = "".join(
    f"<tr><td>{html.escape(a)}</td><td class='n'>{e}</td><td class='n'>{r}</td></tr>"
    for a, e, r in HISTORICO)

lembr_html = "".join(
    f"<li class='gitem' data-gab='{g}'>{html.escape(t)}</li>" for g, t in LEMBRETES)

opcoes_gab = "\n".join(
    f"<option value='{g}'>{html.escape(nome)} — atend. {html.escape(equipe)}</option>"
    for g, nome, equipe in GABINETES)

agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")

pagina = f"""<!doctype html>
<html lang="pt-BR" data-tema="marinho"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Miro Câmara — Página Gabinete (demonstração)</title>
<link rel="stylesheet" href="/web/style.css">
<style>
body{{margin:0;font-family:var(--corpo);background:var(--bg);color:var(--tinta)}}
.pag{{max-width:860px;margin:0 auto;padding:16px}}
.barra{{display:flex;align-items:center;gap:10px;margin-bottom:12px}}
.mono{{width:40px;height:40px;border-radius:50%;background:#f0a500;color:#1a1206;display:flex;align-items:center;justify-content:center;font-weight:700;font-family:var(--titulo);flex:none}}
h1{{font-family:var(--titulo);font-size:21px;margin:0}}
.sub{{color:var(--mut);font-size:13px}}
.abas{{display:flex;gap:10px;margin:14px 0 4px;flex-wrap:wrap;align-items:center}}
.abas select{{border:1px solid var(--linha);background:var(--sup);color:var(--tinta);border-radius:10px;padding:8px 12px;font-size:13.5px;font-family:var(--corpo);max-width:100%}}
.secao{{font-family:var(--titulo);font-size:15px;letter-spacing:.06em;margin:22px 0 4px;color:#f0a500;text-transform:uppercase}}
.secao-desc{{color:var(--mut);font-size:12.5px;margin:0 0 10px}}
.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:10px}}
.card{{background:var(--sup);border:1px solid var(--linha);border-radius:14px;padding:12px 14px}}
.card-top{{display:flex;justify-content:space-between;gap:8px;align-items:baseline}}
.qtd{{background:#f0a500;color:#1a1206;border-radius:999px;font-size:11px;font-weight:700;padding:2px 8px;white-space:nowrap}}
.mut{{color:var(--mut);font-size:13px;margin-top:4px}}
.peq{{font-size:11.5px}}
.rasc{{background:var(--sup);border:1px solid var(--linha);border-radius:14px;padding:14px 16px;margin:10px 0}}
.rasc h3{{font-family:var(--titulo);font-size:16px;margin:8px 0 6px}}
.rasc p{{font-size:13.5px;margin:6px 0;line-height:1.45}}
.rasc-head{{display:flex;gap:8px;align-items:center;flex-wrap:wrap}}
.badge{{background:var(--sup2);border:1px solid var(--linha);border-radius:6px;font-size:11px;font-weight:700;padding:3px 8px;letter-spacing:.04em}}
.tag-ia{{background:#f0a50022;border:1px solid #f0a500;color:#f0a500;border-radius:999px;font-size:10.5px;font-weight:700;padding:2px 9px}}
.trilha{{display:flex;flex-wrap:wrap;gap:4px 0;margin:12px 0 4px}}
.passo{{display:flex;align-items:center;gap:6px;font-size:11px;color:var(--mut);margin-right:10px}}
.passo i{{width:10px;height:10px;border-radius:50%;border:2px solid var(--linha);display:inline-block}}
.passo.feito{{color:var(--tinta)}}
.passo.feito i{{background:#f0a500;border-color:#f0a500}}
table{{width:100%;border-collapse:collapse;background:var(--sup);border-radius:12px;overflow:hidden}}
.tblwrap{{overflow-x:auto;border-radius:12px;-webkit-overflow-scrolling:touch}}
.tblwrap table{{min-width:600px}}
th,td{{padding:8px 10px;font-size:12.5px;border-bottom:1px solid var(--linha);text-align:left;vertical-align:top}}
th{{background:var(--sup2);font-size:11.5px;color:var(--mut)}}
td.n,th.n{{text-align:right}}
.pill{{border-radius:999px;font-size:10.5px;font-weight:700;padding:2px 9px;white-space:nowrap}}
.pill.ok{{background:#2e7d3233;color:#7bd88f}}
.pill.warn{{background:#f0a50033;color:#f0a500}}
.pill.venc{{background:#c6282833;color:#ef7b7b}}
b.warn{{color:#f0a500}} b.venc{{color:#ef7b7b}}
ul.lembr{{margin:0;padding-left:0;list-style:none}}
ul.lembr li{{background:var(--sup);border:1px solid var(--linha);border-radius:10px;padding:9px 12px;margin:6px 0;font-size:13px}}
footer{{margin-top:24px;color:var(--mut);font-size:12px;text-align:center;border-top:1px solid var(--linha);padding-top:12px}}
.oculto{{display:none}}
</style></head><body><div class="pag">
<header class="barra"><span class="mono" id="monoF">CM</span><img src="/web/midia/brasao.png" alt="Brasão de Monção" style="display:none;width:42px;height:auto" onload="this.style.display='block';document.getElementById('monoF').style.display='none'"><div><h1>Miro Câmara · Página Gabinete</h1>
<span class="sub">Câmara de Monção · trabalho dos gabinetes · demonstração</span></div></header>
<div class="abas" id="abas">
<label for="selgab" style="font-size:13px;color:var(--mut)">Espaço do gabinete:</label>
<select id="selgab">
<option value="geral">Visão geral (todos os gabinetes)</option>
{opcoes_gab}
</select>
</div>
<p class="secao-desc">Cada gabinete tem seu espaço e seus próprios assessores; a visão geral soma todos. Escolha um gabinete para ver só as demandas, protocolos e rascunhos dele. Dados fictícios de demonstração.</p>

<div class="secao">Legislar</div>
<p class="secao-desc">As demandas que chegam pelo chat viram pauta: agrupadas por assunto e bairro, o assistente virtual redige o <b>rascunho</b> da propositura (indicação, requerimento ou projeto de lei) — sempre para o vereador revisar antes de protocolar. Não é parecer jurídico.</p>

<h2 style="font-family:var(--titulo);font-size:15px;margin:12px 0 8px">Demandas agrupadas (do canal do cidadão)</h2>
<div class="cards">{demandas_html}</div>

<h2 style="font-family:var(--titulo);font-size:15px;margin:16px 0 8px">Rascunhos de proposituras</h2>
{rascunhos_html}

<div class="secao">Fiscalizar</div>
<p class="secao-desc">Cada encaminhamento à Prefeitura vira um protocolo com prazo. O gabinete cobra a resposta, recebe alerta de vencimento e acompanha o histórico por assunto e bairro.</p>

<h2 style="font-family:var(--titulo);font-size:15px;margin:12px 0 8px">Protocolos com a Prefeitura</h2>
<div class='tblwrap'><table><tr><th>Protocolo</th><th>Assunto</th><th>Local</th><th>Enviado</th><th>Prazo</th><th>Situação</th><th>Status</th></tr>{prot_html}</table></div>

<h2 style="font-family:var(--titulo);font-size:15px;margin:16px 0 8px">Histórico por assunto</h2>
<table><tr><th>Assunto</th><th class="n">Encaminhamentos</th><th class="n">Respondidos</th></tr>{hist_html}</table>

<h2 style="font-family:var(--titulo);font-size:15px;margin:16px 0 8px">Lembretes de pauta e sessões</h2>
<ul class="lembr">{lembr_html}</ul>

<footer>Página de demonstração gerada em {agora}. Protocolos, prazos, demandas e rascunhos são fictícios.<br>
Brasão: site oficial da Câmara de Monção (cmmoncao.ma.gov.br).<br>
Os rascunhos de propositura são texto de apoio gerado por IA (assistente virtual) e exigem revisão do vereador antes de qualquer uso oficial.</footer>
</div>
<script>
document.getElementById('selgab').addEventListener('change',function(){{
  var g=this.value;
  document.querySelectorAll('.gitem').forEach(function(el){{
    var dg=el.getAttribute('data-gab');
    el.classList.toggle('oculto', g!=='geral' && dg!==g && dg!=='*');
  }});
}});
</script>
</body></html>"""
open(OUT, "w").write(pagina)
print("GABINETE-OK", OUT, "| origem dos rascunhos:", gerado_por)
