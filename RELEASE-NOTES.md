Bản phát hành thử nghiệm đầu tiên cho JDCloud AX6600 RE-CS-02, nền OpenWrt 25.12.6.

Mặc định sau khi flash sạch hoặc reset:
- IP LAN 192.168.10.1.
- Cả ba điểm phát Wi-Fi bật, SSID JDCloud, WPA2-PSK, mật khẩu 14789632.
- radio0 kênh Auto, radio1 kênh 1, radio2 kênh 36.

File sysupgrade.bin dùng cho nâng cấp qua LuCI hoặc sysupgrade. Bỏ chọn Keep settings để áp dụng đầy đủ cấu hình mặc định mới. Kiểm tra SHA256SUMS và sysupgrade -T trước khi flash.

File factory.bin có bố trí kernel FIT ở đầu, rootfs tại offset 6 MiB và metadata OpenWrt, theo công thức image của LiBwrt dành cho RE-CS-02. Chưa kiểm chứng file factory trên U-Boot mod của thiết bị. Cần đối chiếu loại image và vùng ghi mà U-Boot mod nhận trước khi sử dụng factory.

Bản nền đã được thử trên RE-CS-02: khởi động, overlay F2FS lưu dữ liệu qua reboot, ba radio Wi-Fi, LAN và Internet qua WAN DHCP, cài nano từ kho APK chính thức. Cấu hình mặc định mới trong release này cần được xác nhận sau flash.

Đây là biến thể Standard, chưa tích hợp tăng tốc luồng NSS/ECM. Driver Ethernet kmod-qca-nss-dp vẫn phục vụ phần cứng mạng. Biến thể NSS sẽ được phát hành riêng sau khi được build và kiểm chứng.

Đối chiếu từng file với SHA256SUMS trong release.
