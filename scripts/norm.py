#!/usr/bin/env python3
"""Normalize + rebrand the mirrored taplaixe.vn tree for taplai.8biz.net.

- renames files saved with query strings (assets: strip query; pages: __key-val.html)
- rewrites references in html/css/js
- rebrands taplaixe.vn -> taplai.8biz.net
- strips AdSense / GA / reCAPTCHA
- repoints contact + lead forms at /api/*
"""
import os, re, sys, shutil
from collections import Counter

ROOT = os.path.expanduser("~/apps/taplai/www/taplaixe.vn")
APPLY = "--apply" in sys.argv

PAGE_Q = re.compile(r'^(?P<base>[^?]+)\?(?P<key>[a-z]+)=(?P<val>[A-Za-z0-9]+)\.html$')

renamed = []
def rename_pass():
    for dirpath, dirnames, filenames in os.walk(ROOT, topdown=False):
        for fn in filenames:
            if '?' not in fn:
                continue
            src = os.path.join(dirpath, fn)
            m = PAGE_Q.match(fn)
            if m and m.group('base').endswith(('.html',)) is False:
                new = f"{m.group('base')}__{m.group('key')}-{m.group('val')}.html"
            else:
                new = fn.split('?')[0]
            dst = os.path.join(dirpath, new)
            renamed.append((src, dst))
            if APPLY:
                if os.path.exists(dst) and dst != src:
                    os.remove(src)
                else:
                    os.rename(src, dst)

# ---------- text rewrites ----------
R_ASSET_V = re.compile(r'%3Fv=[\w\-.]+')
R_DUP_EXT = re.compile(r'\.(css|js)\.(?:css|js)\b')
R_LONE_Q  = re.compile(r'%3F(?!v=)')
R_PAGE_Q  = re.compile(r'(?:\.\./)*([a-z0-9\-]+)%3F(dethi|chuyenmuc|hang)=([A-Za-z0-9]+)\.html', re.I)
R_PAGE_Q2 = re.compile(r'(?:\.\./)*([a-z0-9\-]+)\?(dethi|chuyenmuc|hang)=([A-Za-z0-9]+)\.html', re.I)
R_PLAIN_V = re.compile(r'\?v=[\w\-.]+')

AD_SCRIPTS = [
    re.compile(r'<script[^>]*adsbygoogle\.js[^>]*>\s*</script>', re.I),
    re.compile(r'<script[^>]*googletagmanager\.com[^>]*>\s*</script>', re.I),
    re.compile(r'<script[^>]*www\.google\.com/recaptcha[^>]*>\s*</script>', re.I),
    re.compile(r'<script[^>]*gstatic\.com/recaptcha[^>]*>\s*</script>', re.I),
    re.compile(r'<script[^>]*>\s*window\.dataLayer\s*=\s*window\.dataLayer.{0,600}?</script>', re.S | re.I),
    re.compile(r'<script[^>]*>\s*document\.GOOGLE_RECAPTCHA_SITE_KEY.{0,200}?</script>', re.S | re.I),
    re.compile(r'<ins[^>]*adsbygoogle[^>]*>.*?</ins>', re.S | re.I),
    re.compile(r'\(adsbygoogle\s*=\s*window\.adsbygoogle\s*\|\|\s*\[\]\)\.push\(\{\}\);\s*', re.I),
]

def rebrand(t):
    t = re.sub(r'TAPLAIXE\.VN', 'TAPLAI.8BIZ.NET', t)
    t = re.sub(r'Taplaixe\.vn', 'Taplai.8biz.net', t)
    t = re.sub(r'(?i)taplaixe\.vn', 'taplai.8biz.net', t)
    t = re.sub(r'(?i)taplaixe', 'Taplai', t)
    return t

stats = Counter()

def rewrite(t, fn=''):
    t, n1 = R_ASSET_V.subn('', t)
    t, n2 = R_DUP_EXT.subn(lambda m: '.' + m.group(1), t)
    t, n3 = R_PAGE_Q.subn(lambda m: '/' + m.group(1) + '?' + m.group(2) + '=' + m.group(3), t)
    t, n4 = R_PAGE_Q2.subn(lambda m: '/' + m.group(1) + '?' + m.group(2) + '=' + m.group(3), t)
    # plain '?v=' only in html/css: in .js it can eat real code (e.g. '?v=function(')
    if not fn.endswith('.js'):
        t, n4b = R_PLAIN_V.subn('', t)
    t, n5 = R_LONE_Q.subn('', t)
    stats['asset_v'] += n1; stats['dup_ext'] += n2
    stats['page_q'] += n3 + n4; stats['lone_q'] += n5
    for rx in AD_SCRIPTS:
        t, n = rx.subn('', t)
        stats['ads'] += n
    t = rebrand(t)
    # forms -> clone API endpoints
    t = t.replace('https://taplai.8biz.net/gui-lien-he', '/api/contact')
    t = t.replace('https://taplai.8biz.net/dang-ky-tu-van', '/api/lead')
    t = t.replace('action="https://taplai.8biz.net/vao-phan-mem-thi-ly-thuyet-lai-xe-moi"',
                  'action="/api/exam-start"')
    return t

def text_pass():
    changed = 0
    for dirpath, dirnames, filenames in os.walk(ROOT):
        for fn in filenames:
            if os.path.splitext(fn)[1].lower() not in ('.html', '.css', '.js'):
                continue
            fp = os.path.join(dirpath, fn)
            try:
                t = open(fp, encoding='utf-8').read()
            except UnicodeDecodeError:
                continue
            nt = rewrite(t, fn)
            if nt != t:
                changed += 1
                if APPLY:
                    open(fp, 'w', encoding='utf-8').write(nt)
    return changed

rename_pass()
print(f"files to rename: {len(renamed)}")
for s, d in renamed[:8]:
    print("   ", os.path.basename(s), '->', os.path.basename(d))
print(f"text files changed: {text_pass()}")
print(dict(stats))
if not APPLY:
    print("DRY RUN — pass --apply to write")
