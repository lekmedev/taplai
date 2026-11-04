#!/bin/bash
# Dựng lại taplai.8biz.net trên creek từ repo này.
#
# Nội dung mirror (425 MB) KHÔNG nằm trong git — nó là asset của GitHub Release "v1".
# Script này: tải + giải nén asset nếu thiếu www/ → áp overlay (theme/logo/font) → dựng container → verify.
#
#   bash scripts/deploy.sh            # dựng / cập nhật
#   SKIP_DOWNLOAD=1 bash scripts/deploy.sh   # chỉ áp overlay + restart (khi www/ đã có)
set -euo pipefail
cd "$(dirname "$0")/.."

REPO="lekmedev/taplai"
ASSET="taplai-site-content-v1.tar.gz"
SHA256="8a5e34efb2ff0a396ce191c7125c955180214f45661f23615a9eae60eda03e94"

if [ ! -d www/taplaixe.vn ]; then
  if [ "${SKIP_DOWNLOAD:-0}" = "1" ]; then
    echo "THIẾU www/taplaixe.vn và SKIP_DOWNLOAD=1 — dừng."
    exit 1
  fi
  echo "== tải nội dung từ GitHub Release v1 (~390 MB) =="
  mkdir -p www
  URL="https://github.com/$REPO/releases/download/v1/$ASSET"
  if command -v gh >/dev/null 2>&1; then
    gh release download v1 --repo "$REPO" --pattern "$ASSET" --dir /tmp --clobber
    mv "/tmp/$ASSET" /tmp/site.tar.gz
  else
    curl -L --fail -o /tmp/site.tar.gz "$URL"
  fi
  echo "== kiểm tra sha256 =="
  echo "$SHA256  /tmp/site.tar.gz" | sha256sum -c -
  echo "== giải nén =="
  tar -C www -xzf /tmp/site.tar.gz
  rm -f /tmp/site.tar.gz
fi

echo "== áp overlay (theme WEUP, logo, font, clone-exam-start.js) =="
cp -r overlay/assets/. www/taplaixe.vn/assets/
python3 scripts/inject_theme.py 2>/dev/null || true
python3 scripts/inject.py 2>/dev/null || true

echo "== nginx config check =="
docker run --rm -v "$PWD/conf/default.conf:/etc/nginx/conf.d/default.conf:ro" nginx:alpine nginx -t

echo "== up =="
docker compose up -d

echo "== verify =="
sleep 2
for p in / /bo-600-cau-hoi-ly-thuyet-thi-gplx "/thi-thu-ly-thuyet-hang-b-de-chuan?de=1" "/cau-hoi-ly-thuyet-moi?cau-hoi=1" /videos/1.mp4; do
  code=$(curl -s -o /dev/null -w '%{http_code}' "http://127.0.0.1:8090$p")
  printf '%-45s %s\n' "$p" "$code"
  [ "$code" = "200" ] || { echo "FAIL: $p"; exit 1; }
done
echo "OK — https://taplai.8biz.net"
