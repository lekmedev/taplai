#!/usr/bin/env python3
"""Add a cache-busting ?v= to css/js references in HTML (CF cached the old broken assets)."""
import os, re, sys

ROOT = os.path.expanduser("~/apps/taplai/www/taplaixe.vn")
VER = "20261104b"
rx = re.compile(r'((?:src|href)="[^"]*?\.(?:css|js))(")', re.I)
n = 0
for dirpath, dirnames, filenames in os.walk(ROOT):
    for fn in filenames:
        if not fn.endswith('.html'):
            continue
        fp = os.path.join(dirpath, fn)
        t = open(fp, encoding='utf-8', errors='replace').read()
        nt, c = rx.subn(lambda m: m.group(1) + '?v=' + VER + m.group(2), t)
        if c:
            open(fp, 'w', encoding='utf-8').write(nt)
            n += c
print("refs busted:", n)
