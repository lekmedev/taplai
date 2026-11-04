#!/usr/bin/env python3
"""Inject the clone exam-start redirect script into pages that host #frmExam."""
import os, re, sys

ROOT = os.path.expanduser("~/apps/taplai/www/taplaixe.vn")
TAG = '<script src="/assets/scripts/clone-exam-start.js" defer></script>'
n = 0
for dirpath, dirnames, filenames in os.walk(ROOT):
    for fn in filenames:
        if not fn.endswith('.html'):
            continue
        fp = os.path.join(dirpath, fn)
        t = open(fp, encoding='utf-8', errors='replace').read()
        if 'id="frmExam"' not in t or 'clone-exam-start.js' in t:
            continue
        i = t.lower().rfind('</body>')
        if i == -1:
            t = t + TAG
        else:
            t = t[:i] + TAG + t[i:]
        open(fp, 'w', encoding='utf-8').write(t)
        n += 1
print("injected:", n)
