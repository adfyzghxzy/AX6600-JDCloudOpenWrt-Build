# JDCloud AX6600 — hướng dẫn tiếp tục

- Thiết bị duy nhất: JDCloud RE-CS-02, qualcommax/ipq60xx, eMMC; U-Boot mod. Không có UART.
- Nền OpenWrt 25.12.6. Hai biến thể Standard/NSS, dùng APK.
- Đọc README.md và RELEASE-NOTES.md trước khi chỉnh. Xem docs/releases/r5.md cho trạng thái thực tế.
- Workflow chính: .github/workflows/nss-test.yml. Ghép config/common với config riêng từng biến thể; tên đầy đủ nằm trong README.
- scripts/stage-nss.py đưa phần cứng/NSS từ nguồn đã ghim vào nền stable. Không đổi nguồn/driver/kernel ngoài phạm vi yêu cầu.
- Gói dùng chung: config/jdcloud-re-cs-02-common.config; riêng Standard/NSS ở hai file tương ứng.
- R5 là firmware nguyên byte từ Test5 run 42321445516, commit 0ecd22c785da58faa1444502ba441fb66a1fe690. Tài liệu mới không thay firmware.
- Standard Test5 đã flash và xác nhận LED, modem USB Internet, apk update. RM502Q-AE dùng cdc_ether/usb0 + DHCP, USB 5 Gbps.
- Software Flow Offloading được bật thủ công khi thử, giảm CPU0 nhưng chưa chứng minh tăng thông lượng. Không nhầm với mặc định image.
- NSS trước Test5 đã offload WAN Ethernet; đường modem USB chưa được xác nhận. Không hứa QMI/QMAP hoặc QModem sẽ bật được NSS trên IPQ60xx.
- QModem, driver riêng hãng, XMM đang tạm dừng; chưa thêm nguồn hay xác nhận tương thích. Khi được yêu cầu, khóa phiên bản feed, kiểm tra Kconfig/phụ thuộc và build từng nhóm phù hợp. Dòng is not set không chứng minh build được.
- Không nạp nhiều driver cạnh tranh một thiết bị hoặc cho nhiều dịch vụ chiếm cùng cổng AT. Tránh ảnh hưởng SMS của LuCI+/NetGuardian nếu chúng được cài.
- Giữ kiểm tra image/FIT/F2FS/LED/APK trong workflow. Factory chưa kiểm chứng flash bằng U-Boot mod; nâng cấp thông thường dùng sysupgrade.
- Dùng cache khi phù hợp, không tự chọn build sạch. Tách kết quả build thành công với kiểm thử trên router.
- Nội dung README/Release viết ngắn, tiếng Việt dễ hiểu. Ghi đúng thay đổi và giới hạn đã biết.
