#!/bin/bash
# Mirror the learn-UI question fragment endpoints (AJAX partials).
cd "$HOME/apps/taplai/www/taplaixe.vn" || exit 1
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36'
for ep in cau-hoi-ly-thuyet-moi cau-hoi-ly-thuyet-a1-moi cau-hoi-ly-thuyet-b1; do
  for i in $(seq 1 600); do
    out="${ep}__cau-hoi-${i}.html"
    if [ -s "$out" ]; then continue; fi
    curl -s --max-time 30 -A "$UA" -o "$out" "https://taplaixe.vn/${ep}?cau-hoi=${i}"
    sz=$(stat -c%s "$out" 2>/dev/null || echo 0)
    if [ "$sz" -lt 50 ]; then echo "FAIL $ep $i ($sz)"; rm -f "$out"; fi
    sleep 0.15
  done
  echo "done $ep"
done
echo ALLDONE
