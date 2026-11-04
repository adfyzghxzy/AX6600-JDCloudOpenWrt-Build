# OpenWrt cho JDCloud AX6600 (RE-CS-02)

Nhánh `main` build firmware eMMC cho JDCloud RE-CS-02 (`qualcommax/ipq60xx`). Mã nguồn nền được ghim ở tag OpenWrt `v25.12.6`. Bản vá trong `patches/re-cs-02.patch` chuyển phần hỗ trợ thiết bị từ upstream và cấu hình gói `sysupgrade` cho `0:HLOS` và `rootfs`.

## Build và kiểm tra

Mở tab **Actions**, chọn workflow **Build OpenWrt 25.12.6 for JDCloud RE-CS-02** và chọn nhánh `main`. Workflow kiểm tra kernel FIT nằm trong giới hạn 6 MiB, rootfs SquashFS có LuCI, metadata đúng model và DTB khai báo các cổng Ethernet.

Khi workflow thành công, tải artifact `re-cs-02-openwrt-25.12.6-sysupgrade-candidate` và đối chiếu file `.bin` với `SHA256SUMS`. Đây là firmware thử nghiệm cho RE-CS-02. Trước khi flash qua LuCI, chạy `sysupgrade -T /tmp/<tên-file-sysupgrade.bin>` trên firmware hiện tại. Dừng nếu kiểm tra thất bại hoặc LuCI yêu cầu **Force upgrade**.
