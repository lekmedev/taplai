#!/bin/bash
# Fetch N random exam variants per GPLX class -> __de-N.html
cd "$HOME/apps/taplai/www/taplaixe.vn" || exit 1
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36'
declare -A CNT=( [a1]=10 [a]=10 [b1]=12 [b]=20 [c1]=18 [c]=15 [d1]=14 [d2]=14 [d]=14 [be]=14 [c1e]=14 [ce]=14 [d1e]=14 [d2e]=14 [de]=14 )
for cls in a1 a b1 b c1 c d1 d2 d be c1e ce d1e d2e de; do
  n=${CNT[$cls]}
  for i in $(seq 1 "$n"); do
    out="thi-thu-ly-thuyet-hang-${cls}-de-chuan__de-${i}.html"
    if [ -s "$out" ] && [ "$(stat -c%s "$out")" -gt 50000 ]; then continue; fi
    curl -s --max-time 45 -A "$UA" -o "$out" "https://taplaixe.vn/thi-thu-ly-thuyet-hang-${cls}-de-chuan"
    sz=$(stat -c%s "$out" 2>/dev/null || echo 0)
    if [ "$sz" -lt 50000 ]; then echo "FAIL $out $sz"; sleep 2; fi
    sleep 0.3
  done
  echo "done class $cls ($n)"
done
echo ALLDONE
