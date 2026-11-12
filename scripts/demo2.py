#!/usr/bin/env python3
"""Demo v2 Câmara de Monção: cidadã digita na própria página (clip1), equipe (clip2), gestor (clip3)."""
import json, subprocess, time, urllib.request, os, signal

B = 'http://127.0.0.1:8097'
DIR = '/tmp/moncao-poc'
CFG = json.load(open(f'{DIR}/dados/negocio.json'))
TOK = CFG['token_gestor']; COD_ANA = CFG['equipe'][0]['codigo']
TEL, NOME = '5598981112222', 'Maria Souza'
DISP = ':99'

def log(*a): print(' '.join(str(x) for x in a), flush=True)

def req(metodo, rota, corpo=None, token=None, codigo=None):
    r = urllib.request.Request(B + rota, method=metodo)
    if corpo is not None:
        r.add_header('Content-Type', 'application/json'); r.data = json.dumps(corpo).encode()
    if token: r.add_header('X-Token', token)
    if codigo: r.add_header('X-Codigo', codigo)
    try:
        with urllib.request.urlopen(r) as resp:
            return resp.status, json.loads(resp.read() or b'{}')
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b'{}')

def cdp(cmd, arg):
    r = subprocess.run(['node', f'{DIR}/cdp.js', cmd, arg], capture_output=True, text=True, timeout=30)
    log(f"  cdp {cmd}: {(r.stdout.strip() or r.stderr.strip())[:120]}")

def digita(msg):
    js = ("var t=document.getElementById('texto');t.value=" + json.dumps(msg) +
          ";document.getElementById('form-msg').dispatchEvent(new Event('submit',{cancelable:true}));'enviado'")
    cdp('eval', js)
    log(f"  maria digitou: {msg!r}")

def web(sess, texto):
    st, r = req('POST', '/api/mensagens', {'canal': 'web', 'sessao': sess, 'texto': texto}, token=TOK)
    log(f"  maria(api): {texto!r} -> {json.dumps(r.get('respostas'), ensure_ascii=False)[:120]}")

def gravar(nome):
    p = subprocess.Popen(['ffmpeg', '-f', 'x11grab', '-video_size', '1280x800', '-framerate', '15',
                          '-i', DISP, '-c:v', 'libx264', '-preset', 'veryfast', '-pix_fmt', 'yuv420p',
                          '-y', f'{DIR}/{nome}'], env={'DISPLAY': DISP, 'PATH': os.environ['PATH']},
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2); log(f'  rec {nome}'); return p

def parar(p):
    p.send_signal(signal.SIGINT)
    try: p.wait(timeout=10)
    except subprocess.TimeoutExpired: p.kill(); p.wait()
    time.sleep(1); log('  rec parado')

log('== 0. prepara ==')
st, r = req('POST', '/api/equipe/status', {'status': 'livre'}, codigo=COD_ANA); log('ana livre:', st)
cdp('nav', f'{B}/')
cdp('eval', "localStorage.removeItem('al_sessao');localStorage.setItem('al_tel','" + TEL + "');localStorage.setItem('al_nome','" + NOME + "');'limpo'")
cdp('nav', f'{B}/')
time.sleep(2)

log('== 1. clipe 1: chat da cidadã ==')
p = gravar('clip1.mp4'); time.sleep(3)
cdp('eval', "document.getElementById('nome').value='" + NOME + "';document.getElementById('telefone').value='" + TEL +
    "';document.getElementById('form-entrada').dispatchEvent(new Event('submit',{cancelable:true}));'entrou'")
time.sleep(8)                      # saudação + menu visíveis
digita('1'); time.sleep(9)         # escolhe: falar com vereador
digita('1'); time.sleep(9)         # urgência: hoje/esta semana -> chamado silencioso
digita('tá faltando água no meu bairro faz três dias'); time.sleep(10)
digita('e a ponte do bairro continua quebrada'); time.sleep(10)
digita('tem alguém aí?'); time.sleep(9)
cdp('shot', f'{DIR}/print-chat.png')
parar(p)

st, r = req('GET', '/api/gestor/leads', token=TOK)
sess = r[0]['sessao']; log('sessao:', sess)

log('== 2. relógio +6 min -> alerta ==')
log('relogio:', req('POST', '/api/relogio', {'agora': '2026-11-12T14:11:00'}, token=TOK))
log('tarefas:', req('POST', '/api/tarefas/rodar', {}, token=TOK))

