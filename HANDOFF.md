# HANDOFF — taplai.8biz.net (static mirror của taplaixe.vn)

> Cập nhật lần cuối: **2026-11-04 22:50** (sau khi tạo repo GitHub + Release v1).
> Mục đích: bàn giao cho AI/người khác tiếp quản mà không cần hỏi lại.
> Đọc hết file này trước khi sửa bất cứ thứ gì. Phần **§9 TODO** là việc còn lại.

---

## 1. TL;DR

- `https://taplai.8biz.net` = **static mirror** của `https://taplaixe.vn` (site luyện thi GPLX: 600 câu lý thuyết,
  15 hạng, 120 tình huống mô phỏng, 241 biển báo, bài viết).
- Chạy bằng **1 container nginx:alpine** serve thư mục tĩnh 425 MB, sau **Traefik** (host trên creek).
- **Không có backend.** Mọi tính năng tương tác (chấm điểm, tiến độ, lưu bài) chạy client-side bằng JS gốc của site.
- Đề thi "ngẫu nhiên" đã được **chụp sẵn thành 211 đề** (10–20 đề/hạng) và map qua query `?de=N`.
- Giao diện đã port sang **design system của weup.edu.vn** (navy + đỏ, serif Fraunces) bằng **1 file override**.
- Đã bóc sạch AdSense/GA4/reCAPTCHA của chủ gốc; không còn quảng cáo.
- **Repo GitHub**: https://github.com/lekmedev/taplai (public, `main`) — 41 file, ~800 KB.
  Nội dung mirror (425 MB) nằm ở **Release `v1`** (asset 390 MB), KHÔNG nằm trong git.

---

## 2. Địa chỉ & vận hành

| Thứ | Giá trị |
|---|---|
| Public URL | https://taplai.8biz.net (Cloudflare proxy → Traefik creek :443) |
| Tailnet | http://100.95.76.53:8090 |
| Container | `taplai` (nginx:alpine), `restart: unless-stopped` |
| Port | host `0.0.0.0:8090` → container `80` |
| Repo GitHub | https://github.com/lekmedev/taplai (branch `main`, push bằng SSH account `lekmedev`) |
| Release nội dung | https://github.com/lekmedev/taplai/releases/tag/v1 — asset `taplai-site-content-v1.tar.gz` (390,213,148 bytes) |
| sha256 asset | `8a5e34efb2ff0a396ce191c7125c955180214f45661f23615a9eae60eda03e94` |
| Compose | `~/apps/taplai/docker-compose.yml` |
| Log | `docker logs taplai`; form POST → `~/apps/taplai/logs/forms.log` |
| Dashboard card | dashboard.8biz.net → group "Public services" → "Taplai (luyện thi GPLX)" |
| Traefik | `~/apps/traefik/dynamic.yml` router `taplai-web` + `taplai-https`, service `taplai-svc` |

Lệnh thường dùng:

```bash
ssh creek
cd ~/apps/taplai
docker compose restart                 # sau khi sửa conf/default.conf (reload không đủ, xem §4 bẫy 2)
docker exec taplai nginx -t && docker exec taplai nginx -s reload
curl -s -o /dev/null -w '%{http_code}\n' https://taplai.8biz.net/
git push                               # đẩy thay đổi repo (SSH, account lekmedev)
```

---

## 3. Bản đồ repo

### Trên GitHub (`lekmedev/taplai` — những gì AI khác clone được)

```
taplai/                       # clone về chỉ có phần này (~800 KB)
├── docker-compose.yml        # 1 service nginx, mount 3 volume (xem §4)
├── README.md                 # cách dựng nhanh + BẢNG DESIGN TOKEN (§ "Design system (WEUP)")
├── HANDOFF.md                # file này
├── .gitignore                # ignore www/, logs/, *.tgz, conf/*.bak.*, services.yaml.bak.*
├── conf/
│   └── default.conf          # toàn bộ routing nginx (28 location) — nguồn sự thật của URL mapping
├── scripts/                  # pipeline mirror + deploy (xem §7)
│   └── deploy.sh             # ★ 1 lệnh dựng lại: tải Release v1 → sha256 → giải nén → overlay → up → verify
└── overlay/                  # phần "của mình" áp lên nội dung mirror sau khi giải nén
    └── assets/
        ├── styles/weup-theme.css   # ★ NGUỒN SỰ THẬT của design WEUP (bản chạy ở www/ là bản copy)
        ├── scripts/clone-exam-start.js
        ├── images/logo.png, logo-square.png
        └── fonts/weup/*.woff2 (21 file Fraunces + Be Vietnam Pro)
```

