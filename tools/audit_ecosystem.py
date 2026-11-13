#!/usr/bin/env python3
"""Living-record ecosystem audit. Usage: audit_ecosystem.py <repos-dir> [output.json]
Clones are expected as shallow checkouts, one directory per repo, with .git present."""
import os, sys, json, re, subprocess
from collections import Counter

BASE = sys.argv[1] if len(sys.argv) > 1 else '.'
OUT = sys.argv[2] if len(sys.argv) > 2 else 'audit.json'
EXT_LANG = {'.js':'JavaScript','.ts':'TypeScript','.tsx':'TypeScript','.jsx':'JavaScript','.py':'Python','.sol':'Solidity','.html':'HTML','.css':'CSS','.vue':'Vue','.rs':'Rust','.go':'Go','.java':'Java','.php':'PHP','.rb':'Ruby','.swift':'Swift','.dart':'Dart'}
SECRET_RX = [
    ('Stripe live key', re.compile(r'sk_live_[A-Za-z0-9]{60,}')),
    ('GitHub token', re.compile(r'gh[pous]_[A-Za-z0-9]{36}')),
    ('AWS access key', re.compile(r'AKIA[0-9A-Z]{16}')),
    ('Google API key', re.compile(r'AIza[0-9A-Za-z_-]{35}')),
    ('Private key block', re.compile(r'-----BEGIN (RSA |EC |OPENSSH |PGP )?PRIVATE KEY-----')),
]
TEXT_EXT = {'.js','.ts','.tsx','.jsx','.py','.sol','.json','.md','.yml','.yaml','.sh','.html','.txt','.toml','.env','.cfg','.ini'}

def audit(repo):
    info = {'repo': repo, 'files': 0, 'size_kb': 0, 'top_lang': 'docs/none', 'category': 'near-empty'}
    files = []
    for root, dirs, fs in os.walk(repo):
        dirs[:] = [d for d in dirs if d not in ('.git','node_modules','dist','build','.next')]
        for f in fs: files.append(os.path.join(root, f).replace(repo + os.sep, '', 1))
    info['files'] = len(files)
    du = subprocess.run(['du', '-sk', './' + repo], capture_output=True, text=True).stdout.split()
    info['size_kb'] = int(du[0]) if du else 0
    langs = Counter(EXT_LANG[os.path.splitext(f)[1].lower()] for f in files if os.path.splitext(f)[1].lower() in EXT_LANG)
    if langs: info['top_lang'] = langs.most_common(1)[0][0]
    fl = set(files); low = {f.lower() for f in files}
    info.update(readme=any(f.startswith('readme') for f in low), license=any(f.startswith('licen') for f in low),
                gitignore='.gitignore' in fl, pkg='package.json' in fl,
                ci=any(f.startswith('.github' + os.sep + 'workflows' + os.sep) for f in files),
                tests=any('test' in f.lower() or 'spec' in f.lower() for f in files),
                env_committed='.env' in fl or any(f.startswith('.env.') and f != '.env.example' for f in fl))
    hits = []
    for f in files:
        if os.path.splitext(f)[1].lower() in TEXT_EXT:
            p = os.path.join(repo, f)
            try:
                if os.path.getsize(p) > 200000: continue
                txt = open(p, encoding='utf-8', errors='ignore').read()
                for name, rx in SECRET_RX:
                    if rx.search(txt): hits.append(f'{f} [{name}]')
            except OSError: pass
    info['secret_hits'] = hits[:8]; info['n_secret_hits'] = len(hits)
    info['last_commit'] = subprocess.run(['git','-C',repo,'log','-1','--format=%cs'],capture_output=True,text=True).stdout.strip() or 'never'
    if info['files'] <= 2: info['category'] = 'near-empty'
    elif info['top_lang'] in ('TypeScript','JavaScript','Python','Solidity','Vue','HTML') and info['files'] >= 8: info['category'] = 'app/code'
    elif info['top_lang'] == 'Markdown': info['category'] = 'docs/manifesto'
    else: info['category'] = 'mixed/other'
    return info

repos = sorted(d for d in os.listdir(BASE) if os.path.isdir(os.path.join(BASE, d)) and os.path.exists(os.path.join(BASE, d, '.git')))
results = [audit(r) for r in repos]
json.dump(results, open(OUT, 'w'), indent=1)
print(f"Audited {len(results)} repos -> {OUT}")
print(f"apps: {sum(1 for r in results if r['category']=='app/code')} | docs: {sum(1 for r in results if r['category']=='docs/manifesto')} | near-empty: {sum(1 for r in results if r['category']=='near-empty')}")
for r in results:
    if r['n_secret_hits']: print('  SECRET SIGNAL:', r['repo'], r['secret_hits'][:3])
