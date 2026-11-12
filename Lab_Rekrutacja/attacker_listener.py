"""LAB: 'serwer hakera'. Nasluchuje tylko na 127.0.0.1:4444 i wypisuje, co przyslal skrypt z zadania."""
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