### Trên creek (`~/apps/taplai/`) — ngoài nội dung git còn có

```
~/apps/taplai/
├── (toàn bộ các file git ở trên)
├── www/taplaixe.vn/          # WEB ROOT 425 MB (mount read-only vào container) — nội dung = Release v1 + overlay
│   ├── index.html, <42 trang cấp 1>, bai-viet/ luyen-thi/ (24 trang con)
│   ├── *__de-<n>.html        # 211 đề thi            ← map ?de=N
│   ├── *__dethi-<n>.html     # 15 đề mô phỏng        ← map ?dethi=N
│   ├── *__cau-hoi-<n>.html   # 1150 fragment AJAX    ← map ?cau-hoi=N
│   ├── *__chuyenmuc-<n>.html # 3 chuyên mục bài viết ← map ?chuyenmuc=N
│   ├── *__hang-<X>.html      # 7 trang "đề chuẩn"    ← map ?hang=X
│   ├── assets/styles/main.css        # CSS gốc của site (KHÔNG SỬA)
│   ├── assets/styles/weup-theme.css  # bản copy của overlay — SỬA Ở REPO RỒI COPY SANG
│   ├── assets/scripts/               # JS gốc + clone-exam-start.js
│   ├── assets/fonts/, images/, libs/ # font gốc + weup, ảnh 600cau/*.webp, videojs
│   ├── videos/ (120 mp4, ~300 MB)
│   └── uploads/ (ảnh bài viết)
├── logs/                     # access.log, error.log, forms.log (mount vào /var/log/nginx)
├── conf/default.conf.bak.*   # backup trước các lần sửa conf
├── www-html-backup-20261104-210036.tgz   # backup HTML TRƯỚC khi normalize (5 MB) — P3: có thể xoá
└── mockup/                   # ⚠ file lạ xuất hiện 2026-11-04 22:35 (bien-bao.html + assets), KHÔNG phải của pipeline
                              #   — chưa commit, chưa rõ ai tạo; hỏi Marshal trước khi xoá/commit
```

**Số liệu nội dung**: 2300 file, 425 MB — 1451 HTML (66 trang thật + 211 đề + 15 đề mô phỏng + 1150 fragment
+ 9 biến thể query), 120 video, 659 ảnh. Không có file nào >20 MB.

---

## 4. Cách nginx phục vụ (đọc `conf/default.conf` là hiểu hết)

```nginx
location / { try_files $uri $uri.html $uri/index.html =404; }   # URL sạch: /bo-600-... → .html
```

Các nhóm map đặc biệt (đều dùng `try_files <file biến thể> <file gốc>`):

| Query | File |
|---|---|
| `?de=N` | `thi-thu-ly-thuyet-hang-<hạng>-de-chuan__de-N.html` (15 location, 1/hạng) |
| `?dethi=N` | `thi-thu-tinh-huong-mo-phong__dethi-N.html` |
| `?chuyenmuc=N` | `bai-viet__chuyenmuc-N.html` |
| `?hang=X` | `phan-mem-thi-ly-thuyet-lai-xe-de-chuan__hang-X.html` |
| `?cau-hoi=N` | `<endpoint>__cau-hoi-N.html` cho 3 endpoint ôn tập |

**Bẫy số 1**: query param có **dấu gạch ngang** (`cau-hoi`) thì nginx **không** đọc được qua `$arg_`.
Đã xử lý bằng map regex ở http context:

```nginx
map $args $qid { default ""; ~(?:^|&)cau-hoi=(\d+) $1; }
```

**Bẫy số 2**: `conf/default.conf` bind-mount dạng **1 file** → `sed -i` tạo inode mới, container vẫn đọc bản cũ.
Sửa bằng Python `open(p,'w')` (truncate cùng inode) hoặc `docker restart taplai`.

