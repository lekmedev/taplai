#!/bin/bash
# Dựng lại taplai.8biz.net từ repo này trên creek.
# Repo KHÔNG chứa nội dung mirror (www/) — phải mirror trước, xem HANDOFF.md §6–§7.
# Script này áp overlay/ (theme WEUP, logo, font, clone-exam-start.js) lên nội dung đã mirror
# rồi dựng container và verify.
set -euo pipefail
cd "$(dirname "$0")/.."

if [ ! -d www/taplaixe.vn ]; then
  echo "THIẾU www/taplaixe.vn — mirror nội dung trước (HANDOFF.md §6–§7: wget → fetch_de.sh → fetch_frag.sh → fetch_missing.py → norm.py --apply → inject.py)"
  exit 1
fi

echo "== áp overlay (theme/logo/font/script) =="
cp -r overlay/assets/. www/taplaixe.vn/assets/
# chèn link theme + script exam-start nếu chưa có
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
