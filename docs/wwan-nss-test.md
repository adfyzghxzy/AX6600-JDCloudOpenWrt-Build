# Kiểm tra WWAN và NSS trên RE-CS-02

Các bản mới được xuất thành Actions artifact để thử nghiệm. Chỉ phát hành release sau khi chủ thiết bị xác nhận kiểm tra đạt.

## Tạo Interface modem USB 5G

Bản NSS test chọn sẵn hai nhóm:
- QMI gồm luci-proto-qmi, uqmi và driver QMI/WDM.
- MBIM gồm luci-proto-mbim, umbim và driver MBIM/WDM.

Trong LuCI, vào Mạng → Giao diện → Thêm giao diện, đặt tên wwan5g, chọn giao thức QMI hoặc MBIM theo chế độ thực tế của modem. Chọn cổng điều khiển tương ứng, thường là /dev/cdc-wdm0, nhập APN của SIM, bật DHCP/DNS theo cấu hình giao thức và gán vào vùng tường lửa wan. Lưu và áp dụng.

ModemManager là một phương thức khác. Bộ QMI/MBIM trên có thể hoạt động độc lập với ModemManager. Việc có đủ nhóm package xác nhận cấu hình phần mềm đã được chọn. Model modem, chế độ USB, nguồn điện, SIM và APN vẫn cần kiểm tra thực tế. PCIe/MHI và modem cần driver riêng có thể cần bổ sung.

## Thiết lập NSS lần đầu sau flash

Giữ Flow Offloading của firewall ở None. Bộ mặc định đã tắt Flow Offloading và Packet Steering.

Trong PuTTY, chạy:

```sh
uci set ecm.global.acceleration_engine='nss'
uci commit ecm
/etc/init.d/qca-nss-ecm enable
/etc/init.d/qca-nss-ecm start
```

Nếu có lỗi, gửi nguyên kết quả trước khi tiếp tục thay đổi. Service ECM của nguồn tham khảo cố ý không tự được bật bằng shebang thông thường, nên bước enable ở trên cần được thực hiện cho bản thử này.

## Xác minh

```sh
lsmod | grep -E 'qca_nss|ecm|ath11k'
cat /sys/module/ath11k/parameters/nss_offload
logread | grep -Ei 'nss|ecm|firmware.*fail' | tail -80
find /sys/kernel/debug/ecm -type f -name accelerated_count
```

Mở tải dữ liệu hoặc speed test từ PC/điện thoại phía LAN/Wi-Fi qua WAN, rồi đọc các bộ đếm:

```sh
for family in ipv4 ipv6; do
    counter="/sys/kernel/debug/ecm/ecm_nss_$family/accelerated_count"
    if [ -r "$counter" ]; then
        echo "$counter"
        cat "$counter"
    fi
done
nss_stats ipv4
```

Chụp kết quả trong lúc lưu lượng đang chạy. Kết nối có thể hết hạn sau khi dừng tải. Module đã nạp chưa đủ xác nhận offload; cần đối chiếu bộ đếm ECM và lưu lượng NSS khi thử. Đường WWAN USB cần kiểm tra riêng vì khả năng tăng tốc phụ thuộc driver và đường dữ liệu của modem.
