#!/usr/bin/env python3
"""Re-download JS/CSS/font assets from origin (they were damaged by a too-greedy
'?v=' rewrite) and re-apply only safe text rewrites."""
import os, re, urllib.request, urllib.parse

ROOT = os.path.expanduser("~/apps/taplai/www/taplaixe.vn")
ORIGIN = "https://taplaixe.vn"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36"

EXTS = ('.js', '.css', '.woff', '.woff2', '.ttf', '.eot', '.svg')

def rebrand(t):
    t = re.sub(r'TAPLAIXE\.VN', 'TAPLAI.8BIZ.NET', t)
    t = re.sub(r'Taplaixe\.vn', 'Taplai.8biz.net', t)
    t = re.sub(r'(?i)taplaixe\.vn', 'taplai.8biz.net', t)
    t = re.sub(r'(?i)taplaixe', 'Taplai', t)
    return t

targets = []
for dirpath, dirnames, filenames in os.walk(ROOT):
    for fn in filenames:
        if not fn.lower().endswith(EXTS):
            continue
        if fn == 'clone-exam-start.js':
            continue
        fp = os.path.join(dirpath, fn)
        rel = os.path.relpath(fp, ROOT)
        targets.append((rel, fp))

print("assets to refresh:", len(targets))
ok = fail = 0
for rel, fp in targets:
    url = ORIGIN + '/' + urllib.parse.quote(rel)
    try:
        req = urllib.request.Request(url, headers={'User-Agent': UA})
        with urllib.request.urlopen(req, timeout=60) as r:
            data = r.read()
        if len(data) < 20:
            raise ValueError("too small")
        # brand rewrite only when needed (plain string swap, safe)
        if b'taplaixe' in data.lower():
            data = rebrand(data.decode('utf-8', errors='replace')).encode('utf-8')
        open(fp, 'wb').write(data)
        ok += 1
    except Exception as e:
        fail += 1
        print("FAIL", rel, e)
print(f"refreshed {ok}, failed {fail}")
