# taplai.8biz.net — static mirror của taplaixe.vn

> **Bàn giao / tiếp quản: đọc HANDOFF.md** (bản đồ repo, mapping URL, verify, TODO).
> Script tạo mirror nằm trong scripts/.

Bản clone tĩnh (nginx) của https://taplaixe.vn — luyện thi lý thuyết GPLX + 120 tình huống mô phỏng.
Thương hiệu đã đổi thành **Taplai.8biz.net**, đã bỏ AdSense/GA4/reCAPTCHA của chủ gốc.

## Thành phần

| Thứ | Đường dẫn |
|---|---|
| Nội dung web | `~/apps/taplai/www/taplaixe.vn/` (~420 MB, 301 trang HTML, 120 video, ~1150 fragment câu hỏi) |
| nginx config | `~/apps/taplai/conf/default.conf` |
| Compose | `~/apps/taplai/docker-compose.yml` (container `taplai`, nginx:alpine, host port **8090**) |
| Log form | `~/apps/taplai/logs/forms.log` (POST /api/contact, /api/lead — body được log lại) |
| Traefik | `~/apps/traefik/dynamic.yml` router `taplai-web` + `taplai-https` → `http://taplai:80` |
| Dashboard card | `~/apps/dashboard-homepage/config/services.yaml` → "Taplai (luyện thi GPLX)" |

## Cấu trúc mirror (quan trọng khi sửa)

- Trang thường: `bo-600-cau-hoi-ly-thuyet-thi-gplx.html`, phục vụ cả URL sạch nhờ `try_files $uri $uri.html`.
- Biến thể query → file `__key-value.html`, map trong nginx:
  - `?de=N` → `thi-thu-ly-thuyet-hang-<hạng>-de-chuan__de-N.html` (211 đề, 10–20 đề/hạng)
  - `?dethi=N` → `thi-thu-tinh-huong-mo-phong__dethi-N.html` (15 đề mô phỏng)
  - `?chuyenmuc=N` → `bai-viet__chuyenmuc-N.html`
  - `?hang=X` → `phan-mem-thi-ly-thuyet-lai-xe-de-chuan__hang-X.html`
  - `?cau-hoi=N` → `<endpoint>__cau-hoi-N.html` (fragment AJAX của trang ôn tập; dùng `map $args $qid`
    vì nginx KHÔNG đọc được `$arg_cau-hoi` — tên biến bị cắt ở dấu gạch ngang)
- Form thi (`#frmExam`, POST ở site gốc) được `assets/scripts/clone-exam-start.js` chặn submit và
  redirect sang `/thi-thu-ly-thuyet-hang-<hạng>-de-chuan?de=<random 1..N>`.

## Vận hành

```bash
ssh creek
cd ~/apps/taplai
docker compose restart          # sau khi sửa conf (bind-mount 1 file: sửa bằng sed -i sẽ KHÔNG ăn)
docker exec taplai nginx -t && docker exec taplai nginx -s reload
curl -s -o /dev/null -w '%{http_code}\n' https://taplai.8biz.net/
```

Sửa CSS/JS phải bump `?v=` trong HTML (Cloudflare cache asset 1h) — script mẫu: thêm/bớt
`?v=YYYYMMDDx` cho mọi ref `.css`/`.js`.

## Mirror lại / cập nhật nội dung

Site gốc là ASP.NET render server-side; đề thi random mỗi lần load. Quy trình cập nhật:
wget mirror → tải lại 211 biến thể đề → tải fragment `?cau-hoi=1..600` cho 3 bộ → normalize
(`?v=` chỉ trên `.html`/`.css`, KHÔNG trên `.js`) → audit file thiếu → rebrand → bump `?v=`.
Chi tiết + script: skill `static-site-clone-mirror`.

## Giới hạn đã biết

- Không có backend: form liên hệ/tư vấn chỉ trả success và ghi log, không gửi mail.
- Đề thi là bộ đã chụp sẵn (211 đề), không sinh đề mới mỗi lần vào như bản gốc.
- Nội dung (câu hỏi, video, bài viết) vẫn thuộc bản quyền chủ site gốc taplaixe.vn.

## Design system (WEUP)

Giao diện port sang ngôn ngữ thiết kế của https://weup.edu.vn/ — **không sửa main.css**,
toàn bộ override nằm ở `assets/styles/weup-theme.css` (nạp ngay sau main.css trong mọi trang).

Token đo trực tiếp từ weup.edu.vn (2026-11):

| Token | Giá trị | Dùng cho |
|---|---|---|
| navy | #00203F | header, hero, footer, heading trên nền sáng |
| navy tile | #06305A | card/tile trên nền tối |
| brand red | #990011 | CTA chính, accent, trạng thái active |
| red hover | #7A000E | hover CTA |
| red nhạt | #FF8A96 | chữ nhấn trên nền navy (7.3:1; #990011 trên navy chỉ 1.85:1) |
| surface | #FFFFFF / #F7F8FA / #EEF2F6 | nền trang, section xen kẽ |
| border | #CBD2D9 | viền card/input |
| text | #1F2933 · muted #52606D | body / phụ |
| warning | #F2B544 + #FDF3DC / #6B4E00 | "điểm liệt" |
| font | Fraunces (serif, 400) + Be Vietnam Pro (UI/body) | self-host ở assets/fonts/weup/ |
| CTA | pill 999px, weight 600, cao 46–56px, shadow 0 10px 30px rgba(153,0,17,.35) | mọi nút primary |
| card | radius 22px | card, qcard, panel |

Luật đã áp:
- Một CTA đỏ chính mỗi khung nhìn (CTA trong card hạng ở hero là secondary outline).
- Chữ trên nền tối không dùng đỏ đậm; #FF8A96 cho accent, trắng cho tiêu đề.
- "Đang xem" = navy/trắng, KHÔNG dùng đỏ (đỏ đã mang nghĩa "đã sai").
- Badge đếm câu là metadata (viền mảnh), không phải nút.

Sửa theme: edit `weup-theme.css` → scp → **bump ?v=N** trên mọi link weup-theme.css (Cloudflare cache 1h).

## Repo này chứa gì

Repo là **cấu hình + quy trình**, KHÔNG chứa nội dung mirror (425 MB, nội dung thuộc bản quyền taplaixe.vn).

| Có trong repo | Không có (sinh ra khi deploy) |
|---|---|
| `docker-compose.yml`, `conf/default.conf` | `www/taplaixe.vn/` — toàn bộ nội dung mirror |
| `scripts/` (mirror, normalize, theme, fetch) + `overlay/` (theme WEUP, logo, font, clone-exam-start.js) | `logs/`, `*.tgz` backup, `conf/*.bak.*` |
| `README.md`, `HANDOFF.md` | |

Dựng lại từ đầu: mirror nội dung theo `HANDOFF.md` §6–§7 → `bash scripts/deploy.sh`.
