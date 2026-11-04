#!/usr/bin/env python3
"""Download mirror-referenced local files that are missing from the tree."""
import os, re, html, urllib.parse, urllib.request, sys
from collections import Counter

ROOT = os.path.expanduser("~/apps/taplai/www/taplaixe.vn")
ORIGIN = "https://taplaixe.vn"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36"

attr_re = re.compile(r'(?:src|href)\s*=\s*"([^"]+)"', re.I)
srcset_re = re.compile(r'srcset\s*=\s*"([^"]+)"', re.I)
css_url_re = re.compile(r'url\(\s*[\'"]?([^\'")]+)[\'"]?\s*\)', re.I)
FILE_EXT = re.compile(r'\.(webp|jpe?g|png|gif|svg|mp4|webm|woff2?|ttf|eot|ico|css|js|json|pdf)$', re.I)

missing = set()

def check(ref, base_dir):
    ref = html.unescape(ref).strip()
    if not ref or ref.startswith(('data:', 'mailto:', 'tel:', 'javascript:', '#', '//')):
        return
    if ref.startswith('http'):
        if 'taplaixe.vn' not in ref:
            return
        p = urllib.parse.urlparse(ref)
        path = p.path
        target = os.path.join(ROOT, path.lstrip('/'))
    elif ref.startswith('/'):
        path = urllib.parse.urlparse(ref).path
        target = os.path.join(ROOT, path.lstrip('/'))
    else:
        p = urllib.parse.urlparse(ref)
        path = p.path
        if not path:
            return
        target = os.path.normpath(os.path.join(base_dir, path))
    if not FILE_EXT.search(path):
        return
    if not os.path.isfile(target):
        missing.add((path, target))

for dirpath, dirnames, filenames in os.walk(ROOT):
    for fn in filenames:
        if os.path.splitext(fn)[1].lower() not in ('.html', '.css', '.js'):
            continue
        fp = os.path.join(dirpath, fn)
        txt = open(fp, encoding='utf-8', errors='replace').read()
        refs = attr_re.findall(txt) + css_url_re.findall(txt)
        for ss in srcset_re.findall(txt):
            for part in ss.split(','):
                refs.append(part.strip().split(' ')[0])
        for r in refs:
            check(r, dirpath)

print("missing files:", len(missing))
ok = fail = 0
for path, target in sorted(missing):
    os.makedirs(os.path.dirname(target), exist_ok=True)
    url = ORIGIN + urllib.parse.quote(path)
    try:
        req = urllib.request.Request(url, headers={'User-Agent': UA})
        with urllib.request.urlopen(req, timeout=45) as r:
            data = r.read()
        if len(data) < 100:
            raise ValueError("too small")
        open(target, 'wb').write(data)
        ok += 1
    except Exception as e:
        fail += 1
        print("FAIL", path, e)
print(f"downloaded {ok}, failed {fail}")
