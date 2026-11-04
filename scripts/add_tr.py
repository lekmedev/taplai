#!/usr/bin/env python3
import os, shutil, datetime, sys

P = os.path.expanduser("~/apps/traefik/dynamic.yml")
src = open(P, encoding='utf-8').read()

ROUTER_ANCHOR = """    mininote-https:
      rule: "Host(`p.8biz.net`)"
      entryPoints:
        - websecure
      service: mininote
      tls:
        certResolver: letsencrypt
"""

ROUTER_NEW = ROUTER_ANCHOR + """
    taplai-web:
      rule: "Host(`taplai.8biz.net`)"
      entryPoints:
        - web
      service: taplai-svc

    taplai-https:
      rule: "Host(`taplai.8biz.net`)"
      entryPoints:
        - websecure
      service: taplai-svc
      tls:
        certResolver: letsencrypt
"""

SVC_ANCHOR = """    dashauth-svc:
      loadBalancer:
        servers:
          - url: "http://host.docker.internal:2356"
"""

SVC_NEW = SVC_ANCHOR + """    taplai-svc:
      loadBalancer:
        servers:
          - url: "http://taplai:80"
"""

if 'taplai-svc' in src:
    print("already present")
    sys.exit(0)
if ROUTER_ANCHOR not in src:
    raise SystemExit("ROUTER ANCHOR NOT FOUND")
if SVC_ANCHOR not in src:
    raise SystemExit("SVC ANCHOR NOT FOUND")

bak = P + ".bak.taplai-" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
shutil.copy2(P, bak)

out = src.replace(ROUTER_ANCHOR, ROUTER_NEW, 1).replace(SVC_ANCHOR, SVC_NEW, 1)
open(P, 'w', encoding='utf-8').write(out)
print("backup:", bak)
print("taplai hits:", open(P, encoding='utf-8').read().count('taplai'))
