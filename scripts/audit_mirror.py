#!/usr/bin/env python3
"""Audit mirrored taplaixe.vn tree: find referenced local resources that are missing."""
import os, re, sys, json, urllib.parse
from collections import Counter, defaultdict

ROOT = os.path.expanduser("~/apps/taplai/www/taplaixe.vn")
ORIGIN = "https://taplaixe.vn"

attr_re = re.compile(r'(?:src|href)\s*=\s*"([^"]+)"', re.I)
srcset_re = re.compile(r'srcset\s*=\s*"([^"]+)"', re.I)
css_url_re = re.compile(r'url\(\s*[\'"]?([^\'")]+)[\'"]?\s*\)', re.I)

missing = Counter()
checked = 0

def candidates(ref, base_dir):
    ref = ref.strip()
    if not ref or ref.startswith(('data:', 'mailto:', 'tel:', 'javascript:', '#')):
        return []
    if ref.startswith('//'):
        return []
    if ref.startswith('http'):
        if 'taplaixe.vn' not in ref:
            return []
        p = urllib.parse.urlparse(ref)
        path = p.path
        if p.query:
            path = path + '?' + p.query
        return [os.path.join(ROOT, path.lstrip('/'))]
    # relative / root-relative
    if ref.startswith('/'):
        p = urllib.parse.urlparse(ref)
        path = p.path + ('?' + p.query if p.query else '')
        return [os.path.join(ROOT, path.lstrip('/'))]
    path = urllib.parse.urlparse(ref)
    rel = path.path + ('?' + path.query if path.query else '')
    return [os.path.join(base_dir, rel)]

def exists(c):
    if os.path.isfile(c):
        return True
    if os.path.isfile(c + '.html'):
        return True
    if os.path.isdir(c):
        return True
    return False

for dirpath, dirnames, filenames in os.walk(ROOT):
    for fn in filenames:
        ext = os.path.splitext(fn)[1].lower()
        if ext not in ('.html', '.css', '.js'):
            continue
        fp = os.path.join(dirpath, fn)
        try:
            txt = open(fp, encoding='utf-8', errors='replace').read()
        except Exception:
            continue
        refs = attr_re.findall(txt) + css_url_re.findall(txt)
        for ss in srcset_re.findall(txt):
            for part in ss.split(','):
                refs.append(part.strip().split(' ')[0])
        for r in refs:
            for c in candidates(r, dirpath):
                checked += 1
                if not exists(c):
                    missing[r] += 1

print("checked refs:", checked)
print("distinct missing:", len(missing))
for r, n in missing.most_common(60):
    print(f"{n:4d}  {r}")