Form POST (site gốc cần server) được thay bằng stub:

| Endpoint | Hành vi |
|---|---|
| `/api/contact`, `/api/lead` | trả `{"success":true}` + ghi body vào `logs/forms.log` |
| `/api/exam-start` | trang HTML nhắc chọn lại hạng/đề (fallback) |

Nút "Bắt đầu thi" (`#frmExam` POST) được `assets/scripts/clone-exam-start.js` chặn submit và redirect
sang `/thi-thu-ly-thuyet-hang-<hạng>-de-chuan?de=<random 1..N>` (N lấy từ `document.CLASS_LIST`).

---

## 5. Design system WEUP

Nguồn: đo trực tiếp từ https://weup.edu.vn (computed styles + CSS bundle). Bảng token đầy đủ ở
`README.md` § "Design system (WEUP)". Tóm tắt:

- Navy `#00203F` · tile `#06305A` · brand red `#990011` (hover `#7A000E`) · đỏ nhạt `#FF8A96` cho chữ trên nền tối
- Surface `#FFFFFF/#F7F8FA/#EEF2F6` · border `#CBD2D9` · text `#1F2933` · muted `#52606D` · warning `#F2B544`
- Font: **Fraunces** (serif heading 400) + **Be Vietnam Pro** (UI/body), self-host ở `overlay/assets/fonts/weup/`
- CTA pill `999px` + shadow `0 10px 30px rgba(153,0,17,.35)`; card radius `22px`

**Quy trình sửa theme (đúng thứ tự)**

1. Sửa **`overlay/assets/styles/weup-theme.css` TRONG REPO** (nguồn sự thật) → copy sang
   `www/taplaixe.vn/assets/styles/weup-theme.css` → **bump `?v=N`** trên mọi `<link ... weup-theme.css>`
   (301 trang) → commit + push. Cloudflare cache asset 1 giờ; hiện tại `?v=13`.
2. Không sửa `main.css` (rollback = xoá 1 dòng `<link>`).
3. Đừng dùng đỏ `#990011` làm màu chữ trên nền navy (1.85:1). Dùng `#FF8A96` (7.3:1).
4. Trạng thái "đang xem" = navy/trắng, **không** dùng đỏ (đỏ đã mang nghĩa "đã sai").

---

## 6. Dựng lại từ đầu (đã test 2026-11-04)

```bash
git clone git@github.com:lekmedev/taplai.git && cd taplai
bash scripts/deploy.sh
# → tải Release v1 (390 MB, ~14s @26MB/s) → verify sha256 → giải nén www/ (424 MB)
# → áp overlay/ (theme WEUP, logo, font, clone-exam-start.js) → docker compose up → curl verify 5 URL
```

Nếu máy đã có `www/` (máy đang chạy): `SKIP_DOWNLOAD=1 bash scripts/deploy.sh` — chỉ áp overlay + restart.

Đã verify round-trip: clone 41 file → tải 372 MiB/14s → sha256 OK → giải nén 424 MB / 1451 HTML / 120 video
→ overlay áp thành công (weup-theme.css có mặt).

---

## 7. Data inventory — cái gì lấy từ đâu

| Dữ liệu | Số lượng | Nguồn / cách lấy |
|---|---|---|
| Trang HTML | 66 | `wget --mirror --page-requisites --convert-links --adjust-extension` |
| Đề thi | 211 (10–20/hạng) | fetch cùng URL `/thi-thu-ly-thuyet-hang-<hạng>-de-chuan` N lần — **mỗi lần trả 1 bộ 30 câu ngẫu nhiên** |
| Đề mô phỏng | 15 | `/thi-thu-tinh-huong-mo-phong?dethi=N` |
| Fragment câu hỏi | 1150 | `/cau-hoi-ly-thuyet-moi|a1-moi|b1?cau-hoi=1..600` (id không thuộc bộ → origin trả rỗng) |
| Video | 120 | `/videos/1..120.mp4` (~2.4 MB/file) |
| Ảnh câu hỏi | 562 webp | `/assets/images/600cau/*.webp` |

