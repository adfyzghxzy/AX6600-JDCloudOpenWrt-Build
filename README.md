# OpenWrt cho JDCloud AX6600
Dành cho **RE-CS-02**, eMMC, nền **OpenWrt 25.12.6**.

## Tải firmware

[Tải R5 — Standard và NSS](https://github.com/adfyzghxzy/AX6600-JDCloudOpenWrt-Build/releases/tag/v25.12.6-jdcloud-r5)

| Bản | Nội dung |
|---|---|
| **Standard** | Không tăng tốc luồng NSS/ECM; phù hợp dùng modem USB |
| **NSS** | Thêm Qualcomm NSS/ECM; WWAN USB chưa được xác nhận offload |
| **R1 cũ** | Bản Standard nền ban đầu |

R5 có Argon, tiếng Việt, terminal web, LED Athena và bộ USB QMI/MBIM.
[Xem thay đổi và tình trạng kiểm tra](RELEASE-NOTES.md).

## Flash

Qua LuCI chọn file `*-sysupgrade.bin` đúng biến thể. Bỏ **Keep settings** để nhận toàn bộ mặc định mới.
LAN: `192.168.10.1`. WiFi: `JDCloud`, mật khẩu: `14789632`. Đổi mật khẩu sau khi cài.
Kiểm tra `SHA256SUMS`; không Force upgrade. Factory chưa được kiểm chứng flash qua U-Boot mod.

## Tự build

[Actions → Standard/NSS → Run workflow](https://github.com/adfyzghxzy/AX6600-JDCloudOpenWrt-Build/actions/workflows/nss-test.yml):
chọn `standard`, `nss` hoặc `both`. Để **Build sạch** tắt để dùng cache.

| File | Chỉnh gì? |
|---|---|
| [common.config](config/jdcloud-re-cs-02-common.config) | Package dùng chung |
| [standard.config](config/jdcloud-re-cs-02-standard.config) | Riêng Standard |
| [nss.config](config/jdcloud-re-cs-02-nss.config) | Riêng NSS |

`CONFIG_PACKAGE_ten-goi=y`: đưa vào firmware; `# CONFIG_PACKAGE_ten-goi is not set`: không chọn.
Gói ngoài feed cần tích hợp nguồn và kiểm tra phụ thuộc trước khi build.

## Tiếp tục với AI khác

Gửi link repo và yêu cầu đọc [AGENTS.md](AGENTS.md), config, workflow, ghi chú Release.
Không cần quay lại cuộc chat cũ. Nêu rõ package muốn thêm và biến thể cần build.