log('== 3. clipe 2: equipe (Ana) ==')
cdp('nav', f'{B}/equipe')
cdp('eval', "localStorage.setItem('al_codigo_equipe','" + COD_ANA + "');'seed'")
cdp('nav', f'{B}/equipe')
time.sleep(2)
p = gravar('clip2.mp4'); time.sleep(6)
st, r = req('GET', '/api/gestor/ao-vivo', token=TOK)
cid = (r.get('fila') or [{}])[0].get('id')
log('chamado:', cid, '| alertas:', json.dumps(r.get('alertas'), ensure_ascii=False)[:150])
st, r = req('POST', f'/api/equipe/chamados/{cid}/assumir', {}, codigo=COD_ANA)
log('ana assumiu:', st); time.sleep(6)
cdp('eval', "(function(){var b=document.querySelector('[data-ficha]');if(b){b.click();return 'ficha';}return 'sem';})()")
time.sleep(5)
web(sess, 'quais serviços a câmara oferece?'); time.sleep(6)
st, r = req('GET', '/api/equipe/leads/1', codigo=COD_ANA)
sug = r.get('sugestao') or {}
st, r = req('POST', f'/api/equipe/chamados/{cid}/responder',
            {'texto': sug.get('texto') or 'sem sugestao', 'sugestao_id': sug.get('id')}, codigo=COD_ANA)
log('ana (usada):', st); time.sleep(7)
web(sess, 'e como faço uma denúncia?'); time.sleep(6)
st, r = req('GET', '/api/equipe/leads/1', codigo=COD_ANA)
sug = r.get('sugestao') or {}
st, r = req('POST', f'/api/equipe/chamados/{cid}/responder',
            {'texto': 'A ouvidoria recebe sua denúncia com número de protocolo. Já registrei a sua e a Câmara acompanha a resposta, tá bem?',
             'sugestao_id': sug.get('id')}, codigo=COD_ANA)
log('ana (editada):', st); time.sleep(7)
web(sess, 'muito obrigada!'); time.sleep(5)
st, r = req('POST', f'/api/equipe/chamados/{cid}/responder',
            {'texto': 'Por nada, Maria! Vou agendar seu horário no gabinete e te confirmo amanhã de manhã.'}, codigo=COD_ANA)
log('ana (livre):', st); time.sleep(6)
st, r = req('POST', f'/api/equipe/chamados/{cid}/fechar',
            {'resultado': 'retornar', 'retornar_em': '2026-11-13T09:00', 'nota': 'Confirmar horário no gabinete'}, codigo=COD_ANA)
log('fechou:', st); time.sleep(5)
cdp('shot', f'{DIR}/print-equipe.png')
parar(p)

log('== 4. clipe 3: gestor ==')
cdp('nav', f'{B}/gestor')
cdp('eval', "localStorage.setItem('al_token_gestor','" + TOK + "');'seed'")
cdp('nav', f'{B}/gestor')
time.sleep(3)
p = gravar('clip3.mp4'); time.sleep(8)
cdp('shot', f'{DIR}/print-gestor-aovivo.png')
cdp('eval', "document.getElementById('t-hoje').click();'hoje'"); time.sleep(7)
cdp('shot', f'{DIR}/print-gestor-hoje.png')
cdp('eval', "document.getElementById('t-aprendizado').click();'aprendizado'"); time.sleep(8)
cdp('shot', f'{DIR}/print-gestor-aprendizado.png')
cdp('eval', "document.getElementById('t-base').click();'base'"); time.sleep(6)
cdp('shot', f'{DIR}/print-gestor-base.png')
parar(p)

log('== 5. concat ==')
open(f'{DIR}/clips.txt', 'w').write("file 'clip1.mp4'\nfile 'clip2.mp4'\nfile 'clip3.mp4'\n")
subprocess.run(['ffmpeg', '-f', 'concat', '-safe', '0', '-i', f'{DIR}/clips.txt', '-c', 'copy',
                '-y', f'{DIR}/demo-camara-moncao.mp4'], capture_output=True)
for f in ('clip1.mp4', 'clip2.mp4', 'clip3.mp4', 'demo-camara-moncao.mp4'):
    cam = f'{DIR}/{f}'
    log(f, os.path.getsize(cam) if os.path.exists(cam) else 'FALTOU')
log('FIM')