Số đề/hạng lấy từ `document.CLASS_LIST` trong HTML: A1 10, A 10, B1 12, B 20, C1 18, C 15, D1/D2/D/BE/C1E/CE/D1E/D2E/DE 14.

---

## 8. Script trong `scripts/`

| File | Việc |
|---|---|
| **`deploy.sh`** | **1 lệnh dựng lại**: tải Release v1 + sha256 + giải nén + áp overlay + compose up + verify (`SKIP_DOWNLOAD=1` = bỏ bước tải) |
| `audit_mirror.py` | quét cả cây, liệt kê ref nội bộ trỏ tới file không tồn tại |
| `fetch_missing.py` | tải nốt các file còn thiếu (ảnh/font/video) từ origin |
| `fetch_de.sh` | tải 211 đề thi (chạy nền bằng `setsid nohup`) |
| `fetch_frag.sh` | tải 1800 fragment `?cau-hoi=1..600` cho 3 bộ |
| `norm.py` | chuẩn hoá: rename file có query, rewrite refs, rebrand domain, bỏ ads/GA/reCAPTCHA, trỏ form về `/api/*` (dry-run mặc định, `--apply` để ghi) |
| `restore_assets.py` | tải lại toàn bộ .js/.css/font từ origin (dùng khi asset bị hỏng) |
| `inject.py` | chèn `clone-exam-start.js` vào các trang có `#frmExam` |
| `inject_theme.py` | chèn `<link weup-theme.css>` sau `main.css` |
| `bust.py` | thêm `?v=` vào mọi ref css/js trong HTML |
| `add_tr.py` | thêm router + service Traefik cho `taplai.8biz.net` (idempotent, tự backup) |

Lưu ý: `inject_theme.py` / `inject.py` ghi trực tiếp vào `www/` (hardcode `~/apps/taplai/www/taplaixe.vn`) —
chúng phục vụ pipeline trên creek; `deploy.sh` gọi lại chúng sau khi giải nén.

---

## 9. Verify (làm sau MỌI thay đổi)

```bash
# 1. HTTP
for p in / /bo-600-cau-hoi-ly-thuyet-thi-gplx '/thi-thu-ly-thuyet-hang-b-de-chuan?de=12' \
         '/cau-hoi-ly-thuyet-moi?cau-hoi=227' /videos/60.mp4; do
  printf '%-45s ' "$p"; curl -s -o /dev/null -w '%{http_code}\n' "https://taplai.8biz.net$p"; done

# 2. Không còn brand cũ / quảng cáo
curl -s https://taplai.8biz.net/ | grep -c 'taplaixe\|adsbygoogle'   # phải = 0

# 3. Browser thật (browser_exec): hook window.onerror, rồi
#    - trang ôn tập: click .question[data-question="227"] → card hiện câu + ảnh
#    - thi thử: click #btnStartExam → scrollIntoView('#question0') → click .opt (progress 1/30)
#      → #btnSubmit → dialog xác nhận → nút "Nộp bài" trong dialog → đọc điểm
#    - mô phỏng: video readyState 4 + sitGrid có 120 nút
```

**Bẫy khi test**: `click_at_xy` với toạ độ phần tử ngoài viewport sẽ bấm vào khoảng không →
luôn `scrollIntoView({block:'center'})` rồi lấy lại `getBoundingClientRect()`.
Và `Emulation.setDeviceMetricsOverride` còn hiệu lực cho mọi screenshot sau đó — nhớ set lại 1440x900 / 390x844.

---

## 10. TODO (việc còn lại, xếp theo giá trị)

### P1 — nên làm
1. **Cron re-mirror** (nếu Marshal muốn nội dung tươi): script chạy `fetch_de.sh` + `fetch_frag.sh` +
   `fetch_missing.py` rồi reload; đề mới = chạy lại `fetch_de.sh` (nó bỏ qua file đã có, muốn đề mới
   thì xoá `*__de-*.html` của hạng đó trước) → đóng gói lại tarball → tạo Release mới (v2).
   Chưa đặt lịch — **hỏi Marshal tần suất**.
2. **Form liên hệ/tư vấn thật**: hiện chỉ log body. Nếu cần nhận mail → thêm endpoint nhỏ (FastAPI/Node)
   hoặc đẩy vào Google Apps Script / Telegram bot. Log hiện tại ở `logs/forms.log` (format `body="..."`).

