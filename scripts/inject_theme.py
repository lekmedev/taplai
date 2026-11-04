#!/usr/bin/env python3
"""Inject the WEUP theme stylesheet right after main.css in every mirrored page."""
import os, re, sys

ROOT = os.path.expanduser("~/apps/taplai/www/taplaixe.vn")
VER = "1"
TAG = f'<link rel="stylesheet" href="/assets/styles/weup-theme.css?v={VER}">'
rx = re.compile(r'(<link[^>]+href="[^"]*assets/styles/main\.css[^"]*"[^>]*>)', re.I)

n = 0
for dirpath, _, filenames in os.walk(ROOT):
    for fn in filenames:
        if not fn.endswith('.html'):
            continue
        p = os.path.join(dirpath, fn)
        t = open(p, encoding='utf-8', errors='replace').read()
        if 'weup-theme.css' in t:
            continue
        nt, c = rx.subn(lambda m: m.group(1) + '\n' + TAG, t, count=1)
        if c:
            open(p, 'w', encoding='utf-8').write(nt)
            n += 1
print("pages themed:", n)
