// Uso: node cdp.js nav 'URL' | node cdp.js eval 'JS' | node cdp.js shot /caminho.png
const fs = require('fs');
async function alvo() {
  const lista = await (await fetch('http://127.0.0.1:9223/json')).json();
  const pag = lista.find(t => t.type === 'page');
  if (!pag) throw new Error('sem alvo page');
  return pag.webSocketDebuggerUrl;
}
(async () => {
  const [cmd, arg] = process.argv.slice(2);
  const ws = new WebSocket(await alvo());
  let id = 0; const pend = {};
  ws.onmessage = ev => { const m = JSON.parse(ev.data); if (m.id && pend[m.id]) { pend[m.id](m.result); delete pend[m.id]; } };
  await new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej; });
  const send = (method, params = {}) => new Promise(res => { const i = ++id; pend[i] = res; ws.send(JSON.stringify({ id: i, method, params })); });
  await send('Page.enable'); await send('Runtime.enable');
  if (cmd === 'nav') { await send('Page.navigate', { url: arg }); await new Promise(r => setTimeout(r, 2500)); console.log('nav ok'); }
  else if (cmd === 'eval') { const r = await send('Runtime.evaluate', { expression: arg, awaitPromise: true, returnByValue: true }); console.log(JSON.stringify(r && r.result ? r.result.value : r)); }
  else if (cmd === 'shot') { await new Promise(r => setTimeout(r, 700)); const r = await send('Page.captureScreenshot', { format: 'png' }); fs.writeFileSync(arg, Buffer.from(r.data, 'base64')); console.log('shot ok'); }
  process.exit(0);
})().catch(e => { console.error(String(e)); process.exit(1); });