### P2 — tuỳ nhu cầu
3. **Search bài viết**: form `post-search-bar` (GET `bai-viet.html`) là server-side ở site gốc → trên mirror
   không lọc được. Muốn có thì viết JS filter client-side trên danh sách bài viết.
4. **Đề mới mỗi lần vào**: hiện đề cố định 1..N. Muốn "random như gốc" thì phải có backend sinh đề
   (hoặc JS tự trộn câu từ 600 câu đã có trong `bo-600-...html`).
5. **Logo/bộ nhận diện riêng**: hiện là wordmark chữ trắng "TAPLAI.8BIZ.NET" (vẽ bằng canvas) + icon vô lăng trắng.
   Muốn đổi thì thay `overlay/assets/images/logo.png` (876×152) và `logo-square.png` (48×48) trong repo
   → copy sang `www/` + bump `?v=` ảnh (logo đang là `?v=3`).
6. **Quảng cáo**: đã bỏ hết ads của chủ gốc. Nếu Marshal muốn gắn AdSense account riêng → thêm slot
   vào các vị trí cũ (đầu trang, giữa danh sách câu, cuối bài viết) + script trong `</head>`.

### P3 — dọn dẹp
7. `logs/` đang ~632 KB (access log của quét thử) — có thể truncate.
8. Xoá `www-html-backup-20261104-210036.tgz` (5 MB) sau khi đã ổn định.
9. `mockup/` trong `~/apps/taplai/` — file lạ (bien-bao.html, 2026-11-04 22:35, không do pipeline tạo).
   Hỏi Marshal: giữ, commit hay xoá?

---

## 11. Decision log (tại sao làm thế này)

| Quyết định | Lý do |
|---|---|
| Mirror tĩnh thay vì rebuild | Site gốc render server-side, nội dung nằm trong HTML; mirror giữ nguyên 100% tính năng chấm điểm client-side |
| Chụp sẵn N đề thay vì backend | Đề random mỗi lần load → fetch N lần là cách duy nhất không cần server |
| nginx + `try_files` thay vì app | Không có logic server nào cần; nginx:alpine nhẹ, 425 MB tĩnh |
| 1 file `weup-theme.css` thay vì sửa `main.css` | Rollback 1 dòng; update từ nguồn gốc không conflict |
| Bỏ AdSense/GA/reCAPTCHA | ID của chủ gốc, domain mình không chạy được, và reCAPTCHA sẽ chặn form |
| Đổi brand sang Taplai (theo yêu cầu Marshal) | Tránh trùng nhận diện với site gốc |
| Font self-host | Không phụ thuộc fonts.googleapis, tải nhanh, chủ động subset tiếng Việt |
| **Nội dung qua Release asset, không commit git** | Repo nhẹ (~800 KB, clone nhanh); 425 MB vào git làm mọi clone/pull nặng vĩnh viễn và rất khó gỡ; nội dung là bản quyền taplaixe.vn nhưng Marshal muốn repo tự chứa đủ để dựng lại → Release là điểm giữa, `deploy.sh` tự tải |
| Overlay/ trong repo thay vì chỉ sửa trong www/ | Repo tự chứa phần "của mình" — www/ có thể xoá và dựng lại 100% từ Release + overlay |

---

## 12. Checklist cho AI tiếp quản

- [ ] Đọc §1–§5; mở `conf/default.conf` và `overlay/assets/styles/weup-theme.css`.
- [ ] Baseline: chạy `bash scripts/deploy.sh` (SKIP_DOWNLOAD=1 nếu www/ đã có) + §9 verify.
- [ ] Sửa theme → sửa ở `overlay/` trong repo → copy sang `www/` → bump `?v=` → commit + push.
- [ ] Sửa conf → nhớ `docker restart taplai` (reload không đủ vì bind-mount 1 file).
- [ ] Commit nội dung www/ vào git? **KHÔNG** — nội dung đi qua Release.
- [ ] Không sửa `main.css`.
- [ ] Hỏi Marshal trước khi: đặt cron re-mirror, thêm quảng cáo, đổi logo/nhận diện, xoá backup, xử lý `mockup/`.
