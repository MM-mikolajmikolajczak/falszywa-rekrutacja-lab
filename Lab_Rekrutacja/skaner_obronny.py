"""Szybki audyt pobranego repozytorium PRZED otwarciem w edytorze.   python skaner_obronny.py <folder>
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
